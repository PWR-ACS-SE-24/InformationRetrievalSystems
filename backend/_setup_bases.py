import argparse
import json
import time
import typing as t
from datetime import datetime
from itertools import batched
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty, Full
from threading import Thread

from elasticsearch import helpers
from pylatexenc.latex2text import LatexNodes2Text
from sqlmodel import Session, SQLModel, col, func
from tqdm import tqdm

from arxivsearch.database import ArxivCategoriesModel, ArxivPaperModel, setup_database
from arxivsearch.elastic import setup_elastic
from arxivsearch.logger import setup_logger

INDEXNAME = "arxiv"

index_mapping = {
    "properties": {
        "id": {"type": "keyword"},
        "submitter": {"type": "keyword"},
        "authors": {"type": "keyword"},
        "title": {"type": "text"},
        "comments": {"type": "text"},
        "journal-ref": {"type": "text"},
        "doi": {"type": "keyword"},
        "categories": {"type": "keyword"},
        "abstract": {"type": "text"},
        "update_date": {"type": "date", "format": "yyyy-MM-dd"},
    }
}


def do_elastic_fixes(line: dict) -> dict:
    # to be inserted elastic required weird ass format
    return {"_id": line["id"], "_index": INDEXNAME, "_source": line}


def do_postgres_fixes(line: dict) -> dict:
    # we want to parse date it from YYYY-mm-dd to date
    line["update_date"] = datetime.strptime(line["update_date"], "%Y-%m-%d")
    line["arxiv_id"] = line.pop("id")

    # we update in place, so we need to be careful not to overwrite the data
    # before its inserted into elastic
    return line


def try_and_put(queue: Queue, data: t.Any):
    while True:
        try:
            queue.put(data, timeout=1)
            break
        except Full:
            time.sleep(0.1)
            continue


class Reader(Process):
    def __init__(self, path: Path, reader_queue: Queue, num_processors: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.reader_queue = reader_queue
        self.num_processors = num_processors

    def run(self):
        with open(self.path, "r") as file:
            length = sum(1 for _ in file)
            file.seek(0)
            for line in tqdm(file, total=length):
                data = json.loads(line)

                if data["submitter"] is None:
                    continue

                try_and_put(self.reader_queue, data)

        # reader has finished, waiting for queue to be empty before closing
        while not self.reader_queue.empty():
            time.sleep(0.1)

        # send None to all processors
        for _ in range(self.num_processors):
            try_and_put(self.reader_queue, None)


class Processor(Process):
    def __init__(self, reader_queue: Queue, writer_queue: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reader_queue = reader_queue
        self.writer_queue = writer_queue
        self.latex_context = LatexNodes2Text()

    def fix_text(self, content: str) -> str:
        content = str(self.latex_context.latex_to_text(content))
        return content.replace("\n", " ")

    def process(self, parsed_line: dict) -> dict:

        try:
            # id is ok
            # submitter is being check in a producer
            # authors are fucked up, but lets try and fix them
            authors = set()
            for author in parsed_line["authors_parsed"]:
                full_name = " ".join(author).replace("\n", "")
                full_name, *_ = full_name.split("  ")  # two spaces
                authors.add(full_name.strip())

            # THIS MAY BE WRONG, but lets assume that submitter is also an author
            authors.add(parsed_line["submitter"])
            parsed_line["authors"] = list(authors)

            # title could be fucked up
            parsed_line["title"] = self.fix_text(parsed_line["title"])

            # we dont care about comments, but we defuck them anyway
            if parsed_line["comments"] is None:
                parsed_line["comments"] = ""
            else:
                parsed_line["comments"] = self.fix_text(parsed_line["comments"])

            # journal-ref is nullable for some reason
            # doi is ok, yet sometimes nullable

            # categories are saved like this: <major category>.<sub category>; we want to save both major as itself
            # and major + minor as second category, we are lucky that all arxiv categories are at most two elements.
            # but some articles already have major and minor categories set properly
            parsed_categories = set()
            categories: t.List[str] = parsed_line["categories"].split(" ")

            for category in categories:
                if "." in category:
                    major, _ = category.split(".")
                    parsed_categories.add(major)
                    parsed_categories.add(category)
                else:
                    parsed_categories.add(category)

            parsed_line["categories"] = list(parsed_categories)

            # abstract is fucked up for sure
            parsed_line["abstract"] = self.fix_text(parsed_line["abstract"])

            # update_date is ok
            return parsed_line

        except Exception:
            # line is fucked up, we dont care
            return {}

    def run(self):
        while True:
            try:
                line = self.reader_queue.get(timeout=1)
                if line is None:
                    try_and_put(self.writer_queue, None)
                    break
            except Empty:
                # case: empty but not closed, wait for the data
                continue

            data = self.process(line)

            if data:
                try_and_put(self.writer_queue, data)


class Writer(Process):
    def __init__(self, path: Path, writer_queue: Queue, no_processors: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.writer_queue = writer_queue
        self.no_processors = no_processors
        self.nones = 0

    def run(self):
        with open(self.path, "w") as file:
            while True:
                try:
                    line = self.writer_queue.get(timeout=1)
                    if line is None:
                        self.nones += 1
                        if self.nones == self.no_processors:
                            break
                        continue

                except Empty:
                    # case: empty but not closed, wait for the data
                    continue

                except ValueError:
                    # case: queue closed *should never happen*
                    break

                file.write(json.dumps(line) + "\n")


def setup_bases(path_to_dump: Path, force: bool = False):
    engine = setup_database()
    elastic = setup_elastic()

    logger = setup_logger()
    logger.setLevel("DEBUG")

    logger.info("Setting up bases...")

    logger.info("Checking whether data already exists in both databases")
    postgres_amount = 0
    try:
        elastic_amount = int(elastic.cat.count(index="arxiv", format="json")[0]["count"])
        with Session(engine) as session:
            postgres_amount: int = session.exec(func.count(col(ArxivPaperModel.id))).first()[0]

        logger.debug(f"Postgres amount: {postgres_amount}")
        logger.debug(f"Elastic amount: {elastic_amount}")

        if elastic_amount == postgres_amount and postgres_amount > 0 and force == 0:
            logger.info("Data already exists in both databases, skipping setup")
            return

    except Exception as e:
        logger.error(f"Error while checking elasticsearch: {e}")

    logger.debug("Clearing existing data in elasticsearch")
    if elastic.indices.exists(index="arxiv"):
        elastic.indices.delete(index="arxiv")

    elastic.indices.create(index="arxiv", mappings=index_mapping)

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    logger.info("Starting to parse lines")
    result_path = path_to_dump.with_name("arxiv-processed.jsonl")

    if force == 1:
        if not result_path.exists():
            logger.error("File does not exist, cannot delete")
            return

    else:
        reader_queue = Queue(maxsize=1000)
        writer_queue = Queue(maxsize=1000)

        no_processors = 12

        reader = Reader(path_to_dump, reader_queue, no_processors)
        processors = [Processor(reader_queue, writer_queue) for _ in range(no_processors)]
        writer = Writer(result_path, writer_queue, no_processors)

        reader.start()
        [processor.start() for processor in processors]
        writer.start()

        reader.join()
        [processor.join() for processor in processors]
        writer.join()

        reader_queue.close()
        writer_queue.close()

        logger.info("Finished preprocessing lines")

    def insert_into_elastic(path_to_dump: Path, parts: int = 25, pos: int = 0):
        with open(path_to_dump, "r") as file:
            length = sum(1 for _ in file)
            file.seek(0)
            for i, batch in tqdm(enumerate(batched(file, (length // parts) + 1)), total=parts, position=pos):
                batch = [do_elastic_fixes(json.loads(line)) for line in batch]
                for ok, _ in helpers.parallel_bulk(elastic, batch):
                    if not ok:
                        logger.error("Error while inserting into elastic")
                        continue

                logger.debug(f"Inserted {(i + 1)/ parts * 100:.2f}% of data into elastic")

    def insert_into_postgres(path_to_dump: Path, parts: int = 25, pos: int = 1):
        with open(path_to_dump, "r") as file:
            length = sum(1 for _ in file)
            file.seek(0)
            for i, batch in tqdm(enumerate(batched(file, (length // parts) + 1)), total=parts, position=pos):
                with Session(engine) as session:
                    for entry in batch:
                        session.add(ArxivPaperModel(**do_postgres_fixes(json.loads(entry))))
                    session.commit()

                logger.debug(f"Inserted {(i + 1)/ parts * 100:.2f}% of data into postgres")

    t1 = Thread(target=insert_into_elastic, args=(result_path,))
    t2 = Thread(target=insert_into_postgres, args=(result_path,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    logger.info("Finished inserting data into both databases")
    logger.info("Have a nice day! :)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup bases")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("arxiv-metadata-oai-snapshot.json"),
        help="Path to the dump file",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="count",
        default=0,
        help="How foreceful should the setup be?"
        + "\n\t0: exit if data exists"
        + "\n\t1: delete data and use partially processed data"
        + "\n\t2: delete data and create new data from dump",
    )
    args = parser.parse_args()

    setup_bases(args.path, force=args.force)
