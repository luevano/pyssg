from datetime import datetime, timezone


class Page:
    def __init__(self,
                 name: str,
                 c_time: float,
                 m_time: float,
                 html: str,
                 meta: dict):
        self.name: str = name
        self.c_time: float = c_time
        self.m_time: float = m_time
        self.html: str = html
        self.meta: dict = meta

        # data from self.meta
        self.title: str = ''
        self.author: str = ''
        self.c_datetime: datetime = None
        self.m_datetime: datetime = None
        self.summary: str = ''
        self.lang: str = 'en'
        self.tags: list = None

        # also from self.meta, but for og metadata
        self.og: dict[str, str] = dict()

        self.__parse_meta()

    def __lt__(self, other):
        return self.c_time < other.c_time


    # parses meta from self.meta, for og, it prioritizes,
    # the actual og meta
    def __parse_meta(self):
        try:
            self.title = self.meta['title'][0]
        except KeyError: pass

        try:
            self.author = self.meta['author'][0]
        except KeyError: pass

        self.c_datetime = datetime.fromtimestamp(self.c_time,
                                                 tz=timezone.utc)

        if self.m_time != 0.0:
            self.m_datetime = datetime.fromtimestamp(self.m_time,
                                                     tz=timezone.utc)

        try:
            self.summary = self.meta['summary'][0]
        except KeyError: pass

        try:
            self.lang = self.meta['lang'][0]
        except KeyError: pass

        try:
            self.tags = self.meta['tags']
            self.tags.sort()
        except KeyError: pass

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
