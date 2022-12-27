import os
import sys
import pprint
from copy import deepcopy
from operator import itemgetter
from logging import Logger, getLogger

from jinja2 import Environment, Template, FileSystemLoader as FSLoader

from .utils import get_file_list, get_dir_structure, create_dir, copy_file
from .database import Database
from .md_parser import MDParser
from .page import Page

log: Logger = getLogger(__name__)


class Builder:
    def __init__(self, config: dict,
                 db: Database,
                 dir_path: str) -> None:
        log.debug('initializing site builder')
        self.config: dict = config
        self.db: Database = db
        self.dir_path: str = dir_path

        if self.dir_path not in self.config['dirs']:
            log.error('couldn\'t find "dirs.%s" attribute in config file', self.dir_path)
            sys.exit(1)
        if os.path.isabs(self.dir_path) and self.dir_path.strip() != '/':
            log.error('dir path "%s" cannot be absolute, except for the special case "/"', self.dir_path)
            sys.exit(1)

        log.debug('building dir_cfg for "%s" dir_path', self.dir_path)
        self.dir_cfg: dict = deepcopy(self.config['dirs'][self.dir_path]['cfg'])

        if self.dir_path.strip() == '/':
            log.debug('dir_path is "/", copying src/dst directly')
            self.dir_cfg['src'] = self.config['path']['src']
            self.dir_cfg['dst'] = self.config['path']['dst']
            self.dir_cfg['url'] = self.config['url']['main']
        else:
            log.debug('dir_path is "%s", generating', self.dir_path)
            self.dir_cfg['src'] = os.path.join(self.config['path']['src'], self.dir_path)
            self.dir_cfg['dst'] = os.path.join(self.config['path']['dst'], self.dir_path)
            self.dir_cfg['url'] = f'{self.config["url"]["main"]}/{self.dir_path}'

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
        log.debug('initializing the jinja environment')
        self.env: Environment = Environment(loader=FSLoader(self.config['path']['plt']),
                                            autoescape=False,
                                            trim_blocks=True,
                                            lstrip_blocks=True)

        self.dirs: list[str]
        self.md_files: list[str]
        self.html_files: list[str]

        # files and pages are synoyms
        self.all_files: list[Page]
        self.all_tags: list[tuple[str, str]]
        self.common_vars: dict

    def build(self) -> None:
        log.debug('building site for dir path "%s"', self.dir_path)
        if 'exclude_dirs' not in self.dir_cfg:
            log.debug('"exclude_dirs" field not found in "dirs.%s.cfg"', self.dir_path)
            self.dir_cfg['exclude_dirs'] = []
        if not isinstance(self.dir_cfg['exclude_dirs'], list):
            log.error('"exclude_dirs" field in "dirs.%s.cfg" isn\'t of type "list"', self.dir_path)
            sys.exit(1)

        self.dirs = get_dir_structure(self.dir_cfg['src'],
                                      self.dir_cfg['exclude_dirs'])
        self.md_files = get_file_list(self.dir_cfg['src'],
                                      ('.md',),
                                      self.dir_cfg['exclude_dirs'])
        self.html_files = get_file_list(self.dir_cfg['src'],
                                        ('.html',),
                                        self.dir_cfg['exclude_dirs'])

        self.__create_dir_structure()
        self.__copy_html_files()

        # TODO: check if need to pass dirs.dir_path.files
        parser: MDParser = MDParser(self.md_files,
                                    self.config,
                                    self.dir_cfg,
                                    self.db)
        parser.parse_files()

        # just so i don't have to pass these vars to all the functions
        self.all_files = parser.all_files
        self.all_tags = parser.all_tags

        # TODO: check if need to pass dirs.dir_path.files
        # dict for the keyword args to pass to the template renderer
        log.debug('adding exposed vars for jinja')
        self.common_vars = dict(config=self.config,
                                dir_config=self.dir_cfg,
                                all_pages=self.all_files,
                                all_tags=self.all_tags)

        self.__render_pages(self.dir_cfg['plt'])

        if self.dir_cfg['tags']:
            log.debug('rendering tags for dir_path "%s"', self.dir_path)
            create_dir(os.path.join(self.dir_cfg['dst'], 'tag'), True, True)
            if isinstance(self.dir_cfg['tags'], str):
                self.__render_tags(self.dir_cfg['tags'])
            else:
                self.__render_tags('tag.html')

        default_plts: dict[str, str] = {'index': 'index.html',
                                        'rss': 'rss.xml',
                                        'sitemap': 'sitemap.xml'}
        for opt in default_plts.keys():
            if self.dir_cfg[opt]:
                if isinstance(self.dir_cfg[opt], str):
                    self.__render_template(self.dir_cfg[opt],
                                           default_plts[opt],
                                           **self.common_vars)
                else:
                    self.__render_template(default_plts[opt],
                                           default_plts[opt],
                                           **self.common_vars)

    def __create_dir_structure(self) -> None:
        log.debug('creating dir structure for dir_path "%s"', self.dir_path)
        create_dir(self.dir_cfg['dst'], True, True)
        for d in self.dirs:
            path: str = os.path.join(self.dir_cfg['dst'], d)
            create_dir(path, True, True)

    def __copy_html_files(self) -> None:
        if not len(self.html_files) > 0:
            log.debug('no html files to copy')
            return

        log.debug('copying all html files')
        src_file: str
        dst_file: str
        for file in self.html_files:
            src_file = os.path.join(self.dir_cfg['src'], file)
            dst_file = os.path.join(self.dir_cfg['dst'], file)
            log.debug('copying "%s"', file)
            copy_file(src_file, dst_file)

    def __render_pages(self, template_name: str) -> None:
        log.debug('rendering pages with template "%s"', template_name)
        page_vars: dict = deepcopy(self.common_vars)

        for p in self.all_files:
            p_fname: str = p.name.replace('.md', '.html')
            log.debug('adding page "%s" to exposed vars for jinja', p_fname)
            page_vars['page'] = p
            # actually render article
            self.__render_template(template_name, p_fname, **page_vars)

    def __render_tags(self, template_name: str) -> None:
        log.debug('rendering tags with template "%s"', template_name)
        tag_vars: dict = deepcopy(self.common_vars)
        tag_pages: list[Page]
        for t in self.all_tags:
            log.debug('rendering tag "%s"', t[0])
            # clean tag_pages
            tag_pages = []
            log.debug('adding all pages that contain current tag')
            for p in self.all_files:
                if p.tags is not None and t[0] in list(map(itemgetter(0),
                                                           p.tags)):
                    log.debug('adding page "%s" as it contains tag "%s"',
                              p.name, t[0])
                    tag_pages.append(p)
            log.debug('adding tag and tag_pages to exposed vars for jinja')
            tag_vars['tag'] = t
            tag_vars['tag_pages'] = tag_pages
            t_fname: str = f'tag/@{t[0]}.html'
            # actually render tag page
            self.__render_template(template_name, t_fname, **tag_vars)

    def __render_template(self, template_name: str,
                          file_name: str,
                          **template_vars) -> None:
        log.debug('rendering html "%s" with template "%s"',
                  file_name, template_name)
        template: Template = self.env.get_template(template_name)
        content: str = template.render(**template_vars)
        dst_path: str = os.path.join(self.dir_cfg['dst'], file_name)

        log.debug('writing html file to path "%s"', dst_path)
        with open(dst_path, 'w') as f:
            f.write(content)
