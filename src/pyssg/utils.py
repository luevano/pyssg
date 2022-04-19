import os
import sys
import shutil
import logging
from logging import Logger

log: Logger = logging.getLogger(__name__)


def create_dir(path: str, p: bool=False) -> None:
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        log.info('created directory "%s"', path)
    except FileExistsError:
        log.info('directory "%s" already exists, ignoring', path)


def copy_file(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        log.info('copied file "%s" to "%s"', src, dst)
    else:
        log.info('file "%s" already exists, ignoring', dst)


def sanity_check_path(path: str) -> None:
    if '$' in  path:
        log.error('"$" character found in path "%s";'
                  ' could be due to non-existant env var.', path)
        sys.exit(1)
