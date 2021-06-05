from datetime import datetime, timezone

from .configuration import Configuration


DFORMAT_RSS = '%a, %d %b %Y %H:%M:%S GMT'
DFORMAT_SITEMAP = '%Y-%m-%d'


class Page:
    def __init__(self,
                 name: str,
                 ctime: float,
                 mtime: float,
                 html: str,
                 meta: dict):
        # initial data
        self.name: str = name
        self.ctimestamp: float = ctime
        self.mtimestamp: float = mtime
        self.content: str = html
        self.meta: dict = meta

        # data from self.meta
        self.title: str = ''
        self.author: str = ''
        self.cdatetime: datetime = None
        self.mdatetime: datetime = None
        self.summary: str = ''
        self.lang: str = 'en'
        self.tags: list[tuple[str]] = []

        # constructed
        self.url: str = ''
        self.cdate: str = ''
        self.cdate_list: str = ''
        self.cdate_list_sep: str = ''
        self.cdate_rss: str = ''
        self.cdate_sitemap: str = ''
        self.mdate: str = None
        self.mdate_list: str = None
        self.mdate_list_sep: str = None
        self.mdate_rss: str = ''
        self.mdate_sitemap: str = ''

        # later assigned references to next and previous pages
        self.next: Page = None
        self.previous: Page = None

        # also from self.meta, but for og metadata
        self.og: dict[str, str] = dict()


    def __lt__(self, other):
        return self.ctimestamp < other.ctimestamp


    # parses meta from self.meta, for og, it prioritizes,
    # the actual og meta
    def parse(self, config: Configuration):
        # required meta elements
        self.title = self.meta['title'][0]
        self.author = self.meta['author'][0]
        self.summary = self.meta['summary'][0]
        self.lang = self.meta['lang'][0]

        # dates
        self.cdatetime = datetime.fromtimestamp(self.ctimestamp,
                                                 tz=timezone.utc)
        self.cdate = self.cdatetime.strftime(config.dformat)
        self.cdate_list = self.cdatetime.strftime(config.l_dformat)
        self.cdate_list_sep = self.cdatetime.strftime(config.lsep_dformat)
        self.cdate_rss = self.cdatetime.strftime(DFORMAT_RSS)
        self.cdate_sitemap = self.cdatetime.strftime(DFORMAT_SITEMAP)

        # only if file/page has been modified
        if self.mtimestamp != 0.0:
            self.mdatetime = datetime.fromtimestamp(self.mtimestamp,
                                                     tz=timezone.utc)
            self.mdate = self.mdatetime.strftime(config.dformat)
            self.mdate_list = self.mdatetime.strftime(config.l_dformat)
            self.mdate_list_sep = self.mdatetime.strftime(config.lsep_dformat)
            self.mdate_rss = self.mdatetime.strftime(DFORMAT_RSS)
            self.mdate_sitemap = self.mdatetime.strftime(DFORMAT_SITEMAP)

        # not always contains tags
        try:
            tags_only: list[str] = self.meta['tags']
            tags_only.sort()

            for t in tags_only:
                self.tags.append((t,
                                  f'{config.base_url}/tag/@{t}.html'))
        except KeyError: pass

        self.url = f'{config.base_url}/{self.name.replace(".md", ".html")}'

        # if contains object graph elements
        try:
            # og_e = object graph entry
            for og_e in self.meta['og']:
                kv: str = og_e.split(',', 1)
                if len(kv) != 2:
                    raise Exception('invalid og syntax')

                k: str = kv[0].strip()
                v: str = kv[1].strip()

                self.og[k] = v
        except KeyError: pass
