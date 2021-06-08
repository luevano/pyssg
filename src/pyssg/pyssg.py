import os
import shutil
from importlib.resources import path
from argparse import ArgumentParser, Namespace
from typing import Union

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
import yafg
from MarkdownHighlight.highlight import HighlightExtension
from markdown_checklist.extension import ChecklistExtension

from .configuration import Configuration
from .database import Database
from .builder import Builder
from .page import Page


def get_options() -> Namespace:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that reads
                            Markdown files and creates HTML files.\nIf
                            [-c]onfig file is provided (or exists in default
                            location) all other options are ignored.\nFor
                            datetime formats see:
                            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes''')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='''print program version''')
    parser.add_argument('-c', '--config',
                        default='$XDG_CONFIG_HOME/pyssg/pyssgrc',
                        type=str,
                        help='''config file (path) to read from; defaults to
                        'pyssgrc' first, then
                        '$XDG_CONFIG_HOME/pyssg/pyssgrc' ''')
    parser.add_argument('-s', '--src',
                        default='src',
                        type=str,
                        help='''src directory; handmade files, templates and
                        metadata directory; defaults to 'src' ''')
    parser.add_argument('-d', '--dst',
                        default='dst',
                        type=str,
                        help='''dst directory; generated (and transfered html)
                        files; defaults to 'dst' ''')
    parser.add_argument('-t', '--plt',
                        default='plt',
                        type=str,
                        help='''plt directory; all template files; defaults to
                        'plt' ''')
    parser.add_argument('-u', '--url',
                        default='',
                        type=str,
                        help='''base url without trailing slash''')
    parser.add_argument('--static-url',
                        default='',
                        type=str,
                        help='''base static url without trailing slash''')
    parser.add_argument('--default-image-url',
                        default='',
                        type=str,
                        help='''default image url''')
    parser.add_argument('--title',
                        default='Blog',
                        type=str,
                        help='''general title for the website; defaults to
                        'Blog' ''')
    parser.add_argument('--date-format',
                        default='%a, %b %d, %Y @ %H:%M %Z',
                        type=str,
                        help='''date format used inside pages (for creation and
                        modification times, for example); defaults to '%%a, %%b
                        %%d, %%Y @ %%H:%%M %%Z' ('Tue, Mar 16, 2021 @ 02:46 UTC',
                        for example)''')
    parser.add_argument('--list-date-format',
                        default='%b %d',
                        type=str,
                        help='''date format used for page entries in a list;
                        defaults to '%%b %%d' ('Mar 16', for example)''')
    parser.add_argument('--list-sep-date-format',
                        default='%B %Y',
                        type=str,
                        help='''date format used for the separator between page
                        entries in a list; defaults to '%%B %%Y' ('March 2021',
                        for example)''')
    parser.add_argument('-i', '--init',
                        action='store_true',
                        help='''initializes the dir structure, templates,
                        as well as the 'src' and 'dst' directories''')
    parser.add_argument('-b', '--build',
                        action='store_true',
                        help='''generates all html files and passes over
                        existing (handmade) ones''')
    parser.add_argument('-f', '--force',
                        action='store_true',
                        help='''force building all pages and not only the
                        updated ones''')

    return parser.parse_args()


def main() -> None:
    opts: dict[str, Union[str, bool]] = vars(get_options())
    conf_path: str = opts['config']
    conf_path = os.path.expandvars(conf_path)


    config: Configuration = None
    if os.path.exists('pyssgrc'):
        config = Configuration('pyssgrc')
    else:
        config = Configuration(conf_path)

    config.read()
    config.fill_missing(opts)

    if opts['version']:
        print(f'pyssg v{config.version}')
        return

    if opts['init']:
        try:
            os.mkdir(config.src)
            os.makedirs(os.path.join(config.dst, 'tag'))
            os.mkdir(config.plt)
        except FileExistsError:
            pass

        # copy basic template files
        files: list[str] = ('index.html',
                            'page.html',
                            'tag.html',
                            'rss.xml',
                            'sitemap.xml')
        for f in files:
            plt_file: str = os.path.join(config.plt, f)
            with path('pyssg.plt', f) as p:
                if not os.path.exists(plt_file):
                    shutil.copy(p, plt_file)

        return

    if opts['build']:
        # start the db
        db: Database = Database(os.path.join(config.src, '.files'))
        db.read()

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
        env: Environment = Environment(loader=FileSystemLoader(config.plt),
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
                      yafg.YafgExtension(stripTitle=True,
                                         figureClass="",
                                         figcaptionClass="",
                                         figureNumbering=False,
                                         figureNumberClass="number",
                                         figureNumberText="Figure"),
                      HighlightExtension,
                      ChecklistExtension()]
        md: Markdown = Markdown(extensions=exts,
                                output_format='html5')
        builder: Builder = Builder(config, env, db, md)
        builder.build()

        db.write()
        return
