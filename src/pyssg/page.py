from datetime import datetime, timezone
from logging import Logger, getLogger
from typing import Any

log: Logger = getLogger(__name__)


class Page:
    def __init__(self, name: str,
                 cts: float,
                 mts: float,
                 html: str,
                 toc: str,
                 toc_tokens: list[str],
                 meta: dict[str, Any],
                 config: dict[str, Any]) -> None:
        # initial data
        self.name: str = name.replace(".md", ".html")
        self.cts: float = cts
        self.mts: float = mts
        self.content: str = html
        self.toc: str = toc
        self.toc_tokens: list[str] = toc_tokens
        self.meta: dict[str, Any] = meta
        self.config: dict[str, Any] = config

        # data from self.meta
        self.title: str
        self.author: list[str]
        self.summary: str
        self.lang: str
        self.tags: tuple[str]

        # constructed
        self.cdate_rss: str
        self.cdate_sitemap: str
        self.mdate_rss: str | None = None
        self.mdate_sitemap: str | None = None

        self.next: Page | None = None
        self.previous: Page | None = None

    def __lt__(self, other):
        return self.ctimestamp < other.ctimestamp

    def __get_meta(self, var: str,
                   or_else: str | list[str] = ['']) -> str | list[str] | Any:
        if var in self.meta:
            return self.meta[var]
        else:
            log.debug('getting metadata "%s" failed, using optional value "%s"',
                      var, or_else)
            return or_else

    # these date/cdate/mdate might be a bit overcomplicated

    def date(self, ts: float, format: str) -> str:
        dt: datetime = datetime.fromtimestamp(ts, tz=timezone.utc)

        if format in self.config['fmt']:
            return dt.strftime(self.config['fmt'][format])
        else:
            log.warning('format "%s" not found in config, returning '
                        'empty string', format)
            return ''

    # parses meta from self.meta
    def parse_metadata(self):
        self.title = str(self.__get_meta('title')[0])
        self.author = list(self.__get_meta('author'))
        self.summary = str(self.__get_meta('summary')[0])
        self.lang = str(self.__get_meta('lang', ['en'])[0])

        # probably add a way to sanitize tags
        self.tags = tuple(set(sorted(self.__get_meta('tags', []))))
        log.debug('parsed tags %s', self.tags)

        self.cdate_rss = self.date(self.cts, 'rss_date')
        self.cdate_sitemap = self.date(self.cts, 'sitemap_date')
        if self.mts != 0.0:
            self.mdate_rss = self.date(self.mts,  'rss_date')
            self.mdate_sitemap = self.date(self.mts, 'sitemap_date')

