import os
from jinja2 import Environment, Template
from importlib.metadata import version
from datetime import datetime, timezone

from .page import Page
from .configuration import Configuration


VERSION = version('pyssg')
# specific format for rss
DFORMAT = '%a, %d %b %Y %H:%M:%S GMT'
RUN_DATE = datetime.now(tz=timezone.utc).strftime(DFORMAT)


class RSSBuilder:
    def __init__(self, config: Configuration,
                 env: Environment,
                 pages: list[Page],
                 tags: list[tuple[str]]):
        self.config: Configuration = config
        self.env: Environment = env
        self.pages: list[Page] = pages
        self.tags: list[tuple[str]] = tags


    def build(self):
        template: Template = self.env.get_template("rss.xml")
        content: str = template.render(site_title=self.config.title,
                                       site_base_url=self.config.base_url,
                                       site_base_static_url=self.config.base_static_url,
                                       pyssg_version=VERSION,
                                       run_date=RUN_DATE,
                                       all_pages=self.pages,
                                       all_tags=self.tags)

        with open(os.path.join(self.config.dst, 'rss.xml'), 'w') as f:
            f.write(content)
