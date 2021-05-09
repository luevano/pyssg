from datetime import datetime, timezone


class Page:
    def __init__(self,
                 f_name: str,
                 f_time: float,
                 c_html: str,
                 c_meta: dict):
        self.f_name: str = f_name
        self.f_time: float = f_time
        self.c_html: str = c_html
        self.c_meta: dict = c_meta

        self.title: str = None
        self.author: str = None
        self.timestamp: str = None
        self.summary: str = None
        self.lang: str = None
        self.tags: list = None


    def parse_meta(self):
        try:
            self.title = self.c_meta['title'][0]
        except KeyError:
            pass

        try:
            self.author = self.c_meta['author'][0]
        except KeyError:
            pass

        self.timestamp = datetime.fromtimestamp(self.f_time, tz=timezone.utc)

        try:
            self.summary = self.c_meta['summary'][0]
        except KeyError:
            pass

        try:
            self.lang = self.c_meta['lang'][0]
        except KeyError:
            pass

        try:
            self.tags = self.c_meta['tags']
        except KeyError:
            pass
