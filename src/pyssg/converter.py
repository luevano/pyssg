import os
from markdown import Markdown
from copy import deepcopy
from .page import Page
from .template import Template


def get_pages(src: str, files: list[str]) -> list[Page]:
    md: Markdown = Markdown(extensions=['extra', 'meta', 'sane_lists',
                                        'smarty', 'toc', 'wikilinks'],
                            output_format='html5')

    pages: list[Page] = []

    for f in files:
        f_name = os.path.join(src, f)

        content = md.reset().convert(open(f_name).read())
        f_time = os.stat(f_name).st_mtime

        pages.append(Page(f_name, f_time, content, md.Meta))

    return pages


def create_html_files(src: str, dst: str, files: list[str]) -> None:
    # get the list of page objects
    pages: list[Page] = get_pages(src, files)

    # read all templates into a template obj
    template: Template = Template()
    template.read_templates(src)
    for p in pages:
        # t=template, p=page
        t: Template = deepcopy(template)
        p.parse_meta()

        # common
        t.header = t.header.replace("$$LANG", p.lang)
        t.header = t.header.replace('$$TITLE', p.title)
        t.header = t.header.replace('$$EXTRAHEAD', f'''
    <!-- example extra head -->
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{p.title}">
    <meta property="og:description" content="{p.summary}">''')

        # article entry
        t.article.header = t.article.header.replace('$$TITLE', p.title)

        print(t.header)
        print(t.article.header)
        print(p.c_html)
        print(t.tags.list_header, sep='')
        for tag in p.tags:
            tag_entry = t.tags.list_entry
            tag_entry = tag_entry.replace('$$NAME', tag)
            tag_entry = tag_entry.replace('$$URL', p.f_name)
            print(tag_entry, sep='')
            print(t.tags.list_separator, sep='')
        print(t.tags.list_footer)
        print(t.article.footer)
        print(t.footer)
