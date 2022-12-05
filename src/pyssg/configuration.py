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


def __check_well_formed_config(config: dict) -> None:
    log.debug('checking that config file is well formed (at least contains mandatory fields')
    mandatory_config: dict = get_parsed_yaml('mandatory_config.yaml', 'pyssg.plt')[0]

    for section in mandatory_config.keys():
        log.debug('checking section "%s"', section)
        if not config[section]:
            log.error('config does not have section "%s"', section)
            sys.exit(1)
        # the case for elements that don't have nested elements
        if not mandatory_config[section]:
            log.debug('section "%s" doesn\'t need nested elements', section)
            continue
        for option in mandatory_config[section].keys():
            log.debug('checking option "%s"', option)
            if option not in config[section] or not config[section][option]:
                log.error('config does not have option "%s" in section "%s"', option, section)
                sys.exit(1)


def __expand_all_paths(config: dict) -> None:
    log.debug('expanding all path options: %s', config['path'].keys())
    for option in config['path'].keys():
        config['path'][option] = get_expanded_path(config['path'][option])


# not necessary to type deeper than the first dict
def get_parsed_config(path: str) -> list[dict]:
    log.debug('reading config file "%s"', path)
    config: list[dict] = get_parsed_yaml(path)  # type: ignore

    log.info('found %s document(s) for configuration "%s"', len(config), path)

    __check_well_formed_config(config[0])
    __expand_all_paths(config[0])

    return config


# not necessary to type deeper than the first dict,
#   static config means config that shouldn't be changed by the user
def get_static_config() -> dict[str, dict]:
    log.debug('reading and setting static config')
    config: dict = get_parsed_yaml('static_config.yaml', 'pyssg.plt')[0]  # type: ignore

    config['info']['version'] = VERSION
    config['info']['rss_run_date'] = datetime.now(tz=timezone.utc)\
        .strftime(config['fmt']['rss_date'])
    config['info']['sitemap_run_date'] = datetime.now(tz=timezone.utc)\
        .strftime(config['fmt']['sitemap_date'])

    return config
