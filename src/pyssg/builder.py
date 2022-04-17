import os
import shutil
from copy import deepcopy
from operator import itemgetter
from jinja2 import Environment, Template
from markdown import Markdown
from configparser import ConfigParser

from .database import Database
from .parser import MDParser
from .page import Page
from .discovery import get_file_list, get_dir_structure


class Builder:
    def __init__(self, config: ConfigParser,
                 env: Environment,
                 db: Database,
                 md: Markdown):
        self.config: ConfigParser = config
        self.env: Environment = env
        self.db: Database = db
        self.md: Markdown = md

        self.dirs: list[str] = None
        self.md_files: list[str] = None
        self.html_files: list[str] = None

        self.all_pages: list[Page] = None
        self.updated_pages: list[Page] = None
        self.all_tags: list[str] = None
        self.common_vars: dict = None


    def build(self) -> None:
        self.dirs = get_dir_structure(self.config.get('path', 'src'),
                                      ['templates'])
        self.md_files = get_file_list(self.config.get('path', 'src'),
                                      ['.md'],
                                      ['templates'])
        self.html_files = get_file_list(self.config.get('path', 'src'),
                                        ['.html'],
                                        ['templates'])

        self.__create_dir_structure()
        self.__copy_html_files()

        parser: MDParser = MDParser(self.md_files,
                                    self.config,
                                    self.db,
                                    self.md)
        parser.parse()

        # just so i don't have to pass these vars to all the functions
        self.all_pages = parser.all_pages
        self.updated_pages = parser.updated_pages
        self.all_tags = parser.all_tags

        # dict for the keyword args to pass to the template renderer
        self.common_vars = dict(config=self.config,
                                all_pages=self.all_pages,
                                all_tags=self.all_tags)

        self.__render_articles()
        self.__render_tags()
        self.__render_template('index.html', 'index.html', **self.common_vars)
        self.__render_template('rss.xml', 'rss.xml', **self.common_vars)
        self.__render_template('sitemap.xml', 'sitemap.xml', **self.common_vars)


    def __create_dir_structure(self) -> None:
        for d in self.dirs:
            # for the dir structure,
            # doesn't matter if the dir already exists
            try:
                os.makedirs(os.path.join(self.config.get('path', 'dst'), d))
            except FileExistsError:
                pass


    def __copy_html_files(self) -> None:
        src_file: str = None
        dst_file: str = None

        for f in self.html_files:
            src_file = os.path.join(self.config.get('path', 'src'), f)
            dst_file = os.path.join(self.config.get('path', 'dst'), f)

            # only copy files if they have been modified (or are new)
            if self.db.update(src_file, remove=f'{self.config.get("path", "src")}/'):
                shutil.copy2(src_file, dst_file)


    def __render_articles(self) -> None:
        article_vars: dict = deepcopy(self.common_vars)
        # check if only updated should be created
        if self.config.getboolean('other', 'force'):
            for p in self.all_pages:
                article_vars['page'] = p
                self.__render_template("page.html",
                                       p.name.replace('.md','.html'),
                                       **article_vars)
        else:
            for p in self.updated_pages:
                article_vars['page'] = p
                self.__render_template("page.html",
                                       p.name.replace('.md','.html'),
                                       **article_vars)


    def __render_tags(self) -> None:
        tag_vars: dict = deepcopy(self.common_vars)
        for t in self.all_tags:
            # get a list of all pages that have current tag
            tag_pages: list[Page] = []
            for p in self.all_pages:
                if p.tags is not None and t[0] in list(map(itemgetter(0),
                                                           p.tags)):
                    tag_pages.append(p)

            tag_vars['tag'] = t
            tag_vars['tag_pages'] = tag_pages

            # build tag page
            self.__render_template('tag.html',
                                   f'tag/@{t[0]}.html',
                                   **tag_vars)

            # clean list of pages with current tag
            tag_pages = []


    def __render_template(self, template_name: str,
                          file_name: str,
                          **template_vars) -> None:
        template: Template = self.env.get_template(template_name)
        content: str = template.render(**template_vars)

        with open(os.path.join(self.config.get('path', 'dst'), file_name), 'w') as f:
            f.write(content)
