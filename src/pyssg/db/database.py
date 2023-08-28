import json
import sqlite3
from logging import Logger, getLogger
from sqlite3 import PARSE_DECLTYPES, Connection, Cursor
from typing import Any, Sequence

from pyssg.db.tuple import adapt_tuple, convert_tuple
from pyssg.db.queries import CREATE_FILES_TABLE, SELECT_FILE, SELECT_FILE_ALL, INSERT_FILE, UPDATE_FILE, UPDATE_FILE_TAGS

log: Logger = getLogger(__name__)


class Database:
    def __init__(self, path: str) -> None:
        sqlite3.register_adapter(tuple, adapt_tuple)
        sqlite3.register_converter("tuple", convert_tuple)
        self.con: Connection = sqlite3.connect(path, detect_types=PARSE_DECLTYPES)
        self.cur: Cursor = self.con.cursor()
        # create statements are always commited
        self.query(CREATE_FILES_TABLE)


    # commits the transactions, closes connection and cursor
    def write(self) -> None:
        self.con.commit()
        self.cur.close()
        self.con.close()


    def query(self, sql: str,
              params: dict | Sequence = ()) -> list[Any]:
        return self.cur.execute(sql, params).fetchall()


    # commit query, doesn't wait until calling con.commit()
    def cquery(self, sql: str,
               params: dict | Sequence = ()) -> list[Any]:
        out: list[Any]
        with self.con:
            out = self.query(sql, params)
        return out


    def select(self, fname: str) -> tuple | None:
        out: list[Any]
        out = self.query(SELECT_FILE, (fname,))
        return out[0] if out else None


    def select_all(self) -> list[Any] | None:
        out: list[Any] = self.query(SELECT_FILE_ALL)
        return out if out else None


    def insert(self, fname: str,
               ctime: float,
               checksum: str,
               tags: tuple | None = None) -> None:
        params: tuple = (fname, ctime, checksum, tags)
        out: tuple = self.query(INSERT_FILE, params)[0]
        log.debug("insert %s", out)


    def update(self, fname: str,
               mtime: float,
               checksum: str,
               tags: tuple | None = None) -> None:
        params: tuple = (mtime, checksum, tags, fname)
        out: tuple = self.query(UPDATE_FILE, params)[0]
        log.debug("update %s", out)


    def update_tags(self, fname: str,
                    tags: tuple | None = None) -> None:
        params: tuple = (tags, fname)
        out: tuple = self.query(UPDATE_FILE_TAGS, params)[0]
        log.debug("update %s", out)

