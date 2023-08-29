import os
from operator import itemgetter
from logging import Logger, getLogger
import sys
from typing import Any

from markdown import Markdown
from yafg import YafgExtension
from pymdvar import VariableExtension
from markdown_checklist.extension import ChecklistExtension
from markdown.extensions.toc import TocExtension

from pyssg.db.database import Database
from pyssg.page import Page
from pyssg.utils import get_file_stats

log: Logger = getLogger(__name__)


# TODO: add configuration testing for extensions config (pymdvar for ex)
def get_md_obj(variables: dict[str, str],
               enable_env: bool) -> Markdown:
    exts: list = ['extra',
                  'meta',
                  'sane_lists',
                  'smarty',
                  'wikilinks',
                  TocExtension(permalink=True,
                               baselevel=2),
                  VariableExtension(variables=variables,
                                    enable_env=enable_env),
                  # stripTitle generates an error when True,
                  # if there is no title attr
                  YafgExtension(stripTitle=False,
                                figureClass='',
                                figcaptionClass='',
                                figureNumbering=False,
                                figureNumberClass='number',
                                figureNumberText='Figure'),
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
        # TODO: actually add extensions support, for now only pymdvar is configured
        self.pymdvar_vars: dict[str, str] = dict()
        self.pymdvar_enable_env: bool = False
        if 'exts' in config and 'pymdvar' in config['exts']:
            pymdvar: dict[str, Any] = config['exts']['pymdvar']
            if 'variables' in pymdvar and type(pymdvar['variables']) == dict:
                self.pymdvar_vars = pymdvar['variables']
            if 'enable_env' in pymdvar and type(pymdvar['enable_env']) == bool:
                self.pymdvar_enable_env = pymdvar['enable_env']
        log.debug('pymdvar_variables: %s', self.pymdvar_vars)
        log.debug('pymdvar_enable_env: %s', self.pymdvar_enable_env)

        self.md: Markdown = get_md_obj(self.pymdvar_vars, self.pymdvar_enable_env)

        self.all_files: list[Page] = []
        self.all_tags: list[str] = []

    def parse_files(self) -> None:
        for i, f in enumerate(self.files):
            log.debug('parsing file "%s"', f)
            path: str = os.path.join(self.dir_config['src'], f)
            content: str = self.md.reset().convert(open(path).read())
            fstats = get_file_stats(path)
            chksm: str = fstats[0]
            time: float = fstats[1]

            entry: tuple
            # old entry
            oentry: tuple | None = self.db.select(f)
            if not oentry:
                entry = self.db.insert(f, time, chksm)
            else:
                oe_chksm: str = oentry[3]
                if chksm != oe_chksm:
                    entry = self.db.update(f, time, chksm)
                else:
                    entry = oentry
            
            # ignoring md.Meta type as it is not yet defined
            #   (because it is from an extension)
            page: Page = Page(f,
                              entry[1],
                              entry[2],
                              content,
                              self.md.toc,  # type: ignore
                              self.md.toc_tokens,  # type: ignore
                              self.md.Meta,  # type: ignore
                              self.config)
            page.parse_metadata()
            self.all_files.append(page)

            if self.dir_config['tags']:
                if entry[4] is not None:
                    if set(page.tags) != set(entry[4]):
                        self.db.update_tags(f, page.tags)

                for t in page.tags:
                    if t not in self.all_tags:
                        self.all_tags.append(t)
                        log.debug('added tag "%s" to all tags', t)

        self.all_files.sort(reverse=True)
        self.all_tags.sort()

        pages_amount: int = len(self.all_files)
        # note that prev and next are switched because of the
        # reverse ordering of all_pages
        for i, p in enumerate(self.all_files):
            if i != 0:
                next_page: Page = self.all_files[i - 1]
                p.next = next_page

            if i != pages_amount - 1:
                prev_page: Page = self.all_files[i + 1]
                p.previous = prev_page
