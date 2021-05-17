import os
from datetime import datetime
from markdown import Markdown

from .database import Database
from .page import Page


# parser of md files, stores list of pages and tags
class MDParser:
    def __init__(self, src: str,
                 files: list[str],
                 db: Database):
        self.md: Markdown = Markdown(extensions=['extra', 'meta', 'sane_lists',
                                                 'smarty', 'toc', 'wikilinks'],
                                     output_format='html5')
        self.src: str = src
        self.files: list[str] = files
        self.db: Database = db

        self.all_pages: list[Page] = None
        self.updated_pages: list[Page] = None
        self.all_tags: list[str] = None


    def parse(self):
        # initialize lists
        self.all_pages = []
        self.updated_pages = []
        self.all_tags = []

        for f in self.files:
            src_file: str = os.path.join(self.src, f)
            # get flag if update is successful
            updated: bool = self.db.update(src_file, remove=f'{self.src}/')

            page: Page = None
            content: str = self.md.reset().convert(open(src_file).read())
            page = Page(f, self.db.e[f][0], self.db.e[f][1], content, self.md.Meta)

            # keep a separated list for all and updated pages
            if updated:
                self.updated_pages.append(page)
            self.all_pages.append(page)

            # parse tags
            if page.tags is not None:
                # add its tag to corresponding db entry if existent
                self.db.update_tags(f, page.tags)

                # update all_tags attribute
                for t in page.tags:
                    if t not in self.all_tags:
                        self.all_tags.append(t)

        # sort list of tags for consistency
        self.all_tags.sort()
        self.updated_pages.sort(reverse=True)
        self.all_pages.sort(reverse=True)
