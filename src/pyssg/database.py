import os
import sys
import logging
from logging import Logger

log: Logger = logging.getLogger(__name__)


# db class that works for both html and md files
class Database:
    COLUMN_NUM: int = 4

    def __init__(self, db_path: str):
        log.debug('initializing the page db on path "%s"', db_path)
        self.db_path: str = db_path
        self.e: dict[str, tuple[float, float, list[str]]] = dict()


    # updates the tags for a specific entry (file)
    #   file_name only contains the entry name (without the absolute path)
    def update_tags(self, file_name: str,
                    tags: list[str]) -> None:
        if file_name in self.e:
            log.debug('updating tags for entry "%s"', file_name)
            cts, mts, old_tags = self.e[file_name]
            log.debug('entry "%s" old content: (%s, %s, (%s))',
                      file_name, cts, mts, ', '.join(old_tags))
            self.e[file_name] = (cts, mts, tags)
            log.debug('entry "%s" new content: (%s, %s, (%s))',
                      file_name, cts, mts, ', '.join(tags))
        else:
            log.error('can\'t update tags for entry "%s",'
                      ' as it is not present in db', file_name)
            sys.exit(1)


    # returns a bool that indicates if the entry
    # was (includes new entries) or wasn't updated
    def update(self, file_name: str,
               remove: str=None) -> bool:
        log.debug('updating entry for file "%s"', file_name)
        # initial default values
        f: str = file_name
        tags: list[str] = []
        if remove is not None:
            f = file_name.replace(remove, '')
            log.debug('removed "%s" from "%s": "%s"', remove, file_name, f)


        # get current time, needs actual file name
        time: float = os.stat(file_name).st_mtime
        log.debug('modified time for "%s": %s', file_name, time)

        # three cases, 1) entry didn't exist,
        # 2) entry hasn't been mod and,
        # 3) entry has been mod
        #1)
        if f not in self.e:
            log.debug('entry "%s" didn\'t exist, adding with defaults', f)
            self.e[f] = (time, 0.0, tags)
            return True

        old_time, old_mod_time, tags = self.e[f]
        log.debug('entry "%s" old content: (%s, %s, (%s))',
                  f, old_time, old_mod_time, ', '.join(tags))

        # 2)
        if old_mod_time == 0.0:
            if time > old_time:
                log.debug('entry "%s" has been modified for the first'
                          ' time, updating', f)
                self.e[f] = (old_time, time, tags)
                log.debug('entry "%s" new content: (%s, %s, (%s))',
                          f, old_time, time, ', '.join(tags))
                return True
        # 3)
        else:
            if time > old_mod_time:
                log.debug('entry "%s" has been modified, updating', f)
                self.e[f] = (old_time, time, tags)
                log.debug('entry "%s" new content: (%s, %s, (%s))',
                          f, old_time, time, ', '.join(tags))
                return True

        log.debug('entry "%s" hasn\'t been modified', f)
        return False


    def write(self) -> None:
        log.debug('writing db')
        for k, v in self.e.items():
            log.debug('parsing row for page "%s"', k)
            t: str = None
            row: str = None
            if len(v[2]) == 0:
                t = '-'
            else:
                t = ','.join(v[2])

            row = f'{k} {v[0]} {v[1]} {t}'

            log.debug('writing row: "%s\\n"', row)
            with open(self.db_path, 'w') as file:
                file.write(f'{row}\n')


    def read(self) -> None:
        log.debug('reading db')
        if not os.path.exists(self.db_path):
            log.warning('"%s" doesn\'t exist, will be'
                        ' created once process finishes,'
                        ' ignore if it\'s the first run', self.db_path)
            return

        if os.path.exists(self.db_path) and not os.path.isfile(self.db_path):
            log.error('"%s" is not a file"', self.db_path)
            sys.exit(1)

        rows: list[str] = None
        with open(self.db_path, 'r') as file:
            rows = file.readlines()
        log.info('db contains %d rows', len(rows))

        # parse each entry and populate accordingly
        l: list[str] = None
        # l=list of values in entry
        log.debug('parsing rows from db')
        for it, row in enumerate(rows):
            i = it + 1
            r = row.strip()
            log.debug('row %d content: "%s"', i, r)
            l = tuple(r.split())
            if len(l) != self.COLUMN_NUM:
                log.critical('row %d doesn\'t contain %s columns,'
                             ' contains %d elements; row %d content: "%s"',
                             i, self.COLUMN_NUM, len(l), i, r)
                sys.exit(1)

            t: list[str] = None
            if l[3] == '-':
                t = []
            else:
                t = l[3].split(',')
            log.debug('tag content: (%s)', ', '.join(t))

            self.e[l[0]] = (float(l[1]), float(l[2]), t)
