from typing import Union
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


class DatabaseEntry:
    # not specifying the type of "list" as it could be only str
    #   or the actual values
    def __init__(self, entry: list) -> None:
        self.fname: str = entry[0]
        self.ctimestamp: float = float(entry[1])
        self.mtimestamp: float = float(entry[2])
        self.checksum: str = entry[3]
        self.tags: list[str] = []

        if isinstance(entry[4], list):
            self.tags = entry[4]
        else:
            if entry[4] != '-':
                self.tags = entry[4].split(',')

        log.debug('"%s" tags: %s', self.fname, self.tags)

    def __str__(self) -> str:
        _return_str: str = '[{}, {}, {}, {}, {}]'\
            .format(self.fname,
                    self.ctimestamp,
                    self.mtimestamp,
                    self.checksum,
                    self.tags)
        return _return_str

    # used for csv writing
    def get_raw_entry(self) -> list[str]:
        return [self.fname,
                str(self.ctimestamp),
                str(self.mtimestamp),
                self.checksum,
                ','.join(self.tags) if self.tags else '-']

    def update_tags(self, new_tags: list[str]) -> None:
        self.tags = new_tags
