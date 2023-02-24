import os
import sys
import pytest
from pathlib import Path
from typing import Any, Callable
from pytest import MonkeyPatch
from argparse import ArgumentParser
from datetime import datetime, timezone
from importlib.metadata import version as v
from logging import Logger, getLogger, DEBUG

from pyssg.arg_parser import get_parser
from pyssg.custom_logger import setup_logger


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
def test_dir() -> str:
    return str(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope='session')
def test_resource() -> str:
    return 'tests.io_files'


@pytest.fixture(scope='session')
def simple_yaml() -> str:
    return 'simple.yaml'


@pytest.fixture(scope='session')
def arg_parser() -> ArgumentParser:
    return get_parser()


@pytest.fixture(scope='session')
def logger() -> Logger:
    setup_logger(__name__, DEBUG)
    return getLogger(__name__)


@pytest.fixture
def capture_stdout(monkeypatch: MonkeyPatch) -> dict[str, str | int]:
    buffer: dict[str, str | int] = {'stdout': '', 'write_calls': 0}

    def fake_writer(s):
        buffer['stdout'] += s
        buffer['write_calls'] += 1  # type: ignore

    monkeypatch.setattr(sys.stdout, 'write', fake_writer)
    return buffer


@pytest.fixture
def get_fmt_time() -> Callable[..., str]:
    def fmt_time(fmt: str) -> str:
        return datetime.now(tz=timezone.utc).strftime(fmt)
    return fmt_time


@pytest.fixture
def simple_dict() -> dict[str, Any]:
    return {'define': '$PYSSG_HOME/pyssg/site_example/',
            'title': 'Example site',
            'path': {
                'src': '/tmp/pyssg/pyssg/site_example/src',
                'dst': '/tmp/pyssg/pyssg/site_example/dst',
                'plt': '/tmp/pyssg/pyssg/site_example/plt',
                'db': '/tmp/pyssg/pyssg/site_example/.files'},
            'url': {
                'main': 'https://example.com',
                'static': 'https://static.example.com',
                'default_image': 'images/default.png'},
            'fmt': {
                'date': '%a, %b %d, %Y @ %H:%M %Z',
                'list_date': '%b %d',
                'list_sep_date': '%B %Y'},
            'dirs': {
                '/': {
                    'cfg': {
                        'plt': 'page.html',
                        'tags': False,
                        'index': False,
                        'rss': False,
                        'sitemap': False,
                        'exclude_dirs': []}}}}


@pytest.fixture(scope='function')
def tmp_dir_structure(tmp_path: Path) -> Path:
    root: Path = tmp_path/'dir_str'
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
