import sys
from typing import Callable
import pytest
from logging import getLogger, DEBUG

from pyssg.arg_parser import get_parser
from pyssg.custom_logger import setup_logger


@pytest.fixture(scope='session')
def arg_parser():
    return get_parser()


@pytest.fixture(scope='session')
def logger():
    setup_logger(__name__, DEBUG)
    return getLogger(__name__)


@pytest.fixture
def capture_stdout(monkeypatch: Callable) -> dict[str, str | int]:
    buffer: dict[str, str | int] = {'stdout': '', 'write_calls': 0}

    def fake_writer(s):
        buffer['stdout'] += s
        buffer['write_calls'] += 1  # type: ignore

    monkeypatch.setattr(sys.stdout, 'write', fake_writer)
    return buffer
