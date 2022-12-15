import os
import sys
from importlib.resources import path as rpath
from typing import Union
from logging import Logger, getLogger, DEBUG
from argparse import ArgumentParser

from .arg_parser import get_parser
from .utils import create_dir, copy_file, get_expanded_path
from .configuration import get_parsed_config, get_static_config, DEFAULT_CONFIG_PATH, VERSION
from .database import Database
from .builder import Builder

log: Logger = getLogger(__name__)


def main() -> None:
    arg_parser: ArgumentParser = get_parser()
    args: dict[str, Union[str, bool]] = vars(arg_parser.parse_args())

    # too messy to place at utils.py, don't want to be
    #   passing the arg parser around
    def _log_perror(message: str) -> None:
        arg_parser.print_usage()
        # even if it's an error, print it as info
        #   as it is not critical, only config related
        log.info(message)
        sys.exit(1)

    # -1 as first argument is program path
    num_args = len(sys.argv) - 1
    if num_args == 2 and args['config']:
        _log_perror('pyssg: error: only config argument passed, --help for more')
    elif not num_args > 0 or (num_args == 1 and args['debug']):
        _log_perror('pyssg: error: no arguments passed, --help for more')
    elif num_args == 3 and (args['debug'] and args['config']):
        _log_perror("pyssg: error: no arguments passed other than 'debug' and 'config', --help for more")

    if args['version']:
        log.info('pyssg v%s', VERSION)
        sys.exit(0)

    if args['debug']:
        # need to modify the root logger specifically,
        #   as it is the one that holds the config
        #   (__name__ happens to resolve to pyssg in __init__)
        root_logger: Logger = getLogger('pyssg')
        root_logger.setLevel(DEBUG)
        for handler in root_logger.handlers:
            handler.setLevel(DEBUG)
        log.debug('changed logging level to DEBUG')

    config_path: str = str(args['config']) if args['config'] else DEFAULT_CONFIG_PATH
    # only needed for the DEFAULT_CONFIG_PATH
    config_path = get_expanded_path(config_path)
    config_dir, _ = os.path.split(config_path)
    log.debug('checked config file path, final config path "%s"', config_path)

    if args['copy_default_config']:
        log.info('copying default config file')
        create_dir(config_dir)
        with rpath('pyssg.plt', 'default.yaml') as p:
            copy_file(str(p), config_path)
        sys.exit(0)

    if not os.path.exists(config_path):
        log.error('config file does\'t exist in path "%s"; make sure'
                  ' the path is correct; use --copy-default-config if it\'s the'
                  ' first time if you haven\'t already', config_path)
        sys.exit(1)

    log.debug('reading config files')
    config_all: list[dict] = get_parsed_config(config_path)
    static_config: dict = get_static_config()
    log.debug('applying static_config for each config document')
    for config in config_all:
        config['fmt']['rss_date'] = static_config['fmt']['rss_date']
        config['fmt']['sitemap_date'] = static_config['fmt']['sitemap_date']
        config['info'] = dict()
        config['info']['version'] = static_config['info']['version']
        config['info']['debug'] = str(args['debug'])

    if args['init']:
        log.info('initializing the directory structure and copying over templates')
        for config in config_all:
            log.info('initializing directories for "%s"', config['title'])
            create_dir(config['path']['src'])
            # dst gets created on builder
            # create_dir(config['path']['dst'])
            create_dir(config['path']['plt'])
            files: list[str] = ['index.html',
                                'page.html',
                                'tag.html',
                                'rss.xml',
                                'sitemap.xml']
            log.debug('list of files to copy over: (%s)', ', '.join(files))
            for f in files:
                plt_file: str = os.path.join(config['path']['plt'], f)
                with rpath('pyssg.plt', f) as p:
                    copy_file(str(p), plt_file)
        log.info('finished initialization')
        sys.exit(0)


    if args['build']:
        log.info('building the html files')
        for config in config_all:
            log.info('building html for "%s"', config['title'])
            db: Database = Database(config['path']['db'])
            db.read()

            log.debug('building all dir_paths found in config')
            for dir_path in config['dirs'].keys():
                log.debug('building for "%s"', dir_path)
                builder: Builder = Builder(config, db, dir_path)
                builder.build()

            db.write()
        log.info('finished building the html files')
        sys.exit(0)
