import os
import sys
from copy import deepcopy
from logging import Logger, getLogger

from jinja2 import Environment, Template, FileSystemLoader as FSLoader

from pyssg.utils import get_file_list, get_dir_structure, create_dir, copy_file
from pyssg.db.database import Database
from pyssg.md.parser import MDParser
from pyssg.md.page import Page

log: Logger = getLogger(__name__)


# TODO: need to better handle when using dir_path other than "/", as the "dir_path" is removed
class Builder:
    def __init__(self, config: dict,
                 db: Database,
                 dir_cfg: dict) -> None:
        log.debug('initializing site builder')
        self.config: dict = config
        self.db: Database = db
        self.dir_cfg: dict = deepcopy(dir_cfg)

        if os.path.isabs(self.dir_cfg['dir']) and self.dir_cfg['dir'].strip() != '/':
            log.error('dir path "%s" cannot be absolute', self.dir_cfg['dir'])
            sys.exit(1)

        if self.dir_cfg['dir'].strip() == '/':
            log.debug('dir path is "/", copying src/dst directly')
            self.dir_cfg['src'] = self.config['path']['src']
            self.dir_cfg['dst'] = self.config['path']['dst']
            self.dir_cfg['url'] = self.config['url']['base']
        else:
            log.debug('dir_path is "%s", generating', self.dir_cfg['dir'])
            self.dir_cfg['src'] = os.path.join(self.config['path']['src'], self.dir_cfg['dir'])
            self.dir_cfg['dst'] = os.path.join(self.config['path']['dst'], self.dir_cfg['dir'])
            self.dir_cfg['url'] = f'{self.config["url"]["base"]}/{self.dir_cfg["dir"]}'

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
        self.all_tags: list[str]
        self.common_vars: dict

    def build(self) -> None:
        log.debug('building site for dir path "%s"', self.dir_cfg['dir'])
        if 'exclude_dirs' not in self.dir_cfg:
            log.debug('"exclude_dirs" field for dir "%s" not found', self.dir_cfg['dir'])
            self.dir_cfg['exclude_dirs'] = []
        if not isinstance(self.dir_cfg['exclude_dirs'], list):
            log.error('"exclude_dirs" field for dir "%s" isn\'t of type "list"', self.dir_cfg['dir'])
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

        self.__render_pages(self.dir_cfg['plt']['page'])

        if 'tags' in self.dir_cfg['plt']:
            create_dir(os.path.join(self.dir_cfg['dst'], 'tags'), True)
            self.__render_tags(self.dir_cfg['plt']['tags'])

        generic: dict[str, str] = {'index': 'index.html',
                                   'rss': 'rss.xml',
                                   'sitemap': 'sitemap.xml'}
        for plt in generic:
            if  plt in self.dir_cfg['plt']:
                self.__render_template(self.dir_cfg['plt'][plt],
                                       generic[plt],
                                       **self.common_vars)

    def __create_dir_structure(self) -> None:
        log.debug('creating dir structure for dir "%s"', self.dir_cfg['dir'])
        create_dir(self.dir_cfg['dst'], True)
        for d in self.dirs:
            path: str = os.path.join(self.dir_cfg['dst'], d)
            create_dir(path, True)

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
        page_vars: dict = deepcopy(self.common_vars)

        for p in self.all_files:
            p_fname: str = p.name.replace('.md', '.html')
            page_vars['page'] = p
            # actually render article
            self.__render_template(template_name, p_fname, **page_vars)

    def __render_tags(self, template_name: str) -> None:
        tag_prefix: str = ''
        if 'tags_prefix' in self.dir_cfg:
            tag_prefix = self.dir_cfg['tags_prefix']
        tag_vars: dict = deepcopy(self.common_vars)
        tag_pages: list[Page]
        for t in self.all_tags:
            # clean tag_pages
            tag_pages = []
            for p in self.all_files:
                if p.tags is not None and t in p.tags:
                    tag_pages.append(p)
                    log.debug('added page "%s" to tag "%s"', p.name, t)
            tag_vars['tag'] = t
            tag_vars['tag_pages'] = tag_pages
            t_fname: str = f'tags/{tag_prefix}{t}.html'
            # actually render tag page
            self.__render_template(template_name, t_fname, **tag_vars)

    def __render_template(self, template_name: str,
                          file_name: str,
                          **template_vars) -> None:
        template: Template = self.env.get_template(template_name)
        content: str = template.render(**template_vars)
        dst_path: str = os.path.join(self.dir_cfg['dst'], file_name)

        with open(dst_path, 'w') as f:
            f.write(content)
        log.debug('rendered "%s" with template %s', dst_path, template_name)

