import os
from typing import Union
from importlib.metadata import version
from datetime import datetime, timezone


class Configuration:
    def __init__(self, path: str):
        self.path: str = path
        # config file specific
        self.src: str = None
        self.dst: str = None
        self.plt: str = None
        self.url: str = None
        self.static_url: str = None
        self.default_image_url: str = None
        self.title: str = None
        self.dformat: str = None
        self.l_dformat: str = None
        self.lsep_dformat: str = None
        self.force: bool = None

        # other
        self.version: str = version('pyssg')
        self.dformat_rss: str = '%a, %d %b %Y %H:%M:%S GMT'
        self.dformat_sitemap: str = '%Y-%m-%d'
        self.run_date_rss = datetime.now(tz=timezone.utc).strftime(self.dformat_rss)
        self.run_date_sitemap = \
        datetime.now(tz=timezone.utc).strftime(self.dformat_sitemap)


    def read(self):
        try:
            lines: list[str] = None
            with open(self.path, 'r') as f:
                lines = f.readlines()

            opts: dict[str, Union[str, bool]] = dict()
            for l in lines:
                kv: list[str] = l.split('=', 1)
                if len(kv) != 2:
                    raise Exception('wrong config syntax')

                k: str = kv[0].strip().lower()
                v_temp: str = kv[1].strip()
                # check if value should be a boolean true
                v: Union[str, bool] = v_temp\
                    if v_temp.lower() not in ['true', '1', 'yes']\
                    else True

                opts[k] = v

            try:
                self.src = opts['src']
            except KeyError: pass

            try:
                self.dst = opts['dst']
            except KeyError: pass

            try:
                self.plt = opts['plt']
            except KeyError: pass

            try:
                self.url = opts['url']
            except KeyError: pass

            try:
                self.static_url = opts['static_url']
            except KeyError: pass

            try:
                self.default_image_url = opts['default_image_url']
            except KeyError: pass

            try:
                self.title = opts['title']
            except KeyError: pass

            try:
                self.dformat = opts['date_formaT']
            except KeyError: pass

            try:
                self.l_dformat = opts['list_date_FORMAT']
            except KeyError: pass

            try:
                self.lsep_dformat = opts['list_sep_dATE_FORMAT']
            except KeyError: pass

            try:
                # if the parser above didn't read a boolean true, then take it
                # as a false anyways
                self.force = opts['force'] if opts['force'] is True else False
            except KeyError: pass

        except OSError: pass


    def fill_missing(self, opts: dict[str, Union[str, bool]]) -> None:
        if self.src is None:
            self.src = opts['src']

        if self.dst is None:
            self.dst = opts['dst']

        if self.plt is None:
            self.plt = opts['plt']

        if self.url is None:
            self.url = opts['url']

        if self.static_url is None:
            self.static_url = opts['static_url']

        if self.default_image_url is None:
            self.default_image_url = opts['default_image_url']

        if self.title is None:
            self.title = opts['title']

        if self.dformat is None:
            self.dformat = opts['date_format']

        if self.l_dformat is None:
            self.l_dformat = opts['list_date_format']

        if self.lsep_dformat is None:
            self.lsep_dformat = opts['list_sep_date_format']

        if self.force is None:
            self.force = opts['force']
