import pytest
from pytest import LogCaptureFixture
from typing import Any, Callable
from logging import DEBUG, INFO, WARNING, ERROR
from pyssg.configuration import get_static_config, get_parsed_config


# this test is a bit sketchy, as the way the datetimes are calculated could vary
#   by milliseconds or even have a difference in seconds
def test_static_default(rss_date_fmt: str,
                               sitemap_date_fmt: str,
                               get_fmt_time: Callable[..., str],
                               version: str) -> None:
    rss_run_date: str = get_fmt_time(rss_date_fmt)
    sitemap_run_date: str = get_fmt_time(sitemap_date_fmt)
    sc_dict: dict[str, Any] = {'fmt': {'rss_date': rss_date_fmt,
                                       'sitemap_date': sitemap_date_fmt},
                               'info': {'rss_run_date': rss_run_date,
                                        'sitemap_run_date': sitemap_run_date,
                                        'version': version}}
    static_config: dict[str, Any] = get_static_config()
    assert static_config == sc_dict


def test_simple(test_dir: str) -> None:
    yaml_dict: dict[str, Any] = {'define': '$PYSSG_HOME/pyssg/site_example/',
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
    yaml_path: str = f'{test_dir}/io_files/simple.yaml'
    yaml: list[dict[str, Any]] = get_parsed_config(yaml_path)
    assert len(yaml) == 1
    assert yaml[0] == yaml_dict


def test_simple_mising_key(test_dir: str,
                           caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have "title"')
    yaml_path: str = f'{test_dir}/io_files/simple_missing_key.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_simple_mising_dirs(test_dir: str,
                                caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have any dirs configs (dirs.*)')
    yaml_path: str = f'{test_dir}/io_files/simple_missing_dirs.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_simple_root_dir(test_dir: str,
                         caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have "dirs./"')
    yaml_path: str = f'{test_dir}/io_files/simple_missing_root_dir.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err
