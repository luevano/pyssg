import os
import sys
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


def main() -> None:
    args: dict[str, Union[str, bool]] = vars(get_parsed_arguments())
    if not len(sys.argv) > 1:
        print(f'pyssg v{VERSION} - no arguments passed, --help for more')
        sys.exit(0)

    if args['version']:
        print(f'pyssg v{VERSION}')
        sys.exit(0)

    config_path: str = args['config'] if args['config'] else DEFAULT_CONFIG_PATH
    config_path = os.path.normpath(os.path.expandvars(config_path))
    sanity_check_path(config_path)
    config_dir, _ = os.path.split(config_path)

    if args['copy_default_config']:
        create_dir(config_dir)
        with rpath('pyssg.plt', 'default.ini') as p:
            copy_file(p, config_path)
        sys.exit(0)

    if not os.path.exists(config_path):
        print(f'''config file does't exist in path "{config_path}"; make sure
                  the path is correct; use --copy-default-config to if you
                  haven't already''')
        sys.exit(1)

    config: ConfigParser = get_parsed_config(config_path)

    if args['init']:
        create_dir(config.get('path', 'src'))
        create_dir(os.path.join(config.get('path', 'dst'), 'tag'), True)
        create_dir(config.get('path', 'plt'))
        files: list[str] = ('index.html',
                            'page.html',
                            'tag.html',
                            'rss.xml',
                            'sitemap.xml')
        for f in files:
            plt_file: str = os.path.join(config.get('path', 'plt'), f)
            with rpath('pyssg.plt', f) as p:
                copy_file(p, plt_file)
        sys.exit(0)

    if args['build']:
        # start the db
        db: Database = Database(os.path.join(config.get('path', 'src'), '.files'))
        db.read()

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
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
        md: Markdown = Markdown(extensions=exts,
                                output_format='html5')
        builder: Builder = Builder(config, env, db, md)
        builder.build()

        db.write()
        sys.exit(0)
