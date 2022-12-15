import sys
from importlib.metadata import version
from importlib.resources import path as rpath
from datetime import datetime, timezone
from logging import Logger, getLogger

from .utils import get_expanded_path
from .yaml_parser import get_parsed_yaml

log: Logger = getLogger(__name__)
DEFAULT_CONFIG_PATH: str = '$XDG_CONFIG_HOME/pyssg/config.yaml'
VERSION: str = version('pyssg')


def __check_well_formed_config(config: dict,
                               config_base: list[dict],
                               prefix_key: str = '') -> None:
    for key in config_base[0].keys():
        current_key: str = f'{prefix_key}.{key}' if prefix_key != '' else key
        log.debug('checking "%s"', current_key)
        if key not in config:
            log.error('config doesn\'t have "%s"', current_key)
            log.debug('key: %s; config.keys: %s', key, config.keys())
            sys.exit(1)
        # checks for dir_paths
        if key == 'dirs':
            if '/' not in config[key]:
                log.error('config doesn\'t have "%s./"', current_key)
                log.debug('key: %s; config.keys: %s', key, config[key].keys())
                sys.exit(1)
            log.debug('checking "%s" fields for (%s) dir_paths', key, ', '.join(config[key].keys()))
            for dkey in config[key].keys():
                new_current_key: str = f'{current_key}.{dkey}'
                new_config_base: list[dict] = [config_base[1], config_base[1]]
                __check_well_formed_config(config[key][dkey], new_config_base, new_current_key)
            continue
        # the case for elements that don't have nested elements
        if not config_base[0][key]:
            log.debug('"%s" doesn\'t need nested elements', current_key)
            continue
        new_config_base: list[dict] = [config_base[0][key], config_base[1]]
        __check_well_formed_config(config[key], new_config_base, current_key)


def __expand_all_paths(config: dict) -> None:
    log.debug('expanding all path options: %s', config['path'].keys())
    for option in config['path'].keys():
        config['path'][option] = get_expanded_path(config['path'][option])


# not necessary to type deeper than the first dict
def get_parsed_config(path: str) -> list[dict]:
    log.debug('reading config file "%s"', path)
    config_all: list[dict] = get_parsed_yaml(path)
    mandatory_config: list[dict] = get_parsed_yaml('mandatory_config.yaml', 'pyssg.plt')
    log.info('found %s document(s) for configuration "%s"', len(config_all), path)
    log.debug('checking that config file is well formed (at least contains mandatory fields')
    for config in config_all:
        __check_well_formed_config(config, mandatory_config)
        __expand_all_paths(config)
    return config_all


# not necessary to type deeper than the first dict,
#   static config means config that shouldn't be changed by the user
def get_static_config() -> dict[str, dict]:
    log.debug('reading and setting static config')
    config: dict = get_parsed_yaml('static_config.yaml', 'pyssg.plt')[0]
    # do I really need a lambda function...
    time = lambda x : datetime.now(tz=timezone.utc).strftime(config['fmt'][x])
    config['info']['version'] = VERSION
    config['info']['rss_run_date'] = time('rss_date')
    config['info']['sitemap_run_date'] = time('sitemap_date')
    return config
