from logging import Formatter, LogRecord, DEBUG, INFO, WARNING, ERROR, CRITICAL

# only reason for this class is to get info formatting as normal text
#   and everything else with more info and with colors
class PerLevelFormatter(Formatter):
    # colors for the terminal in ansi
    __YELLOW: str = '\x1b[33m'
    __RED: str = '\x1b[31m'
    __BOLD_RED: str = '\x1b[31;1m'
    __RESET: str = '\x1b[0m'

    __DATE_FMT: str = '%Y-%m-%d %H:%M:%S'
    __COMMON_FMT: str = '[%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d]: %(message)s'
    __FORMATS: dict[int, str] = {
        DEBUG: __COMMON_FMT,
        INFO: '%(message)s',
        WARNING: f'{__YELLOW}{__COMMON_FMT}{__RESET}',
        ERROR: f'{__RED}{__COMMON_FMT}{__RESET}',
        CRITICAL: f'{__BOLD_RED}{__COMMON_FMT}{__RESET}'
    }

    def format(self, record: LogRecord) -> str:
        # this should never fail, as __FORMATS is defined above,
        #   so no issue of just converting to str
        fmt: str = str(self.__FORMATS.get(record.levelno))
        formatter: Formatter = Formatter(
            fmt=fmt, datefmt=self.__DATE_FMT, style='%')
        return formatter.format(record)
