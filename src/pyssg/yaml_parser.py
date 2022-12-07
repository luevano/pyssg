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


def __read_raw_yaml(path: str) -> list[dict]:
    all_docs: list[dict] = []
    with open(path, 'r') as f:
        for doc in yaml.safe_load_all(f):
            all_docs.append(doc)
    return all_docs


def get_parsed_yaml(resource: str, package: str='') -> list[dict]:
    if package == '':
        log.debug('parsing yaml; reading "%s"', resource)
        return __read_raw_yaml(resource)
    log.debug('parsing yaml; reading "%s.%s"', package, resource)
    with rpath(package, resource) as p:
        return __read_raw_yaml(str(p))


SafeLoader.add_constructor('!join', __join_constructor)
