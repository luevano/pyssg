from .pyssg import main
from .custom_logger import setup_logger


setup_logger()
# not meant to be used as a package, so just give main
__all__ = ['main']
