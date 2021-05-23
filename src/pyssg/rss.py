import os
import importlib.metadata
from datetime import datetime, timezone

from .page import Page
from .configuration import Configuration


VERSION = importlib.metadata.version('pyssg')
DFORMAT = '%a, %d %b %Y %H:%M:%S %Z'


class RSSBuilder:
    def __init__(self, config: Configuration,
                 template: str,
                 pages: list[Page]):
        self.config: Configuration = config
        self.rss: str = template
        self.pages: list[Page] = pages


    def build(self):
        # initial base replacements
        self.rss = self.rss.replace('$$TITLE', self.config.title)
        self.rss = self.rss.replace('$$LINK', self.config.base_url)
        self.rss = self.rss.replace('$$PYSSGVERSION', VERSION)
        items_formatted: str = self.__get_items_formatted()
        self.rss = self.rss.replace('$$ITEMS', items_formatted)

        current_date: str = datetime.now(tz=timezone.utc).strftime(DFORMAT)
        self.rss = self.rss.replace('$$CURRENTDATE', current_date)

        with open(os.path.join(self.config.dst, 'rss.xml'), 'w') as f:
            f.write(self.rss)


    def __get_items_formatted(self) -> str:
        # i_f=items formatted for short
        i_f: str = ''
        for p in pages:
            url: str = f'{self.config.base_url}/{p.name.replace(".md", ".html")}'
            date: str = p.c_datetime.strftime(DFORMAT)

            i_f = f'{i_f}    <item>\n'
            i_f = f'{i_f}      <title>{p.title}</title>\n'
            i_f = f'{i_f}      <link>{url}</link>\n'
            i_f = f'{i_f}      <description>{p.summary}</description>\n'
            i_f = f'{i_f}      <guid isPermaLink="true">{url}</guid>\n'
            i_f = f'{i_f}      <pubDate>{date}</pubDate>\n'
            i_f = f'{i_f}    </item>\n'

        return i_f
