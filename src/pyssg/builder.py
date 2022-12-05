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

        log.debug('building dir_config and src/dst paths for "%s" dir path', self.dir_path)
        self.dir_config: dict = deepcopy(self.config['dirs'][self.dir_path])

        if self.dir_path.strip() == '/':
            log.debug('dir path is "/", copying src/dst directly')
            self.dir_config['src'] = self.config['path']['src']
            self.dir_config['dst'] = self.config['path']['dst']
            self.dir_config['url'] = self.config['url']['main']
        else:
            self.dir_config['src'] = os.path.join(self.config['path']['src'], self.dir_path)
            self.dir_config['dst'] = os.path.join(self.config['path']['dst'], self.dir_path)
            self.dir_config['url'] = f"{self.config['url']['main']}/{self.dir_path}"

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
        log.debug('initializing the jinja environment')
        self.__loader: FSLoader = FSLoader(self.config['path']['plt'])
        self.env: Environment = Environment(loader=self.__loader,
                                            autoescape=False,
                                            trim_blocks=True,
                                            lstrip_blocks=True)

        self.dirs: list[str]
        self.md_files: list[str]
        self.html_files: list[str]

        # files and pages are synoyms
        self.all_files: list[Page]
        self.updated_files: list[Page]
        self.all_tags: list[tuple[str, str]]
        self.common_vars: dict


    def build(self) -> None:
        log.debug('building site for dir path "%s"', self.dir_path)
        if 'exclude_dirs' not in self.dir_config:
            log.debug('"exclude_dirs" attribute not found in "dirs.%s" in config file', self.dir_path)
            self.dir_config['exclude_dirs'] = []
        if not isinstance(self.dir_config['exclude_dirs'], list):
            log.error('"exclude_dirs" attribute is not of type "list"')
            sys.exit(1)

        self.dirs = get_dir_structure(self.dir_config['src'],
                                      self.dir_config['exclude_dirs'])
        self.md_files = get_file_list(self.dir_config['src'],
                                      ['.md'],
                                      self.dir_config['exclude_dirs'])
        self.html_files = get_file_list(self.dir_config['src'],
                                        ['.html'],
                                        self.dir_config['exclude_dirs'])

        self.__create_dir_structure()
        self.__copy_html_files()

        parser: MDParser = MDParser(self.md_files,
                                    self.config,
                                    self.dir_config,
                                    self.db)
        parser.parse_files()

        # just so i don't have to pass these vars to all the functions
        self.all_files = parser.all_files
        self.updated_files = parser.updated_files
        self.all_tags = parser.all_tags

        # dict for the keyword args to pass to the template renderer
        log.debug('adding config, all_pages and all_tags to exposed vars for jinja')
        self.common_vars = dict(config=self.config,
                                dir_config=self.dir_config,
                                all_pages=self.all_files,
                                all_tags=self.all_tags)

        self.__render_pages(self.dir_config['plt'])

        if 'tags' in self.dir_config and self.dir_config['tags']:
            log.debug('rendering tags for dir "%s"', self.dir_path)
            create_dir(os.path.join(self.dir_config['dst'], 'tag'), True, True)
            self.__render_tags(self.dir_config['tags'])

        opt_renders: dict[str, str] = {'index': 'index.html',
                                       'rss': 'rss.xml',
                                       'sitemap': 'sitemap.xml'}
        for opt in opt_renders.keys():
            if opt in self.dir_config and self.dir_config[opt]:
                self.__render_template(self.dir_config[opt],
                    opt_renders[opt],
                    **self.common_vars)


    def __create_dir_structure(self) -> None:
        log.debug('creating dir structure')
        create_dir(self.dir_config['dst'], True, True)
        _dir_path: str
        for d in self.dirs:
            _dir_path = os.path.join(self.dir_config['dst'], d)
            # using silent=True to not print the info create dir msgs for this
            create_dir(_dir_path, True, True)


    def __copy_html_files(self) -> None:
        if len(self.html_files) > 0:
            log.debug('copying all html files')
        else:
            log.debug('no html files to copy')
        src_file: str
        dst_file: str

        for f in self.html_files:
            src_file = os.path.join(self.dir_config['src'], f)
            dst_file = os.path.join(self.dir_config['dst'], f)

            # only copy files if they have been modified (or are new)
            if self.db.update(src_file, remove=f'{self.dir_config["src"]}/'):
                log.debug('file "%s" has been modified or is new, copying', f)
                copy_file(src_file, dst_file)
            else:
                if self.config['info']['force']:
                    log.debug('file "%s" hasn\'t been modified, but option force is set to true, copying anyways', f)
                    copy_file(src_file, dst_file)
                else:
                    log.debug('file "%s" hasn\'t been modified, ignoring', f)


    def __render_pages(self, template_name: str) -> None:
        log.debug('rendering html')
        page_vars: dict = deepcopy(self.common_vars)
        temp_files: list[Page]

        # check if only updated should be created
        if self.config['info']['force']:
            log.debug('all html will be rendered, force is set to true')
            temp_files = self.all_files
        else:
            log.debug('only updated or new html will be rendered')
            temp_files = self.updated_files

        for p in temp_files:
            log.debug('adding page to exposed vars for jinja')
            page_vars['page'] = p
            # actually render article
            self.__render_template(template_name,
                                   p.name.replace('.md','.html'),
                                   **page_vars)


    def __render_tags(self, template_name: str) -> None:
        log.debug('rendering tags')
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

            # actually render tag page
            self.__render_template(template_name,
                                   f'tag/@{t[0]}.html',
                                   **tag_vars)


    def __render_template(self, template_name: str,
                          file_name: str,
                          **template_vars) -> None:
        log.debug('rendering html "%s" with template "%s"',
                  file_name, template_name)
        template: Template = self.env.get_template(template_name)
        content: str = template.render(**template_vars)
        dst_path: str = os.path.join(self.dir_config['dst'], file_name)

        log.debug('writing html file to path "%s"', dst_path)
        with open(dst_path, 'w') as f:
            f.write(content)
