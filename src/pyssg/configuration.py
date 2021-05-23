import os
from typing import Union


class Configuration:
    def __init__(self, path: str):
        self.path: str = path
        self.src: str = None
        self.dst: str = None
        self.base_url: str = None
        self.title: str = None
        self.dformat: str = None
        self.l_dformat: str = None
        self.lsep_dformat: str = None
        self.force: bool = None


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

                k: str = kv[0].strip()
                v_temp: str = kv[1].strip()
                # check if value should be a boolean true
                v: Union[str, bool] = v_temp\
                    if v_temp.lower() not in ['true', '1', 'yes']\
                    else True

                opts[k] = v

            try:
                self.src = opts['SRC_PATH']
            except KeyError: pass

            try:
                self.dst = opts['DST_PATH']
            except KeyError: pass

            try:
                self.base_url = opts['BASE_URL']
            except KeyError: pass

            try:
                self.title = opts['TITLE']
            except KeyError: pass

            try:
                self.dformat = opts['DATE_FORMAT']
            except KeyError: pass

            try:
                self.l_dformat = opts['LIST_DATE_FORMAT']
            except KeyError: pass

            try:
                self.lsep_dformat = opts['LIST_SEP_DATE_FORMAT']
            except KeyError: pass

            try:
                # if the parser above didn't read a boolean true, then take it
                # as a false anyways
                self.force = opts['FORCE'] if opts['FORCE'] is True else False
            except KeyError: pass

        except OSError: pass


    def fill_missing(self, opts: dict[str, Union[str, bool]]) -> None:
        if self.src is None:
            self.src = opts['src']

        if self.dst is None:
            self.dst = opts['dst']

        if self.base_url is None:
            self.base_url = opts['url']

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
