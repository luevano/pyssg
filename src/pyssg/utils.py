import os
import sys
import shutil
from hashlib import md5
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


# TODO: add file exclusion option
def get_file_list(path: str,
                  exts: tuple[str],
                  exclude_dirs: list[str] = []) -> list[str]:
    log.debug('retrieving file list in path "%s" that contain file'
              ' extensions %s except directories %s', path, exts, exclude_dirs)
    file_list: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude_dirs != []:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(exts):
                # [1:] is required to remove the '/' at the beginning after replacing
                file_name: str = os.path.join(root, file).replace(path, '')[1:]
                file_list.append(file_name)
                log.debug('added file "%s" without "%s" part: "%s"',
                          file, path, file_name)
            else:
                log.debug('ignoring file "%s" as it doesn\'t contain'
                          ' any of the extensions %s', file, exts)
    return file_list


def get_dir_structure(path: str,
                      exclude: list[str] = []) -> list[str]:
    log.debug('retrieving dir structure in path "%s" except directories (%s)',
              path, ', '.join(exclude))
    dir_list: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude != []:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]
        for d in dirs:
            if root in dir_list:
                dir_list.remove(root)
                log.debug('removed dir "%s" as it already is in the list', root)
            # not removing the 'path' part here, as comparisons with 'root' would fail
            joined_dir: str = os.path.join(root, d)
            dir_list.append(joined_dir)
            log.debug('added dir "%s" to the list', joined_dir)
    log.debug('removing "%s" from all dirs in list', path)
    # [1:] is required to remove the '/' at the beginning after replacing
    return [d.replace(path, '')[1:] for d in dir_list]


def create_dir(path: str, p: bool = False, silent=False) -> None:
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        if not silent:
            log.info('created directory "%s"', path)
    except FileExistsError:
        if not silent:
            log.info('directory "%s" already exists, ignoring', path)


def copy_file(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        log.info('copied file "%s" to "%s"', src, dst)
    else:
        log.info('file "%s" already exists, ignoring', dst)


# only used for database, but keeping it here as it is an independent function
# as seen in SO: https://stackoverflow.com/a/1131238
def get_checksum(path: str) -> str:
    log.debug('calculating md5 checksum for "%s"', path)
    file_hash = md5()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_expanded_path(path: str) -> str:
    log.debug('expanding path "%s"', path)
    expanded_path: str = os.path.normpath(os.path.expandvars(path))
    if '$' in expanded_path:
        log.error('"$" character found in expanded path "%s";'
                  ' could be due to non-existant env var', expanded_path)
        sys.exit(1)
    log.debug('expanded path "%s" to "%s"', path, expanded_path)
    return expanded_path
