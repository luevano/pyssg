import os
import sys
import pytest
from typing import Callable
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
