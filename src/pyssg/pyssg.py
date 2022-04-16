import os
import shutil
from importlib.resources import path
from typing import Union

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from yafg import YafgExtension
from MarkdownHighlight.highlight import HighlightExtension
from markdown_checklist.extension import ChecklistExtension

from .arg_parser import get_parsed_arguments
from .configuration import Configuration
from .database import Database
from .builder import Builder


def main() -> None:
    opts: dict[str, Union[str, bool]] = vars(get_parsed_arguments())
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
        return
