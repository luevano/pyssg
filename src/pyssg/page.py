from datetime import datetime, timezone

from .configuration import Configuration


class Page:
    def __init__(self,
                 name: str,
                 ctime: float,
                 mtime: float,
                 html: str,
                 meta: dict,
                 config: Configuration):
        # initial data
        self.name: str = name
        self.ctimestamp: float = ctime
        self.mtimestamp: float = mtime
        self.content: str = html
        self.meta: dict = meta
        self.config: Configuration = config

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
        self.image_url: str = ''
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
    def parse(self):
        # required meta elements
        self.title = self.meta['title'][0]
        self.author = self.meta['author'][0]
        self.summary = self.meta['summary'][0]
        self.lang = self.meta['lang'][0]

        # dates
        self.cdatetime = datetime.fromtimestamp(self.ctimestamp,
                                                 tz=timezone.utc)
        self.cdate = self.cdatetime.strftime(self.config.dformat)
        self.cdate_list = self.cdatetime.strftime(self.config.l_dformat)
        self.cdate_list_sep = self.cdatetime.strftime(self.config.lsep_dformat)
        self.cdate_rss = self.cdatetime.strftime(self.config.dformat_rss)
        self.cdate_sitemap = \
        self.cdatetime.strftime(self.config.dformat_sitemap)

        # only if file/page has been modified
        if self.mtimestamp != 0.0:
            self.mdatetime = datetime.fromtimestamp(self.mtimestamp,
                                                     tz=timezone.utc)
            self.mdate = self.mdatetime.strftime(self.config.dformat)
            self.mdate_list = self.mdatetime.strftime(self.config.l_dformat)
            self.mdate_list_sep = self.mdatetime.strftime(self.config.lsep_dformat)
            self.mdate_rss = self.mdatetime.strftime(self.config.dformat_rss)
            self.mdate_sitemap = \
            self.mdatetime.strftime(self.config.dformat_sitemap)

        # not always contains tags
        try:
            tags_only: list[str] = self.meta['tags']
            tags_only.sort()

            for t in tags_only:
                self.tags.append((t,
                                  f'{self.config.url}/tag/@{t}.html'))
        except KeyError: pass

        self.url = f'{self.config.url}/{self.name.replace(".md", ".html")}'

        try:
            self.image_url = \
            f'{self.config.static_url}/{self.meta["image_url"][0]}'
        except KeyError:
            self.image_url = \
            f'{self.config.static_url}/{self.config.default_image_url}'

        # if contains open graph elements
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
