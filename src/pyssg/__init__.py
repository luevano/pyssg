from .pyssg import main
import logging
from logging import Logger, StreamHandler
from .per_level_formatter import PerLevelFormatter


# since this is the root package, setup the logger here,
#   set DEBUG here for testing purposes, can't make it 
#   dynamic yet (with a flag, for example)
__LOG_LEVEL: int = logging.INFO
log: Logger = logging.getLogger(__name__)
log.setLevel(__LOG_LEVEL)
ch: StreamHandler = StreamHandler()
ch.setLevel(__LOG_LEVEL)
ch.setFormatter(PerLevelFormatter())
log.addHandler(ch)

# not meant to be used as a package, so just give main
__all__ = ['main']