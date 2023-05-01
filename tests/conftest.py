import os
import sys
import pytest
import shutil
from pathlib import Path
from typing import Any, Callable
from pytest import MonkeyPatch
from argparse import ArgumentParser
from datetime import datetime, timezone
from importlib.metadata import version as v
from logging import Logger, getLogger, DEBUG
from copy import deepcopy

from pyssg.arg_parser import get_parser
from pyssg.custom_logger import setup_logger
from pyssg.database_entry import DatabaseEntry
from pyssg.page import Page


@pytest.fixture(scope='session')
def version():
    return v('pyssg')


@pytest.fixture(scope='session')
def rss_date_fmt():
    return '%a, %d %b %Y %H:%M:%S GMT'


@pytest.fixture(scope='session')
def sitemap_date_fmt():
    return '%Y-%m-%d'


@pytest.fixture(scope='session')
def sample_files_path() -> str:
    return f'{str(os.path.dirname(os.path.abspath(__file__)))}/sample_files'


@pytest.fixture(scope='session')
def config_resource() -> str:
    return 'tests.sample_files.config'


@pytest.fixture(scope='session')
def default_yaml() -> str:
    return 'default.yaml'


@pytest.fixture(scope='session')
def arg_parser() -> ArgumentParser:
    return get_parser()


@pytest.fixture(scope='session')
def logger() -> Logger:
    setup_logger(__name__, DEBUG)
    return getLogger(__name__)


@pytest.fixture(scope='function')
def capture_stdout(monkeypatch: MonkeyPatch) -> dict[str, str | int]:
    buffer: dict[str, str | int] = {'stdout': '', 'write_calls': 0}

    def fake_writer(s):
        buffer['stdout'] += s
        buffer['write_calls'] += 1  # type: ignore

    monkeypatch.setattr(sys.stdout, 'write', fake_writer)
    return buffer


@pytest.fixture(scope='session')
def get_fmt_time() -> Callable[..., str]:
    def fmt_time(fmt: str) -> str:
        return datetime.now(tz=timezone.utc).strftime(fmt)
    return fmt_time


@pytest.fixture(scope='function')
def default_config() -> dict[str, Any]:
    return {'define': '$PYSSG_HOME/pyssg/site_example/',
            'title': 'Example site',
            'path': {
                'src': '/tmp/pyssg/pyssg/site_example/src',
                'dst': '/tmp/pyssg/pyssg/site_example/dst',
                'plt': '/tmp/pyssg/pyssg/site_example/plt',
                'db': '/tmp/pyssg/pyssg/site_example/.files'},
            'url': {
                'main': 'https://example.com'},
            'fmt': {
                'date': '%a, %b %d, %Y @ %H:%M %Z'},
            'dirs': {
                '/': {
                    'cfg': {
                        'plt': 'page.html',
                        'tags': False,
                        'index': False,
                        'rss': False,
                        'sitemap': False}}}}


@pytest.fixture(scope='function')
def root_dir_config() -> dict[str, Any]:
    return {'plt': 'page.html',
            'tags': False,
            'index': False,
            'rss': False,
            'sitemap': False,
            'src': '/tmp/pyssg/pyssg/site_example/src',
            'dst': '/tmp/pyssg/pyssg/site_example/dst',
            'url': 'https://example.com'}


@pytest.fixture(scope='function')
def tmp_dir_structure(tmp_path: Path) -> Path:
    root: Path = tmp_path/'dir_structure'
    # order matters
    dirs: list[Path] = [root,
                        root/'first',
                        root/'first/f1',
                        root/'first/f1/f2',
                        root/'second',
                        root/'second/s1']
    for i, d in enumerate(dirs):
        d.mkdir()
        for ext in ['txt', 'md', 'html']:
            (d/f'f{i}.{ext}').write_text('sample')
    return root


@pytest.fixture(scope='session')
def tmp_db_e1() -> DatabaseEntry:
    return DatabaseEntry(('first.md',
                          1671076311.823135,
                          0.0,
                          '778bce781d95730cd1e872a10130e20d',
                          '-'))


@pytest.fixture(scope='session')
def tmp_db_e2() -> DatabaseEntry:
    return DatabaseEntry(('a/second.md',
                          1671077831.63301,
                          # 1671078892.892921,
                          1677381461.8107588,
                          # '6092d6471d3a83135293e34ef6012939',
                          'a61d0116844b6ebc02db62b4b1bf453d',
                          'english,short,update'))


@pytest.fixture(scope='function')
def tmp_db(tmp_path: Path,
           tmp_db_e1: DatabaseEntry,
           tmp_db_e2: DatabaseEntry) -> Path:
    root: Path = tmp_path/'db'
    db_path: Path = tmp_path/'db/sample_db.psv'
    root.mkdir()
    e1: str = '|'.join(tmp_db_e1.get_raw_entry())
    e2: str = '|'.join(tmp_db_e2.get_raw_entry())
    db_path.write_text(f'{e1}\n{e2}\n')
    return db_path


@pytest.fixture(scope='function')
def tmp_db_wrong_col_num(tmp_path: Path) -> Path:
    root: Path = tmp_path/'db'
    db_path: Path = tmp_path/'db/sample_db_wrong_col_num.psv'
    root.mkdir()
    # missing tags, could be anything though
    db_path.write_text('name|0.0|0.0|cksm\n')
    return db_path


@pytest.fixture(scope='function')
def tmp_src_dir(tmp_path: Path,
                sample_files_path: str) -> Path:
    src: Path = tmp_path/'src'
    src_a: Path = src/'a'
    src.mkdir()
    src_a.mkdir()
    src_test: str = f'{sample_files_path}/md'

    files: list[str] = ['first.md', 'new.md', 'a/second.md']
    for f in files:
        shutil.copy2(f'{src_test}/{f}', f'{str(src)}/{f}')
    return src


@pytest.fixture(scope='function')
def page_simple(default_config: dict[str, Any],
                root_dir_config: dict[str, Any],
                rss_date_fmt: str,
                sitemap_date_fmt: str) -> Page:
    # adding the fmt as it is added on the code before being passed to the page
    config: dict[str, Any] = deepcopy(default_config)
    config['fmt']['rss_date'] = rss_date_fmt
    config['fmt']['sitemap_date'] = sitemap_date_fmt

    return Page(
        name='simple.md',
        ctime=1682418172.291993,
        mtime=0.0,
        html='<p>Simple converted md with nothing but this text.</p>',
        toc='<div class="toc">\n<ul></ul>\n</div>\n',
        toc_tokens=[],
        meta=dict(),
        config=config,
        dir_config=root_dir_config
    )


# this is basically page_simple with extras
@pytest.fixture(scope='function')
def page_simple_modified(default_config: dict[str, Any],
                         root_dir_config: dict[str, Any],
                         rss_date_fmt: str,
                         sitemap_date_fmt: str) -> Page:
    config: dict[str, Any] = deepcopy(default_config)
    config['fmt']['rss_date'] = rss_date_fmt
    config['fmt']['sitemap_date'] = sitemap_date_fmt

    dir_config: dict[str, Any] = deepcopy(root_dir_config)
    dir_config['tags'] = True
    tags: list[str] = ['blog', 'english', 'etc']

    basic_meta: dict[str, Any] = {
        'title': 'Example title',
        'author': 'Single Author',
        'summary': 'Some summary.',
        'lang': 'es',
        'tags': tags
    }

    return Page(
        name='simple_modified.md',
        ctime=1682418300.291993,
        mtime=1682418350.291993,
        html='<p>Simple converted md with nothing but this text, modified.</p>',
        toc='<div class="toc">\n<ul></ul>\n</div>\n',
        toc_tokens=[],
        meta=basic_meta,
        config=config,
        dir_config=dir_config
    )
