import json
import re

def extract_year_from_created(created_str):
    # "Sun, 1 Apr 2007 12:04:13 GMT"
    match = re.search(r'\b\d{4}\b', created_str)
    return int(match.group()) if match else None

def find_min_year_from_jsonl(file_path):
    min_year = float('inf')

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                versions = record.get("versions", [])
                for version in versions:
                    created = version.get("created", "")
                    year = extract_year_from_created(created)
                    if year is not None and year < min_year:
                        min_year = year
            except json.JSONDecodeError:
                continue 

    return min_year if min_year != float('inf') else None

file_path = "arxiv-processed.jsonl"
min_created_year = find_min_year_from_jsonl(file_path)
print(f"Najwcześniejszy rok w polu 'created': {min_created_year}")