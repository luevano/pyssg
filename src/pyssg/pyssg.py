import os
import sys
from importlib.resources import path as rpath
from typing import Union
from logging import Logger, getLogger, DEBUG
from argparse import ArgumentParser

from .arg_parser import get_parser
from .utils import create_dir, copy_file, get_expanded_path
from .configuration import get_parsed_config, VERSION
from .database import Database
from .builder import Builder

log: Logger = getLogger(__name__)


def main() -> None:
    arg_parser: ArgumentParser = get_parser()
    args: dict[str, Union[str, bool]] = vars(arg_parser.parse_args())

    # TODO: move this logic to the logger
    # too messy to place at utils.py, don't want to be
    #   passing the arg parser around
    def _log_perror(message: str) -> None:
        arg_parser.print_usage()
        # even if it's an error, print it as info
        #   as it is not critical, only config related
        log.info(f'pyssg: error: {message}, --help for more')
        sys.exit(1)

    # -1 as first argument is program path
    num_args = len(sys.argv) - 1
    if num_args == 2 and args['config']:
        _log_perror('only config argument passed')
    elif not num_args > 0 or (num_args == 1 and args['debug']):
        _log_perror('no arguments passed')
    elif num_args == 3 and (args['debug'] and args['config']):
        _log_perror('no arguments passed other than "debug" and "config"')

    if args['version']:
        log.info('pyssg v%s', VERSION)
        sys.exit(0)

    # TODO: move this logic to the logger
    if args['debug']:
        # need to modify the root logger specifically,
        #   as it is the one that holds the config
        #   (__name__ happens to resolve to pyssg in __init__)
        root_logger: Logger = getLogger('pyssg')
        root_logger.setLevel(DEBUG)
        for handler in root_logger.handlers:
            handler.setLevel(DEBUG)
        log.debug('changed logging level to DEBUG')

    # TODO: modify init arg in argparser
    if args['init']:
        init_dir: str = os.path.normpath(get_expanded_path(str(args['init'])))
        log.info('initializing directory structure and copying templates')
        create_dir(init_dir)
        with rpath('pyssg.plt', 'default.yaml') as p:
            copy_file(str(p), os.path.join(init_dir, 'config.yaml'))
        create_dir(os.path.join(init_dir, 'src'))
        create_dir(os.path.join(init_dir, 'dst'))
        create_dir(os.path.join(init_dir, 'plt'))
        files: list[str] = ['index.html',
                            'page.html',
                            'tag.html',
                            'rss.xml',
                            'sitemap.xml',
                            'entry.md']
        log.debug('list of files to copy over: (%s)', ', '.join(files))
        for f in files:
            plt_file: str = os.path.join(os.path.join(init_dir, 'plt'), f)
            with rpath('pyssg.plt', f) as p:
                copy_file(str(p), plt_file)
        log.info('finished initialization')
        sys.exit(0)

    config_path: str = get_expanded_path(str((args['config']))) \
                        if args['config'] else 'config.yaml'

    if not os.path.exists(config_path):
        log.error('config file does\'t exist in path "%s"; make sure'
                  ' the path is correct; use --init <dir> if it\'s the'
                  ' first time if you haven\'t already', config_path)
        sys.exit(1)

    log.debug('reading config files')
    config: list[dict] = get_parsed_config(config_path)
    print(config)

    log.debug('exiting due to testing')
    sys.exit(0)
    if args['build']:
        log.info('building the html files')
        for conf in config:
            log.info('building html for "%s"', conf['title'])
            db: Database = Database(conf['path']['db'])
            db.read()

            log.debug('building all dir_paths found in conf')
            for dir_path in conf['dirs'].keys():
                log.debug('building for "%s"', dir_path)
                builder: Builder = Builder(conf, db, dir_path)
                builder.build()

            db.write()
        log.info('finished building the html files')
        sys.exit(0)
