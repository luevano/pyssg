import logging
from logging import Formatter


class PerLevelFormatter(logging.Formatter):
    # colors for the terminal in ansi
    yellow: str = "\x1b[33m"
    red: str = "\x1b[31m"
    bold_red: str = "\x1b[31;1m"
    reset: str = "\x1b[0m"

    DATE_FMT: str = '%Y-%m-%d %H:%M:%S'
    COMMON_FMT: str = '[%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d]: %(message)s'
    FORMATS: dict[int, str] = {
        logging.DEBUG: COMMON_FMT,
        logging.INFO: '%(message)s',
        logging.WARNING: f'{yellow}{COMMON_FMT}{reset}',
        logging.ERROR: f'{red}{COMMON_FMT}{reset}',
        logging.CRITICAL: f'{bold_red}{COMMON_FMT}{reset}'
    }


    def format(self, record: str) -> str:
        fmt: str = self.FORMATS.get(record.levelno)
        formatter: Formatter = logging.Formatter(
            fmt=fmt, datefmt=self.DATE_FMT, style='%')

        return formatter.format(record)
