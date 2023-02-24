import pytest
from pytest import LogCaptureFixture
from typing import Any, Callable
from logging import ERROR
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


def test_simple(test_dir: str,
                simple_yaml: str,
                simple_dict: dict[str, Any]) -> None:
    yaml_path: str = f'{test_dir}/io_files/{simple_yaml}'
    yaml: list[dict[str, Any]] = get_parsed_config(yaml_path)
    assert len(yaml) == 1
    assert yaml[0] == simple_dict


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
                                 'config doesn\'t have any dirs (dirs.*)')
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


# this really just tests that both documents in the yaml file are read,
#   multiple.yaml is just simple.yaml with the same document twice,
#   shouldn't be an issue as the yaml package handles this
def test_multiple(test_dir: str, simple_dict: dict[str, Any]) -> None:
    yaml_path: str = f'{test_dir}/io_files/multiple.yaml'
    yaml: list[dict[str, Any]] = get_parsed_config(yaml_path)
    assert len(yaml) == 2
    assert yaml[0] == simple_dict
    assert yaml[1] == simple_dict


# also, this just tests that the checks for a well formed config file are
#   processed for all documents
def test_multiple_one_doc_error(test_dir: str,
                                caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have any dirs (dirs.*)')
    yaml_path: str = f'{test_dir}/io_files/multiple_one_doc_error.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err
