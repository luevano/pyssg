import os
from datetime import datetime, timezone

from .page import Page
from .configuration import Configuration


DFORMAT = '%Y-%m-%d'


class SitemapBuilder:
    def __init__(self, config: Configuration,
                 template: str,
                 pages: list[Page],
                 tags: list[str]):
        self.config: Configuration = config
        self.sitemap: str = template
        self.pages: list[Page] = pages
        self.tags: list[str] = tags


    def build(self):
        # initial base replacements
        urls_formatted: str = self.__get_urls_formatted()
        self.sitemap = self.sitemap.replace('$$URLS', urls_formatted)


        with open(os.path.join(self.config.dst, 'sitemap.xml'), 'w') as f:
            f.write(self.sitemap)


    def __get_urls_formatted(self) -> str:
        # u_f=items formatted for short
        u_f: str = ''
        for p in self.pages:
            url: str = f'{self.config.base_url}/{p.name.replace(".md", ".html")}'
            date: str = p.m_datetime.strftime(DFORMAT)

            u_f = f'{u_f}    <url>\n'
            u_f = f'{u_f}      <loc>{url}</loc>\n'
            u_f = f'{u_f}      <lastmod>{date}</lastmod>\n'
            u_f = f'{u_f}      <changefreq>weekly</changefreq>\n'
            u_f = f'{u_f}      <priority>1.0</priority>\n'
            u_f = f'{u_f}    </url>\n'

        for t in self.tags:
            url: str = f'{self.config.base_url}/tag/@{t}.html'
            date: str = datetime.now(tz=timezone.utc).strftime(DFORMAT)

            u_f = f'{u_f}    <url>\n'
            u_f = f'{u_f}      <loc>{url}</loc>\n'
            u_f = f'{u_f}      <lastmod>{date}</lastmod>\n'
            u_f = f'{u_f}      <changefreq>daily</changefreq>\n'
            u_f = f'{u_f}      <priority>0.5</priority>\n'
            u_f = f'{u_f}    </url>\n'

        return u_f
