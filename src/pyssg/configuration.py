import os
import sys
from importlib.metadata import version
from logging import Logger, getLogger
from typing import Any

from .utils import get_expanded_path, get_time_now
from .yaml_parser import get_yaml

log: Logger = getLogger(__name__)
VERSION: str = version('pyssg')


def __expand_all_paths(config: dict[str, Any]) -> None:
    log.debug('expanding all path options: %s', config['path'].keys())
    for option in config['path'].keys():
        config['path'][option] = get_expanded_path(config['path'][option])


# not necessary to type deeper than the first dict
def get_parsed_config(path: str) -> list[dict[str, Any]]:
    log.debug('reading default config')
    config: list[dict[str, Any]] = get_yaml(path)
    log.info('found %s document(s) for config "%s"', len(config), path)

    if len(config) < 2:
        log.error('config file requires at least 2 documents:'
                  ' main config and root dir config')
        sys.exit(1)

    __expand_all_paths(config[0])

    log.debug('adding possible missing configuration and populating')
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

    if config[1]['dir'] != "/":
        log.error('the first directory config needs to be'
                  ' root (/), found %s instead', config[1]['dir'])
        sys.exit(1)
    return config

