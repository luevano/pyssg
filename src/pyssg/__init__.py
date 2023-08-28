from pyssg.pyssg import main
from pyssg.custom_logger import setup_logger
from pyssg.cfg.yaml_parser import setup_custom_yaml


setup_logger()
setup_custom_yaml()
# not meant to be used as a package, so just give main
__all__ = ['main']
