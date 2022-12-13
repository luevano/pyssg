import os
import sys
import csv
from logging import Logger, getLogger

from .utils import get_checksum
from .database_entry import DatabaseEntry

log: Logger = getLogger(__name__)


# db class that works for both html and md files
class Database:
    __COLUMN_NUM: int = 5
    __COLUMN_DELIMITER: str = '|'

    def __init__(self, db_path: str) -> None:
        log.debug('initializing the page db on path "%s"', db_path)
        self.db_path: str = db_path
        self.e: dict[str, DatabaseEntry] = dict()

    def update_tags(self, file_name: str,
                    new_tags: list[str]) -> None:
        # technically, I should ensure this function can only run if self.e is populated
        if file_name in self.e:
            log.debug('updating tags for entry "%s"', file_name)
            log.debug('entry "%s" old tags: %s',
                      file_name, self.e[file_name])

            self.e[file_name].update_tags(new_tags)
            log.debug('entry "%s" new tags: %s',
                      file_name, self.e[file_name])
        else:
            log.error('can\'t update tags for entry "%s",'
                      ' as it is not present in db', file_name)
            sys.exit(1)

    def update(self, file_name: str,
               remove: str='') -> None:
        log.debug('updating entry for file "%s"', file_name)
        f: str = file_name
        tags: list[str] = []
        if remove != '':
            f = file_name.replace(remove, '')
            log.debug('removed "%s" from "%s": "%s"', remove, file_name, f)

        # get current time, needs actual file name
        time: float = os.stat(file_name).st_mtime
        log.debug('time for "%s": %s', file_name, time)

        # calculate current checksum, also needs actual file name
        checksum: str = get_checksum(file_name)
        log.debug('checksum for "%s": "%s"', file_name, checksum)

        # three cases, 1) entry didn't exist,
        # 2) entry has been mod and,
        # 3) entry hasn't been mod
        #1)
        if f not in self.e:
            log.debug('entry "%s" didn\'t exist, adding with defaults', f)
            self.e[f] = DatabaseEntry([f, time, 0.0, checksum, tags])
            return

        # old_e is old entity
        old_e: DatabaseEntry = self.e[f]
        log.debug('entry "%s" old content: %s', f, old_e)

        # 2)
        if checksum != old_e.checksum:
            log.debug('entry "%s" has been modified, updating', f)
            self.e[f] = DatabaseEntry([f, old_e.ctimestamp, time, checksum, tags])
            log.debug('entry "%s" new content: (%s, %s, %s, (%s))', f, self.e[f])
            return
        # 3)
        else:
            log.debug('entry "%s" hasn\'t been modified', f)
            return

    def write(self) -> None:
        log.debug('writing db')
        with open(self.db_path, 'w') as file:
            csv_writer = csv.writer(file, delimiter=self.__COLUMN_DELIMITER)
            for _, v in self.e.items():
                log.debug('writing row: %s', v)
                csv_writer.writerow(v.get_raw_entry())

    def _db_path_exists(self) -> bool:
        log.debug('checking that "%s" exists or is a file', self.db_path)
        if not os.path.exists(self.db_path):
            log.warning('"%s" doesn\'t exist, will be'
                        ' created once process finishes,'
                        ' ignore if it\'s the first run', self.db_path)
            return False
        if not os.path.isfile(self.db_path):
            log.error('"%s" is not a file"', self.db_path)
            sys.exit(1)
        return True

    def _get_csv_rows(self) -> list[list[str]]:
        rows: list[list[str]]
        with open(self.db_path, 'r') as f:
            csv_reader = csv.reader(f, delimiter=self.__COLUMN_DELIMITER)
            rows = list(csv_reader)
        log.debug('db contains %d rows', len(rows))
        return rows

    # TODO: don't include files that are not in the db anymore
    def read(self) -> None:
        log.debug('reading db')
        if not self._db_path_exists():
            return

        rows: list[list[str]] = self._get_csv_rows()
        # l=list of values in entry
        log.debug('parsing rows from db')
        for it, row in enumerate(rows):
            i: int = it + 1
            col_num: int = len(row)
            log.debug('row %d content: "%s"', i, row)
            if col_num != self.__COLUMN_NUM:
                log.critical('row %d doesn\'t contain %s columns, contains %d'
                             ' columns: "%s"',
                             i, self.__COLUMN_NUM, col_num, row)
                sys.exit(1)
            entry: DatabaseEntry = DatabaseEntry(row)
            self.e[entry.fname] = entry
