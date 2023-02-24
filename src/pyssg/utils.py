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
                # [1:] is required to remove the '/'
                #   at the beginning after replacing
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
            # not removing the 'path' part here,
            #   as comparisons with 'root' would fail
            joined_dir: str = os.path.join(root, d)
            dir_list.append(joined_dir)
            log.debug('added dir "%s" to the list', joined_dir)
    log.debug('removing "%s" from all dirs in list', path)
    # [1:] is required to remove the '/' at the beginning after replacing
    return [d.replace(path, '')[1:] for d in dir_list]


# TODO: probably change it so it returns a bool, easier to check
def create_dir(path: str, p: bool = False, silent=False) -> None:
    log_msg: str = ''
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        log_msg = f'created directory "{path}"'
        if not silent:
            log.info(log_msg)
        log.debug(log_msg)
    except FileExistsError:
        log_msg = f'directory "{path}" exists, ignoring'
        if not silent:
            log.info(log_msg)
        log.debug(log_msg)


# TODO: change this as it doesn't take directories into account,
#   a file can be copied into a directory, need to get the filename
#   and use it when copying
# TODO: probably change it so it returns a bool, easier to check
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
