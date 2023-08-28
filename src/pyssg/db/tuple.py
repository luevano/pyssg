import json
# for more https://docs.python.org/3.11/library/sqlite3.html#adapter-and-converter-recipes
#   and https://docs.python.org/3.11/library/sqlite3.html#sqlite3.PARSE_DECLTYPES


def adapt_tuple(data: tuple | None) -> str | None:
    return json.dumps(data) if data else None


def convert_tuple(data: str | None) -> tuple | None:
    return tuple(json.loads(data)) if data else None

