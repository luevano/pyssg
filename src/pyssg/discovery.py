import os
import logging
from logging import Logger

log: Logger = logging.getLogger(__name__)


def get_file_list(path: str,
                  exts: list[str],
                  exclude: list[str]=None) -> list[str]:
    log.debug('retrieving file list in path "%s" that contain file'
              ' extensions (%s) except (%s)',
              path, ', '.join(exts),
              ', '.join(exclude if exclude is not None else []))
    out: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude is not None:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]

        for f in files:
            if f.endswith(tuple(exts)):
                stripped_f: str = os.path.join(root, f).replace(path, '')[1:]
                out.append(stripped_f)
                log.debug('added file "%s" without "%s" part: "%s"',
                          f, path, stripped_f)
            else:
                log.debug('ignoring file "%s" as it doesn\'t contain'
                          ' any of the extensions (%s)', f, ', '.join(exts))

    return out


def get_dir_structure(path: str,
                      exclude: list[str]=None) -> list[str]:
    log.debug('retrieving dir structure in path "%s" except (%s)',
              path, ', '.join(exclude if exclude is not None else []))
    out: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude is not None:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]

        for d in dirs:
            if root in out:
                out.remove(root)
                log.debug('removed dir "%s" as it already is in the list', root)
            joined_dir: str = os.path.join(root, d)
            out.append(joined_dir)
            log.debug('added dir "%s" to the list', joined_dir)

    log.debug('removing "%s" from all dirs in list', path)
    return [o.replace(path, '')[1:] for o in out]
