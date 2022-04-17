import os
from operator import itemgetter
from markdown import Markdown
from configparser import ConfigParser

from .database import Database
from .page import Page


# parser of md files, stores list of pages and tags
class MDParser:
    def __init__(self, files: list[str],
                 config: ConfigParser,
                 db: Database,
                 md: Markdown):
        self.files: list[str] = files

        self.config: ConfigParser = config
        self.db: Database = db
        self.md: Markdown = md

        self.all_pages: list[Page] = None
        self.updated_pages: list[Page] = None
        self.all_tags: list[tuple[str]] = None


    def parse(self) -> None:
        # initialize lists
        self.all_pages = []
        self.updated_pages = []
        self.all_tags = []
        # not used, not sure why i had this
        # all_tag_names: list[str] = []

        for f in self.files:
            src_file: str = os.path.join(self.config.get('path', 'src'), f)
            # get flag if update is successful
            updated: bool = self.db.update(src_file, remove=f'{self.config.get("path", "src")}/')

            content: str = self.md.reset().convert(open(src_file).read())
            page: Page = Page(f,
                              self.db.e[f][0],
                              self.db.e[f][1],
                              content,
                              self.md.Meta,
                              self.config)
            page.parse()

            # keep a separated list for all and updated pages
            if updated:
                self.updated_pages.append(page)
            self.all_pages.append(page)

            # parse tags
            if page.tags is not None:
                # add its tag to corresponding db entry if existent
                self.db.update_tags(f, list(map(itemgetter(0), page.tags)))

                # update all_tags attribute
                for t in page.tags:
                    if t[0] not in list(map(itemgetter(0), self.all_tags)):
                        self.all_tags.append(t)

        # sort list of tags for consistency
        self.all_tags.sort(key=itemgetter(0))
        self.updated_pages.sort(reverse=True)
        self.all_pages.sort(reverse=True)

        pages_amount: int = len(self.all_pages)
        # note that prev and next are switched because of the reverse rodering
        # of all_pages
        for i, p in enumerate(self.all_pages):
            if i != 0:
                next_page: Page = self.all_pages[i - 1]
                p.next = next_page

            if i != pages_amount - 1:
                prev_page: Page = self.all_pages[i + 1]
                p.previous = prev_page
