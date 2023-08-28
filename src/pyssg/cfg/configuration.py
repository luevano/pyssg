import sys
from importlib.metadata import version
from logging import Logger, getLogger
from typing import Any

from pyssg.utils import get_expanded_path, get_time_now
from pyssg.cfg.yaml_parser import get_yaml

log: Logger = getLogger(__name__)
VERSION: str = version('pyssg')


def __expand_all_paths(config: list[dict[str, Any]]) -> None:
    for option in config[0]['path'].keys():
        path: str = get_expanded_path(config[0]['path'][option])
        config[0]['path'][option] = path


def __add_mandatory_config(config: list[dict[str, Any]]) -> None:
    if 'fmt' not in config[0]:
        config[0]['fmt'] = dict()
    if 'rss_date' not in config[0]['fmt']:
        config[0]['fmt']['rss_date'] = '%a, %d %b %Y %H:%M:%S GMT'
    if 'sitemap_date' not in config[0]['fmt']:
        config[0]['fmt']['sitemap_date'] = '%Y-%m-%d'

    if 'info' not in config[0]:
        config[0]['info'] = dict()
    config[0]['info']['version'] = VERSION
    config[0]['info']['rss_run_date'] = get_time_now('rss_date')
    config[0]['info']['sitemap_run_date'] = get_time_now('sitemap_date')


def get_parsed_config(path: str) -> list[dict[str, Any]]:
    config: list[dict[str, Any]] = get_yaml(path)
    log.info('found %s documents for config "%s"', len(config), path)

    if len(config) < 2:
        log.error('config file requires at least 2 documents:'
                  ' main config and root dir config')
        sys.exit(1)

    __expand_all_paths(config)
    __add_mandatory_config(config)

    if config[1]['dir'] != "/":
        log.error('the first directory config needs to be'
                  ' root (/), found %s instead', config[1]['dir'])
        sys.exit(1)
    return config

