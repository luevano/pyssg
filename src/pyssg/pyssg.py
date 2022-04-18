import os
import sys
import logging
from logging import Logger
from importlib.resources import path as rpath
from typing import Union
from configparser import ConfigParser

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from yafg import YafgExtension
from MarkdownHighlight.highlight import HighlightExtension
from markdown_checklist.extension import ChecklistExtension

from .utils import create_dir, copy_file, sanity_check_path
from .arg_parser import get_parsed_arguments
from .configuration import get_parsed_config, DEFAULT_CONFIG_PATH, VERSION
from .database import Database
from .builder import Builder

log: Logger = logging.getLogger(__name__)


def main() -> None:
    args: dict[str, Union[str, bool]] = vars(get_parsed_arguments())

    if args['debug']:
        # need to modify the root logger specifically,
        #   as it is the one that holds the config
        #   (__name__ happens to resolve to pyssg in __init__)
        root_logger: Logger = logging.getLogger('pyssg')
        root_logger.setLevel(logging.DEBUG)
        for handler in root_logger.handlers:
            handler.setLevel(logging.DEBUG)
        log.debug('changed logging level to DEBUG')

    if not len(sys.argv) > 1 or (len(sys.argv) == 2 and args['debug']):
        log.info('pyssg v%s - no arguments passed, --help for more', VERSION)
        sys.exit(0)

    if args['version']:
        log.info('pyssg v%s', VERSION)
        sys.exit(0)

    log.debug('checking config file path')
    config_path: str = args['config'] if args['config'] else DEFAULT_CONFIG_PATH
    config_path = os.path.normpath(os.path.expandvars(config_path))
    sanity_check_path(config_path)
    config_dir, _ = os.path.split(config_path)
    log.debug('checked config file path, final config path "%s"', config_path)

    if args['copy_default_config']:
        log.info('copying default config file')
        create_dir(config_dir)
        with rpath('pyssg.plt', 'default.ini') as p:
            copy_file(p, config_path)
        sys.exit(0)

    if not os.path.exists(config_path):
        log.error('config file does\'t exist in path "%s"; make sure'
                  ' the path is correct; use --copy-default-config if it\'s the'
                  ' first time if you haven\'t already', config_path)
        sys.exit(1)

    config: ConfigParser = get_parsed_config(config_path)

    if args['init']:
        log.info('initializing the directory structure and copying over templates')
        create_dir(config.get('path', 'src'))
        create_dir(os.path.join(config.get('path', 'dst'), 'tag'), True)
        create_dir(config.get('path', 'plt'))
        files: list[str] = ('index.html',
                            'page.html',
                            'tag.html',
                            'rss.xml',
                            'sitemap.xml')
        log.debug('list of files to copy over: (%s)', ', '.join(files))
        for f in files:
            plt_file: str = os.path.join(config.get('path', 'plt'), f)
            with rpath('pyssg.plt', f) as p:
                copy_file(p, plt_file)
        sys.exit(0)

    if args['build']:
        log.debug('building the html files')
        db: Database = Database(os.path.join(config.get('path', 'src'), '.files'))
        db.read()

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
        log.debug('initializing the jinja environment')
        env: Environment = Environment(loader=FileSystemLoader(config.get('path', 'plt')),
                                       autoescape=False,
                                       trim_blocks=True,
                                       lstrip_blocks=True)

        # md extensions
        exts: list = ['extra',
                      'meta',
                      'sane_lists',
                      'smarty',
                      'toc',
                      'wikilinks',
                      # stripTitle generates an error when True,
                      # if there is no title attr
                      YafgExtension(stripTitle=False,
                                    figureClass="",
                                    figcaptionClass="",
                                    figureNumbering=False,
                                    figureNumberClass="number",
                                    figureNumberText="Figure"),
                      HighlightExtension(),
                      ChecklistExtension()]
        log.debug('list of md extensions: (%s)',
                  ', '.join([e if isinstance(e, str) else type(e).__name__
                             for e in exts]))
        log.debug('initializing markdown parser')
        md: Markdown = Markdown(extensions=exts,
                                output_format='html5')
        builder: Builder = Builder(config, env, db, md)
        builder.build()

        db.write()
        sys.exit(0)
