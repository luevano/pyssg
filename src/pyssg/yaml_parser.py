import yaml
from yaml import SafeLoader
from yaml.nodes import SequenceNode
from io import TextIOWrapper
from importlib.resources import path as rpath
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


# required to concat values in yaml using !join [value, value, ...]
def __join_constructor(loader: SafeLoader, node: SequenceNode) -> str:
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])
SafeLoader.add_constructor('!join', __join_constructor)


# "file" is either a path or the yaml content itself
def __read_raw_yaml(file: TextIOWrapper) -> list[dict]:
    all_docs: list[dict] = []
    all_docs_gen = yaml.safe_load_all(file)
    for doc in all_docs_gen:
        all_docs.append(doc)

    return all_docs


def get_parsed_yaml(resource: str, package: str='') -> list[dict]:
    all_yaml_docs: list[dict] = []
    if package == '':
        log.debug('no package specified, reading file "%s"', resource)
        with open(resource, 'r') as f:
            all_yaml_docs = __read_raw_yaml(f)
    else:
        log.debug('package "%s" specified, reading resource "%s"',
            package, resource)
        with rpath(package, resource) as p:
            with open(p, 'r') as f:
                all_yaml_docs = __read_raw_yaml(f)

    return all_yaml_docs
