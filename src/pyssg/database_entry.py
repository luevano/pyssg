import sys
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


class DatabaseEntry:
    # ignoring return type as it makes the line too long, unnecessary, too
    def __init__(self, entry: tuple[str, float, float, str, str | set[str]]):
        self.fname: str = str(entry[0])
        self.ctimestamp: float = float(entry[1])
        self.mtimestamp: float = float(entry[2])
        self.checksum: str = str(entry[3])
        self.tags: set[str] = set()

        if isinstance(entry[4], set):
            self.tags = entry[4]
            self.__remove_invalid()
        elif isinstance(entry[4], str):
            if entry[4] != '-':
                self.tags = set(e.strip() for e in str(entry[4]).split(','))
                self.__remove_invalid()
        # this should be unreachable as the type has to be str or set[str],
        #   but I have just in case to evade bugs
        else:
            log.error('tags has to be either a set or string (comma separated)')
            sys.exit(1)

        log.debug('"%s" tags: %s', self.fname, self.tags)

    def __str__(self) -> str:
        _return_str: str = "['{}', {}, {}, '{}', {}]"\
            .format(self.fname,
                    self.ctimestamp,
                    self.mtimestamp,
                    self.checksum,
                    sorted(self.tags))
        return _return_str

    def __remove_invalid(self) -> None:
        if '-' in self.tags:
            self.tags.remove('-')

    # used for csv writing
    def get_raw_entry(self) -> list[str]:
        return [self.fname,
                str(self.ctimestamp),
                str(self.mtimestamp),
                self.checksum,
                ','.join(sorted(self.tags)) if self.tags else '-']

    def update_tags(self, new_tags: set[str]) -> None:
        self.tags = new_tags
        self.__remove_invalid()
