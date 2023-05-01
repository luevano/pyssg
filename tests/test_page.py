from copy import deepcopy
from logging import WARNING
from typing import Any
from pytest import LogCaptureFixture
from pyssg.page import Page


# TODO: this probably needs more testing, but I'm doing the coverage for now


def test_page_basic(page_simple: Page) -> None:
    page_simple.parse_metadata()
    assert page_simple.title == ''
    assert page_simple.author == ['']
    assert page_simple.summary == ''
    assert page_simple.lang == 'en'
    assert page_simple.url == f"{page_simple.dir_config['url']}/{page_simple.name.replace('.md', '.html')}"


def test_page_no_mdate(page_simple: Page,
                       caplog: LogCaptureFixture) -> None:
    page_simple.parse_metadata()
    war: tuple[str, int, str] = ('pyssg.page',
                                 WARNING,
                                 'no mdatetime found, can\'t return a formatted string')
    assert page_simple.mdate('date') == ''
    assert caplog.record_tuples[-1] == war


def test_page_no_fmt(page_simple: Page,
                     caplog: LogCaptureFixture) -> None:
    page_simple.parse_metadata()
    war: tuple[str, int, str] = ('pyssg.page',
                                 WARNING,
                                 'format "something" not found in config, '
                                 'returning empty string')
    assert page_simple.cdate('something') == ''
    assert caplog.record_tuples[-1] == war


def test_page_comparison(page_simple: Page,
                         page_simple_modified: Page) -> None:
    assert not page_simple > page_simple_modified
    assert page_simple < page_simple_modified
    assert page_simple != page_simple_modified


def test_page_modified(page_simple_modified: Page) -> None:
    page_simple_modified.parse_metadata()
    meta: dict[str, Any] = deepcopy(page_simple_modified.meta)
    assert page_simple_modified.title == meta['title']
    assert page_simple_modified.author == list(meta['author'])
    assert page_simple_modified.summary == meta['summary']
    assert page_simple_modified.lang == meta['lang']
    assert page_simple_modified.url == f"{page_simple_modified.dir_config['url']}/{page_simple_modified.name.replace('.md', '.html')}"


def test_page_modified_no_tags(page_simple_modified: Page) -> None:
    meta: dict[str, Any] = deepcopy(page_simple_modified.meta)
    meta['tags'] = []
    page_simple_modified.meta = meta
    page_simple_modified.parse_metadata()
