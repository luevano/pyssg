from importlib.resources import path as rpath
from pyssg.yaml_parser import get_parsed_yaml


def test_yaml_resource_read() -> None:
    yaml: list[dict] = get_parsed_yaml('simple.yaml', 'tests.io_files')
    assert len(yaml) == 1


def test_yaml_path_read(test_dir: str) -> None:
    yaml: list[dict] = get_parsed_yaml(f'{test_dir}/io_files/simple.yaml')
    assert len(yaml) == 1


def test_yaml_join() -> None:
    yaml: dict = get_parsed_yaml('simple.yaml', 'tests.io_files')[0]
    define_str: str = '$HOME/pyssg/site_example/'
    assert yaml['define'] == define_str
    assert yaml['path']['src'] == f'{define_str}src'
