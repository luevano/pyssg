import os
import shutil
from copy import deepcopy

from .template import Template
from .database import Database
from .parser import MDParser
from .page import Page
from .discovery import get_file_list, get_dir_structure

class HTMLBuilder:
    def __init__(self, src: str,
                 dst: str,
                 base_url: str,
                 template: Template,
                 db: Database,
                 dformat: str=None,
                 l_dformat: str=None,
                 lsep_dformat: str=None):
        self.src: str = src
        self.dst: str = dst
        self.base_url: str = base_url
        self.template: Template = template
        self.db: Database = db
        self.dformat: str = None
        self.l_dformat: str = None
        self.lsep_dformat: str = None

        if dformat is not None:
            self.dformat = dformat
        else:
            self.dformat = "%a, %d %b, %Y @ %H:%M %Z"

        if l_dformat is not None:
            self.l_dformat = l_dformat
        else:
            self.l_dformat = "%b %d"

        if lsep_dformat is not None:
            self.lsep_dformat = lsep_dformat
        else:
            self.lsep_dformat = "%B %Y"

        self.dirs: list[str] = None
        self.md_files: list[str] = None
        self.html_files: list[str] = None


    def build(self) -> None:
        self.dirs = get_dir_structure(self.src, ['templates'])
        self.md_files = get_file_list(self.src, ['.md'], ['templates'])
        self.html_files = get_file_list(self.src, ['.html'], ['templates'])

        self.__create_dir_structure()
        self.__copy_html_files()

        parser: MDParser = MDParser(self.src, self.md_files, self.db)
        parser.parse()

        # create the article index
        self.__create_article_index(parser.all_tags, parser.all_pages)

        # create each category of html pages
        self.__create_articles(parser.updated_pages)
        self.__create_tags(parser.all_tags, parser.all_pages)


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


    # this is really similar to create_tag (singular)
    def __create_article_index(self, tags: list[str],
                               pages: list[Page]) -> None:
        # make temporary template
        t: Template = deepcopy(self.template)

        # do basic replacements
        # get page and tag list formated, both functions do replacements
        p_list: list[str] = self.__get_pages_formatted(pages, t)
        t_list: list[str] = self.__get_tags_formatted(tags, t)
        # common
        t.header = t.header.replace("$$LANG", 'en')
        t.header = t.header.replace('$$TITLE', f'Index')

        with open(os.path.join(self.dst, 'index.html'), 'w') as f:
            f.write(t.header)
            f.write(t.articles.header)

            f.write(t.tags.list_header)
            for tag in t_list:
                f.write(tag)
            f.write(t.tags.list_footer)

            f.write(t.articles.list_header)
            for page in p_list:
                f.write(page)
            f.write(t.articles.list_footer)

            f.write(t.articles.footer)
            f.write(t.footer)


    def __create_articles(self, pages: list[Page]) -> None:
        for p in pages:
            self.__create_article(p)


    def __create_article(self, page: Page) -> None:
        # TODO: create better solution for replace
        # make temporary template
        t: Template = deepcopy(self.template)

        # prepare html file name
        f_name: str = page.name
        f_name = f_name.replace('.md', '.html')

        # get timestamps
        c_date: str = page.c_datetime.strftime(self.dformat)
        m_date: str = None
        if page.m_datetime is not None:
            m_date: str = page.m_datetime.strftime(self.dformat)

        # do basic replacements
        # get tag list formatted (some replacements done inside
        # get_tags_formatted)
        t_list: list[str] = None
        if page.tags is not None:
            t_list = self.__get_tags_formatted(page.tags, t)

        # common
        t.header = t.header.replace("$$LANG", page.lang)
        t.header = t.header.replace('$$TITLE', page.title)

        # article header
        t.article.header = t.article.header.replace('$$TITLE', page.title)
        t.article.header = t.article.header.replace('$$AUTHOR', page.author)
        t.article.header = t.article.header.replace('$$CTIME', c_date)
        if m_date is not None:
            t.article.header = t.article.header.replace('$$MTIME', m_date)
        else:
            t.article.header = t.article.header.replace('$$MTIME', '')

        # article footer (same replaces as header)
        t.article.footer = t.article.footer.replace('$$TITLE', page.title)
        t.article.footer = t.article.footer.replace('$$AUTHOR', page.author)
        t.article.footer = t.article.footer.replace('$$CTIME', c_date)
        if m_date is not None:
            t.article.footer = t.article.footer.replace('$$MTIME', m_date)
        else:
            t.article.footer = t.article.footer.replace('$$MTIME', '')


        with open(os.path.join(self.dst, f_name), 'w') as f:
            f.write(t.header)
            f.write(t.article.header)
            f.write(page.html)

            if t_list is not None:
                f.write(t.tags.list_header)
                for tag in t_list:
                    f.write(tag)
                f.write(t.tags.list_footer)

            f.write(t.article.footer)
            f.write(t.footer)


    def __get_tags_formatted(self, tags: list[str],
                             template: Template) -> list[str]:
        tag_amount: int = len(tags)
        tags_formatted: list[str] = []
        for i, t in enumerate(tags):
            # t_e=tag entry
            t_e: str = template.tags.list_entry
            t_e = t_e.replace('$$URL',
                              f'{self.base_url}/tag/@{t}.html')
            t_e = t_e.replace('$$NAME', t)

            tags_formatted.append(t_e)
            if i != tag_amount - 1:
                tags_formatted.append(template.tags.list_separator)

        return tags_formatted


    def __create_tags(self, tags: list[str],
                      pages: list[Page]) -> None:
        for t in tags:
            # get a list of all pages that have current tag
            # and sort them (by time)
            tag_pages: list[Page] = []
            for p in pages:
                if p.tags is not None and t in p.tags:
                    tag_pages.append(p)
            tag_pages.sort(reverse=True)

            # build tag page
            self.__create_tag(t, tag_pages)

            # clean list of pages with current tag
            tag_pages = []


    def __create_tag(self, tag: str,
                     pages: list[Page]) -> None:
        # TODO: create better solution for replace
        # make temporary template
        t: Template = deepcopy(self.template)

        # do basic replacements
        # get page list formated (some replacements done inside
        # get_pages_formatted)
        p_list: list[str] = self.__get_pages_formatted(pages, t)
        # common
        t.header = t.header.replace("$$LANG", 'en')
        t.header = t.header.replace('$$TITLE', f'Posts filtered by: {tag}')

        # tag header
        tag_url: str = f'{self.base_url}/tag/@{tag}.html'
        t.tags.header = t.tags.header.replace('$$NAME', tag)
        t.tags.header = t.tags.header.replace('$$URL', tag_url)

        with open(os.path.join(self.dst, f'tag/@{tag}.html'), 'w') as f:
            f.write(t.header)
            f.write(t.tags.header)

            f.write(t.articles.list_header)
            for p in p_list:
                f.write(p)
            f.write(t.articles.list_footer)

            f.write(t.tags.footer)
            f.write(t.footer)


    def __get_pages_formatted(self, pages: list[Page],
                              template: Template) -> list[str]:
        month_year: str = '-'
        pages_formatted: list[str] = []
        for p in pages:
            # check if the monthly separator should be included
            c_month_year: str = p.c_datetime.strftime(self.lsep_dformat)
            if c_month_year != month_year:
                month_year = c_month_year

                month_sep: str = template.articles.list_separator
                month_sep = month_sep.replace('$$SEP', month_year)

                pages_formatted.append(month_sep)

            f_name: str = p.name
            f_name = f_name.replace('.md', '.html')

            # p_e=page entry
            p_e: str = template.articles.list_entry
            p_e = p_e.replace('$$URL', f'{self.base_url}/{f_name}')
            p_e = p_e.replace('$$DATE', p.c_datetime.strftime(self.l_dformat))
            p_e = p_e.replace('$$TITLE', p.title)

            pages_formatted.append(p_e)

        return pages_formatted
