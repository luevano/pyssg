import os
from operator import itemgetter
from markdown import Markdown
from logging import Logger, getLogger

from markdown import Markdown
from yafg import YafgExtension
from markdown_checklist.extension import ChecklistExtension

from .database import Database
from .page import Page

log: Logger = getLogger(__name__)


def _get_md_obj() -> Markdown:
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
                  ChecklistExtension(),
                  'pymdownx.mark',
                  'pymdownx.caret',
                  'pymdownx.tilde']
    log.debug('list of md extensions: (%s)',
              ', '.join([e if isinstance(e, str) else type(e).__name__
                         for e in exts]))
    # for some reason, the definition for output_format doesn't include html5
    #   even though it is listed in the documentation, ignoring
    return Markdown(extensions=exts, output_format='html5')  # type: ignore


# page and file is basically a synonym
class MDParser:
    def __init__(self, files: list[str],
                 config: dict,
                 dir_config: dict,
                 db: Database):
        log.debug('initializing the md parser with %d files', len(files))
        self.files: list[str] = files
        self.config: dict = config
        self.dir_config: dict = dir_config
        self.db: Database = db
        self.md: Markdown = _get_md_obj()

        self.all_files: list[Page] = []
        self.all_tags: list[tuple[str, str]] = []

    def parse_files(self) -> None:
        log.debug('parsing all files')
        for i, f in enumerate(self.files):
            log.debug('parsing file "%s"', f)
            src_file: str = os.path.join(self.dir_config['src'], f)
            log.debug('path "%s"', src_file)
            self.db.update(src_file, remove=f'{self.dir_config["src"]}/')

            log.debug('parsing md into html')
            content: str = self.md.reset().convert(open(src_file).read())
            # ignoring md.Meta type as it is not yet defined (because it is from an extension)
            page: Page = Page(f,
                              self.db.e[f].ctimestamp,
                              self.db.e[f].mtimestamp,
                              content,
                              self.md.Meta,  # type: ignore
                              self.config,
                              self.dir_config)
            page.parse_metadata()

            log.debug('adding to file list')
            self.all_files.append(page)

            if self.dir_config['tags'] and page.tags is not None:
                log.debug('parsing tags for "%s"', f)
                self.db.update_tags(f, list(map(itemgetter(0), page.tags)))

                log.debug('add all tags to tag list')
                for t in page.tags:
                    if t[0] not in list(map(itemgetter(0), self.all_tags)):
                        log.debug('adding tag "%s"', t[0])
                        self.all_tags.append(t)
                    else:
                        log.debug('ignoring tag "%s"; already present', t[0])
            else:
                log.debug('no tags to parse')

        log.debug('sorting all lists for consistency')
        self.all_files.sort(reverse=True)
        self.all_tags.sort(key=itemgetter(0))

        pages_amount: int = len(self.all_files)
        # note that prev and next are switched because of the
        # reverse ordering of all_pages
        log.debug('update next and prev attributes')
        for i, p in enumerate(self.all_files):
            if i != 0:
                next_page: Page = self.all_files[i - 1]
                p.next = next_page

            if i != pages_amount - 1:
                prev_page: Page = self.all_files[i + 1]
                p.previous = prev_page
