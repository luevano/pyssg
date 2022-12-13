import os
import sys
from datetime import datetime, timezone
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


class Page:
    def __init__(self,
                 name: str,
                 ctime: float,
                 mtime: float,
                 html: str,
                 meta: dict,
                 config: dict,
                 dir_config: dict) -> None:
        log.debug('initializing the page object with name "%s"', name)
        # initial data
        self.name: str = name
        self.ctimestamp: float = ctime
        self.mtimestamp: float = mtime
        self.content: str = html
        self.meta: dict = meta
        # TODO: need to fix this to use the dir_config stuff
        self.config: dict = config
        self.dir_config: dict = dir_config

        # data from self.meta
        self.title: str
        self.author: list[str]
        self.summary: str
        self.lang: str
        self.cdatetime: datetime
        self.mdatetime: datetime
        self.tags: list[tuple[str, str]] = []

        # constructed
        self.url: str
        self.image_url: str
        self.cdate: str
        self.cdate_list: str
        self.cdate_list_sep: str
        self.cdate_rss: str
        self.cdate_sitemap: str

        self.mdate: str
        self.mdate_list: str
        self.mdate_list_sep: str
        self.mdate_rss: str
        self.mdate_sitemap: str

        # later assigned references to next and previous pages
        #   not always assigned (tail ends), and the None helps check it, ignoring
        self.next: Page = None  # type: ignore
        self.previous: Page = None  # type: ignore

        # also from self.meta, but for og metadata
        self.og: dict[str, str] = dict()

    def __lt__(self, other):
        return self.ctimestamp < other.ctimestamp

    def __get_meta(self, var: str, or_else: str | list[str]) -> str | list[str]:
        if var in self.meta:
            log.debug('getting metadata "%s"', var)
            return self.meta[var]
        else:
            log.debug('getting metadata "%s" failed, using optional value "%s"', var, or_else)
            return or_else

    # parses meta from self.meta, for og, it prioritizes,
    #   the actual og meta
    def parse_metadata(self):
        log.debug('parsing metadata for file "%s"', self.name)
        self.title = self.__get_meta('title', [''])[0]
        self.author = list(self.__get_meta('author', ['']))
        self.summary = self.__get_meta('summary', [''])[0]
        self.lang = self.__get_meta('lang', ['en'])[0]

        log.debug('parsing timestamp')
        self.cdatetime = datetime.fromtimestamp(self.ctimestamp,
                                                 tz=timezone.utc)
        # these could be actual function
        cdate = lambda x : self.cdatetime.strftime(self.config['fmt'][x])
        mdate = lambda x : self.mdatetime.strftime(self.config['fmt'][x])

        self.cdate = cdate('date')
        self.cdate_list = cdate('list_date')
        self.cdate_list_sep = cdate('list_sep_date')
        self.cdate_rss = cdate('rss_date')
        self.cdate_sitemap = cdate('sitemap_date')

        if self.mtimestamp != 0.0:
            log.debug('parsing modified timestamp')
            self.mdatetime = datetime.fromtimestamp(self.mtimestamp, tz=timezone.utc)
            self.mdate = mdate('date')
            self.mdate_list = mdate('list_date')
            self.mdate_list_sep = mdate('list_sep_date')
            self.mdate_rss = mdate('rss_date')
            self.mdate_sitemap = mdate('sitemap_date')
        else:
            log.debug('not parsing modified timestamp, hasn\'t been modified')

        if self.dir_config['tags']:
            log.debug('parsing tags')
            tags_only: list[str] = list(self.__get_meta('tags', []))
            if tags_only:
                tags_only.sort()

                for t in tags_only:
                    # need to specify dir_config['url'] as it is a hardcoded tag url
                    self.tags.append((t, f'{self.dir_config["url"]}/tag/@{t}.html'))
            else:
                log.debug('no tags to parse')

        log.debug('parsing url')
        # no need to specify dir_config['url'] as self.name already contains the relative url
        self.url = f'{self.config["url"]["main"]}/{self.name.replace(".md", ".html")}'
        log.debug('final url "%s"', self.url)

        log.debug('parsing image url')
        default_image_url: str = ''
        if 'default_image' in self.config['url']:
            log.debug('"default_image" url found, will use if no "image_url" is found')
            default_image_url = self.config['url']['default_image']

        image_url: str
        image_url = self.__get_meta('image_url', [default_image_url])[0]

        if image_url != '':
            if 'static' in self.config['url']:
                self.image_url = f'{self.config["url"]["static"]}/{image_url}'
            else:
                log.debug('no static url set, using main url, this could cause problems')
                self.image_url = f'{self.config["url"]["main"]}/{image_url}'
            log.debug('final image url "%s"', self.image_url)
        else:
            self.image_url = ''
            log.debug('no image url set for the page, could be because no'
                      ' "image_url" was found in the metadata and/or no '
                      ' "default_image" set in the config file')

        # if contains open graph elements
        # TODO: better handle this part
        # og_e = object graph entry
        og_elements: list[str] = list(self.__get_meta('og', []))
        if og_elements:
            log.debug('parsing og metadata')
            for og_e in og_elements:
                kv: list[str] = og_e.split(',', 1)
                if len(kv) != 2:
                    log.error('invalid og syntax for "%s", needs to be "k, v"', og_e)
                    sys.exit(1)

                k: str = kv[0].strip()
                v: str = kv[1].strip()

                log.debug('og element: ("%s", "%s")', k, v)
                self.og[k] = v

        else:
            log.debug('no tags to parse')