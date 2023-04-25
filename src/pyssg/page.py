from datetime import datetime, timezone
from logging import Logger, getLogger
from typing import Any

log: Logger = getLogger(__name__)


class Page:
    def __init__(self, name: str,
                       ctime: float,
                       mtime: float,
                       html: str,
                       toc: str,
                       toc_tokens: list[str],
                       meta: dict[str, Any],
                       config: dict[str, Any],
                       dir_config: dict[str, Any]) -> None:
        log.debug('initializing a page object with name "%s"', name)
        # initial data
        self.name: str = name
        self.ctimestamp: float = ctime
        self.mtimestamp: float = mtime
        self.content: str = html
        self.toc: str = toc
        self.toc_tokens: list[str] = toc_tokens
        self.meta: dict[str, Any] = meta
        self.config: dict[str, Any] = config
        self.dir_config: dict[str, Any] = dir_config

        # data from self.meta
        self.title: str
        self.author: list[str]
        self.summary: str
        self.lang: str
        self.cdatetime: datetime
        self.mdatetime: datetime | None = None
        self.tags: list[tuple[str, str]] = []

        # constructed
        self.url: str
        self.image_url: str
        self.cdate_rss: str
        self.cdate_sitemap: str
        self.mdate_rss: str | None = None
        self.mdate_sitemap: str | None = None

        self.next: Page | None = None
        self.previous: Page | None = None

    def __lt__(self, other):
        return self.ctimestamp < other.ctimestamp

    def __get_meta(self, var: str,
                   or_else: str | list[str] = '') -> str | list[str] | Any:
        if var in self.meta:
            log.debug('getting metadata "%s"', var)
            return self.meta[var]
        else:
            log.debug('getting metadata "%s" failed, using optional value "%s"',
                      var, or_else)
            return or_else

    def cdate(self, format: str) -> str:
        if format in self.config['fmt']:
            return self.cdatetime.strftime(self.config['fmt'][format])
        else:
            log.warning('format "%s" not found in config, returning '
                        'empty string', format)
            return ''

    def mdate(self, format: str) -> str:
        if self.mdatetime is None:
            log.warning('no mdatetime found, can\'t return a formatted string')
            return ''
        if format in self.config['fmt']:
            return self.mdatetime.strftime(self.config['fmt'][format])
        else:
            log.warning('format "%s" not found in config, returning '
                        'empty string', format)
            return ''

    def from_timestamp(self, timestamp: float) -> datetime:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # parses meta from self.meta, for og, it prioritizes,
    #   the actual og meta
    def parse_metadata(self):
        log.debug('parsing metadata for file "%s"', self.name)
        self.title = str(self.__get_meta('title'))
        self.author = list(self.__get_meta('author', ['']))
        self.summary = str(self.__get_meta('summary'))
        self.lang = str(self.__get_meta('lang', 'en'))

        log.debug('parsing timestamp')
        self.cdatetime = self.from_timestamp(self.ctimestamp)
        self.cdate_rss = self.cdate('rss_date')
        self.cdate_sitemap = self.cdate('sitemap_date')

        if self.mtimestamp != 0.0:
            log.debug('parsing modified timestamp')
            self.mdatetime = self.from_timestamp(self.mtimestamp)
            self.mdate_rss = self.mdate('rss_date')
            self.mdate_sitemap = self.mdate('sitemap_date')
        else:
            log.debug('not parsing modified timestamp, hasn\'t been modified')

        if self.dir_config['tags']:
            log.debug('parsing tags')
            tags_only: list[str] = list(self.__get_meta('tags', []))
            if tags_only:
                tags_only.sort()

                for t in tags_only:
                    # need to specify dir_config['url'] as it is
                    #   a hardcoded tag url
                    tag_url: str = f'{self.dir_config["url"]}/tag/@{t}.html'
                    self.tags.append((t, tag_url))
            else:
                log.debug('no tags to parse')

        log.debug('parsing page url')
        # no need to specify dir_config['url'] as self.name already
        #   contains the relative url
        name_html: str = self.name.replace(".md", ".html")
        self.url = f'{self.config["url"]["main"]}/{name_html}'
        log.debug('final url "%s"', self.url)

        log.debug('parsing image url')
        default_image_url: str = ''
        if 'default_image' in self.config['url']:
            log.debug('"default_image" url found, will use if no "image_url" '
                      'is found')
            default_image_url = self.config['url']['default_image']

        image_url: str
        image_url = str(self.__get_meta('image_url', default_image_url))

        if image_url != '':
            if 'static' in self.config['url']:
                self.image_url = f'{self.config["url"]["static"]}/{image_url}'
            else:
                log.debug('no static url set, using main url')
                self.image_url = f'{self.config["url"]["main"]}/{image_url}'
            log.debug('final image url "%s"', self.image_url)
        else:
            self.image_url = ''
            log.debug('no image url set for the page, could be because no'
                      ' "image_url" was found in the metadata and/or no '
                      ' "default_image" set in the config file')
