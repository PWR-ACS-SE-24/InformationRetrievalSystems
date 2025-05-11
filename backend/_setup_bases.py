import argparse
import json
import re
import typing as t
from datetime import datetime
from itertools import batched
from pathlib import Path

from elasticsearch import helpers
from sqlmodel import Session, SQLModel, col, func, select

from arxivsearch.database import ArxivCategoriesModel, ArxivPaperModel, setup_database
from arxivsearch.elastic import setup_elastic
from arxivsearch.logger import setup_logger

INDEXNAME = "arxiv"

index_mapping = {
    "properties": {
        "id": {"type": "keyword"},
        "submitter": {"type": "text"},
        "authors": {"type": "text"},
        "title": {"type": "text"},
        "comments": {"type": "text"},
        "journal-ref": {"type": "text"},
        "doi": {"type": "keyword"},
        # in elastic every field is an array
        "categories": {"type": "keyword"},
        "abstract": {"type": "text"},
        "update_date": {"type": "date", "format": "yyyy-MM-dd"},
    }
}

TEXT_DEFUCKER_3000 = re.compile(r"\\\\.")


def fix_text(line: str) -> str:
    line = line.replace("\n", " ")
    return TEXT_DEFUCKER_3000.sub("", line)


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


def parse_lines(file: Path, parts: int = 25):
    with open(file, "r") as f:
        length = sum(1 for _ in f)
        f.seek(0)

        for batched_lines in batched(f, (length // parts) + 1):
            lines = []

            for line in batched_lines:
                # do fixes that are common between both databases
                parsed_line = json.loads(line)

                # id is ok

                # submitter is empty sometimes?
                if parsed_line["submitter"] is None:
                    continue

                # authors are fucked up
                parsed_line["authors"] = fix_text(parsed_line["authors"])

                # title could be fucked up
                parsed_line["title"] = fix_text(parsed_line["title"])

                # we dont care about comments, but we defuck them anyway
                if parsed_line["comments"] is None:
                    parsed_line["comments"] = ""
                else:
                    parsed_line["comments"] = fix_text(parsed_line["comments"])

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
                parsed_line["abstract"] = fix_text(parsed_line["abstract"])

                # update_date is ok

                lines.append(parsed_line)
            yield lines


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

        if elastic_amount == postgres_amount and postgres_amount > 0 and not force:
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

    parts = 25

    logger.info("Starting to parse lines")

    with Session(engine) as session:
        for i, batches in enumerate(parse_lines(path_to_dump, parts=parts)):

            # we need to insert into elastic first, because postgres_fix may breaks dicts
            helpers.bulk(elastic, map(do_elastic_fixes, batches))
            logger.debug(f"Inserted {(i + 1)/ parts * 100:.2f}% of data into elastic")

            # we need to insert into postgres
            for entry in batches:
                paper = ArxivPaperModel(**do_postgres_fixes(entry))
                session.add(paper)

            session.commit()
            logger.debug(f"Inserted {(i + 1)/ parts * 100:.2f}% of data into postgres")


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
        action="store_true",
        help="Force setup even if data already exists",
    )
    args = parser.parse_args()

    setup_bases(args.path, force=args.force)
