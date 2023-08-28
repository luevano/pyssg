import os
import sys
import shutil
from hashlib import md5
from logging import Logger, getLogger
from datetime import datetime, timezone

log: Logger = getLogger(__name__)


# TODO: add file exclusion option
def get_file_list(path: str,
                  exts: tuple[str],
                  exclude_dirs: list[str] = []) -> list[str]:
    log.debug('retrieving file list in "%s",'
              ' extensions %s, except dirs %s',
              path, exts, exclude_dirs)
    file_list: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude_dirs != []:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(exts):
                # [1:] is required to remove the '/'
                #   at the beginning after replacing
                fname: str = os.path.join(root, file)
                fname = fname.replace(path, '')[1:]
                file_list.append(fname)
                log.debug('added "%s"', fname)
            else:
                log.debug('ignoring "%s", doesn\'t contain'
                          ' extensions %s', file, exts)
    return file_list


def get_dir_structure(path: str,
                      exclude: list[str] = []) -> list[str]:
    log.debug('retrieving dir structure in "%s",'
              ' except dirs %s', path, exclude)
    dir_list: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude != []:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]
        for d in dirs:
            if root in dir_list:
                dir_list.remove(root)
            # not removing the 'path' part here,
            #   as comparisons with 'root' would fail
            dname: str = os.path.join(root, d)
            dir_list.append(dname)
            log.debug('added dir "%s" to the list', dname)
    # [1:] is required to remove the '/' at the beginning after replacing
    return [d.replace(path, '')[1:] for d in dir_list]


# TODO: probably change it so it returns a bool, easier to check
def create_dir(path: str, p: bool = False) -> None:
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        log.info('created directory "%s"', path)
    except FileExistsError:
        log.debug('directory "%s" exists, ignoring', path)


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


# as seen in SO: https://stackoverflow.com/a/1131238
def get_checksum(path: str) -> str:
    file_hash = md5()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            file_hash.update(chunk)
    out: str = file_hash.hexdigest()
    log.debug('md5 checksum of "%s": %s', path, out)
    return out


def get_expanded_path(path: str) -> str:
    epath: str = os.path.normpath(os.path.expandvars(path))
    if '$' in epath:
        log.error('"$" character found in expanded path "%s",'
                  ' could be due to non-existant env var', epath)
        sys.exit(1)
    log.debug('expanded path "%s" to "%s"', path, epath)
    return epath


def get_file_stats(path: str) -> tuple[str, float]:
    time: float = os.stat(path).st_mtime
    chksm: str = get_checksum(path)
    return (chksm, time)


def get_time_now(fmt: str, tz: timezone=timezone.utc) -> str:
    return datetime.now(tz=tz).strftime(fmt)

