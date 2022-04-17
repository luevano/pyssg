import sys
from importlib.metadata import version
from importlib.resources import path as rpath
from datetime import datetime, timezone
from configparser import ConfigParser


DEFAULT_CONFIG_PATH = '$XDG_CONFIG_HOME/pyssg/config.ini'
VERSION = version('pyssg')


def __check_well_formed_config(config: ConfigParser) -> None:
    default_config: ConfigParser = ConfigParser()
    with rpath('pyssg.plt', 'default.ini') as p:
        default_config.read(p)

    for section in default_config.sections():
        if not config.has_section(section):
            print(f'config does not have section "{section}"')
            sys.exit(1)
        for option in default_config.options(section):
            if not config.has_option(section, option):
                print(f'config does not have option "{option}" in section "{section}"')
                sys.exit(1)


def get_parsed_config(path: str) -> ConfigParser:
    config: ConfigParser = ConfigParser()
    config.read(path)

    __check_well_formed_config(config)

    # set other required options
    config.set('fmt', 'rss_date', '%%a, %%d %%b %%Y %%H:%%M:%%S GMT')
    config.set('fmt', 'sitemap_date', '%%Y-%%m-%%d')
    config.set('info', 'version', VERSION)
    config.set('info', 'rss_run_date', datetime.now(
        tz=timezone.utc).strftime(config.get('fmt', 'rss_date')))
    config.set('info', 'sitemap_run_date', datetime.now(
        tz=timezone.utc).strftime(config.get('fmt', 'sitemap_date')))

    return config
