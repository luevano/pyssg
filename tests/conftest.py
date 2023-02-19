import pytest
from pyssg.arg_parser import get_parser


@pytest.fixture
def arg_parser():
    return get_parser()