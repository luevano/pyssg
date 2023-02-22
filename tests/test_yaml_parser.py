from typing import Any
from pyssg.yaml_parser import get_parsed_yaml

# the point of these tests is just to read yaml files
#   and test the join functionality


def test_yaml_resource_read(simple_yaml:str, test_resource: str) -> None:
    yaml: list[dict[str, Any]] = get_parsed_yaml(simple_yaml, test_resource)
    assert len(yaml) == 1


def test_yaml_path_read(test_dir: str) -> None:
    yaml_path: str = f'{test_dir}/io_files/simple.yaml'
    yaml: list[dict[str, Any]] = get_parsed_yaml(yaml_path)
    assert len(yaml) == 1


def test_yaml_join(simple_yaml:str, test_resource: str) -> None:
    yaml: dict[str, Any] = get_parsed_yaml(simple_yaml, test_resource)[0]
    define_str: str = '$PYSSG_HOME/pyssg/site_example/'
    assert yaml['define'] == define_str
    assert yaml['path']['src'] == f'{define_str}src'
