import os
import shutil
from operator import itemgetter
from copy import deepcopy
from jinja2 import Environment, Template
from markdown import Markdown
from importlib.metadata import version
from datetime import datetime, timezone

from .configuration import Configuration
from .database import Database
from .parser import MDParser
from .page import Page
from .discovery import get_file_list, get_dir_structure


VERSION = version('pyssg')
# specific format for rss
DFORMAT = '%a, %d %b %Y %H:%M:%S GMT'
RUN_DATE = datetime.now(tz=timezone.utc).strftime(DFORMAT)


class HTMLBuilder:
    def __init__(self, config: Configuration,
                 env: Environment,
                 db: Database,
                 md: Markdown):
        self.src: str = config.src
        self.dst: str = config.dst
        self.title: str = config.title
        self.base_url: str = config.base_url
        self.base_static_url: str = config.base_static_url
        self.force: bool = config.force

        self.config: Configuration = config
        self.env: Environment = env
        self.db: Database = db
        self.md: Markdown = md

        self.dirs: list[str] = None
        self.md_files: list[str] = None
        self.html_files: list[str] = None

        self.all_pages: list[Page] = None
        self.updated_pages: list[Page] = None
        self.all_tags: list[str] = None


    def build(self) -> None:
        self.dirs = get_dir_structure(self.src, ['templates'])
        self.md_files = get_file_list(self.src, ['.md'], ['templates'])
        self.html_files = get_file_list(self.src, ['.html'], ['templates'])

        self.__create_dir_structure()
        self.__copy_html_files()

        parser: MDParser = MDParser(self.src,
                                    self.md_files,
                                    self.db,
                                    self.md)
        parser.parse(self.config)

        # just to be able to extract all pages out of this class
        self.all_pages = parser.all_pages
        self.updated_pages = parser.updated_pages
        self.all_tags = parser.all_tags

        # create the article index
        self.__create_article_index()
        # check if all pages should be created
        self.__create_articles()
        self.__create_tags()


    def __create_dir_structure(self) -> None:
        for d in self.dirs:
            # for the dir structure,
            # doesn't matter if the dir already exists
            try:
                os.makedirs(os.path.join(self.dst, d))
            except FileExistsError:
                pass


    def __copy_html_files(self) -> None:
        src_file: str = None
        dst_file: str = None

        for f in self.html_files:
            src_file = os.path.join(self.src, f)
            dst_file = os.path.join(self.dst, f)

            # only copy files if they have been modified (or are new)
            if self.db.update(src_file, remove=f'{self.src}/'):
                shutil.copy2(src_file, dst_file)


    def __create_article_index(self) -> None:
        template: Template = self.env.get_template("index.html")
        content: str = template.render(site_title=self.title,
                                       site_base_url=self.base_url,
                                       site_base_static_url=self.base_static_url,
                                       pyssg_version=VERSION,
                                       run_date=RUN_DATE,
                                       all_pages=self.all_pages,
                                       all_tags=self.all_tags)

        with open(os.path.join(self.dst, 'index.html'), 'w') as f:
            f.write(content)


    def __create_articles(self) -> None:
        # check if only updated should be created
        if self.force:
            for p in self.all_pages:
                self.__create_article(p)
        else:
            for p in self.updated_pages:
                self.__create_article(p)


    def __create_article(self, page: Page) -> None:
        # prepare html file name
        f_name: str = page.name
        f_name = f_name.replace('.md', '.html')

        template: Template = self.env.get_template("page.html")
        content: str = template.render(site_title=self.title,
                                       site_base_url=self.base_url,
                                       site_base_static_url=self.base_static_url,
                                       pyssg_version=VERSION,
                                       run_date=RUN_DATE,
                                       all_pages=self.all_pages,
                                       all_tags=self.all_tags,
                                       page=page)


        with open(os.path.join(self.dst, f_name), 'w') as f:
            f.write(content)


    def __create_tags(self) -> None:
        for t in self.all_tags:
            # get a list of all pages that have current tag
            tag_pages: list[Page] = []
            for p in self.all_pages:
                if p.tags is not None and t[0] in list(map(itemgetter(0),
                                                           p.tags)):
                    tag_pages.append(p)

            # build tag page
            self.__create_tag(t, tag_pages)

            # clean list of pages with current tag
            tag_pages = []


    def __create_tag(self, tag: tuple[str],
                     pages: list[Page]) -> None:

        template: Template = self.env.get_template("tag.html")
        content: str = template.render(site_title=self.title,
                                       site_base_url=self.base_url,
                                       site_base_static_url=self.base_static_url,
                                       pyssg_version=VERSION,
                                       run_date=RUN_DATE,
                                       all_pages=self.all_pages,
                                       all_tags=self.all_tags,
                                       tag=tag,
                                       tag_pages=pages)

        with open(os.path.join(self.dst, f'tag/@{tag[0]}.html'), 'w') as f:
            f.write(content)
