import pytest
from pytest import LogCaptureFixture
from typing import Any, Callable
from logging import ERROR
from pyssg.configuration import get_static_config, get_parsed_config


# this test is a bit sketchy, as the way the datetimes are calculated could vary
#   by milliseconds or even have a difference in seconds
def test_static_config(rss_date_fmt: str,
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


def test_default_config(sample_files_path: str,
                        default_yaml: str,
                        default_config_dict: dict[str, Any]) -> None:
    yaml_path: str = f'{sample_files_path}/config/{default_yaml}'
    yaml: list[dict[str, Any]] = get_parsed_config(yaml_path)
    assert len(yaml) == 1
    assert yaml[0] == default_config_dict


def test_default_config_mising_mandatory_key(sample_files_path: str,
                                             caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have "title"')
    yaml_path: str = f'{sample_files_path}/config/default_missing_mandatory_key.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_default_config_mising_dirs(sample_files_path: str,
                                    caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have any dirs (dirs.*)')
    yaml_path: str = f'{sample_files_path}/config/default_missing_dirs.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_default_config_root_dir(sample_files_path: str,
                                 caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have "dirs./"')
    yaml_path: str = f'{sample_files_path}/config/default_missing_root_dir.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


# this really just tests that both documents in the yaml file are read,
#   both documents are the same (the default.yaml)
def test_multiple_default_config(sample_files_path: str,
                                 default_config_dict: dict[str, Any]) -> None:
    yaml_path: str = f'{sample_files_path}/config/multiple_default.yaml'
    yaml: list[dict[str, Any]] = get_parsed_config(yaml_path)
    assert len(yaml) == 2
    assert yaml[0] == default_config_dict
    assert yaml[1] == default_config_dict


# also, this just tests that the checks for a well formed config file are
#   processed for all documents
def test_multiple_default_config_one_doc_error(sample_files_path: str,
                                               caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.configuration',
                                 ERROR,
                                 'config doesn\'t have any dirs (dirs.*)')
    yaml_path: str = f'{sample_files_path}/config/multiple_default_one_doc_error.yaml'
    with pytest.raises(SystemExit) as system_exit:
        get_parsed_config(yaml_path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err
