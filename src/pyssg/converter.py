import os
from datetime import datetime
from markdown import Markdown
from copy import deepcopy

from .database import Database
from .template import Template
from .page import Page


def get_pages(src: str,
              files: list[str],
              db: Database) -> (list[Page], list[Page]):
    md: Markdown = Markdown(extensions=['extra', 'meta', 'sane_lists',
                                        'smarty', 'toc', 'wikilinks'],
                            output_format='html5')

    all_pages: list[Page] = []
    updated_pages: list[Page] = []
    for f in files:
        src_file: str = os.path.join(src, f)
        # get flag if update is successful
        updated: bool = db.update(src_file, remove=f'{src}/')

        page: Page = None
        content: str = md.reset().convert(open(src_file).read())
        page = Page(f, db.e[f][0], db.e[f][1], content, md.Meta)

        if updated:
            updated_pages.append(page)
        all_pages.append(page)

        # add its tag to corresponding entry if existent
        if page.tags is not None:
            db.update_tags(f, page.tags)


    return (all_pages, updated_pages)


def create_articles(dst: str,
                    pages: list[Page],
                    template: Template) -> None:
    # TODO: clean this mess
    # TODO: proper creation of html files
    for p in pages:
        create_article(dst, p, template)


def create_article(dst: str,
                   page: Page,
                   template: Template) -> None:
    # TODO: clean this mess
    # make temporary template
    t: Template = deepcopy(template)
    # TODO: make this configurable
    base_url: str = 'https://blog.luevano.xyz/'

    f_name: str = page.name
    f_name = f_name.replace('.md', '.html')
    f_name = f_name.replace('.markdown', '.html')

    with open(os.path.join(dst, f_name), 'w') as f:
        # common
        t.header = t.header.replace("$$LANG",
                                    page.lang if page.lang is not None else 'en')
        t.header = t.header.replace('$$TITLE', page.title)
        t.header = t.header.replace('$$EXTRAHEAD', '')

        # article header
        t.article.header = t.article.header.replace('$$TITLE', page.title)

        # Actually write to the html file
        f.write(t.header)
        f.write(t.article.header)
        f.write(page.html)

        if page.tags is not None:
            tag_amount: int = len(page.tags)

            f.write(t.tags.list_header)
            for i, tag in enumerate(page.tags):
                t_entry: str = t.tags.list_entry
                t_entry = t_entry.replace('$$URL', f'{base_url}tag/@{tag}.html')
                t_entry = t_entry.replace('$$NAME', tag)

                f.write(t_entry)
                # don't write last separator, not needed
                if i != tag_amount - 1:
                    f.write(t.tags.list_separator)
            f.write(t.tags.list_footer)

        f.write(t.article.footer)
        f.write(t.footer)


def get_all_tags(pages: list[Page]) -> list[str]:
    tags: list[str] = []
    for p in pages:
        if p.tags is not None:
            for t in p.tags:
                if t not in tags:
                    tags.append(t)
    tags.sort()

    return tags


def create_tags(dst: str,
                tags: list[str],
                pages: list[Page],
                template: Template) -> None:
    for t in tags:
        # get a list of all pages that have current tag
        # and sort them (by time)
        tag_pages: list[Page] = []
        for p in pages:
            if p.tags is not None and t in p.tags:
                tag_pages.append(p)
        tag_pages.sort(reverse=True)

        # build tag page
        create_tag(dst, t, tag_pages, template)

        # clean list of pages with current tag
        tag_pages = []


def create_tag(dst: str,
               tag: str,
               pages: list[Page],
               template: Template) -> None:
    # TODO: clean this mess
    # make temporary template
    t: Template = deepcopy(template)
    # TODO: make this configurable
    base_url: str = 'https://blog.luevano.xyz/'

    with open(os.path.join(dst, f'tag/@{tag}.html'), 'w') as f:
        # common
        t.header = t.header.replace("$$LANG", 'en')
        t.header = t.header.replace('$$TITLE', f'Posts filtered by tag "{tag}"')
        t.header = t.header.replace('$$EXTRAHEAD', '')

        # tag header
        t.tags.header = t.tags.header.replace('$$NAME', tag)
        t.tags.header = t.tags.header.replace('$$URL',
                                              f'{base_url}tag/@{tag}.html')

        # Actually write to the html file
        f.write(t.header)
        f.write(t.tags.header)
        f.write(t.articles.list_header)

        month_year: str = '-'
        for p in pages:
            c_month_year: str = p.c_datetime.strftime('%B %Y')
            if c_month_year != month_year:
                month_year = c_month_year

                month_sep: str = t.articles.list_separator
                month_sep = month_sep.replace('$$SEP', month_year)

                f.write(month_sep)

            f_name: str = p.name
            f_name = f_name.replace('.md', '.html')
            f_name = f_name.replace('.markdown', '.html')

            page_entry: str = t.articles.list_entry
            page_entry = page_entry.replace('$$URL', f'{base_url}{f_name}')
            page_entry = page_entry.replace('$$DATE',
                                            p.c_datetime.strftime('%b %d'))
            page_entry = page_entry.replace('$$TITLE', p.title)

            f.write(page_entry)

        f.write(t.articles.list_footer)
        f.write(t.tags.footer)
        f.write(t.footer)


def create_article_index(dst: str,
                         tags: list[str],
                         pages: list[Page]) -> None:
    # TODO: actually make this function
    pass


def create_html_files(src: str,
                      dst: str,
                      files: list[str],
                      db: Database) -> None:
    # get the list of page objects
    all_pages, updated_pages = get_pages(src, files, db)

    # get all tags
    all_tags = get_all_tags(all_pages)

    # read all templates into a template obj
    template: Template = Template(src)
    template.read()

    # create each category of html pages
    create_articles(dst, updated_pages, template)
    create_tags(dst, all_tags, all_pages, template)

    # create the article index
    create_article_index(dst, all_tags, all_pages)
