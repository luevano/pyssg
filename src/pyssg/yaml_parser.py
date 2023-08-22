import yaml
from yaml import SafeLoader
from yaml.nodes import SequenceNode
from importlib.resources import path as rpath
from logging import Logger, getLogger
from typing import Any

log: Logger = getLogger(__name__)


# required to concat values in yaml using !join [value, value, ...]
def __join_constructor(loader: SafeLoader, node: SequenceNode) -> str:
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


def setup_custom_yaml() -> None:
    SafeLoader.add_constructor('!join', __join_constructor)


def get_yaml(path: str) -> list[dict[str, Any]]:
    all_docs: list[dict[str, Any]] = []
    with open(path, 'r') as f:
        for doc in yaml.safe_load_all(f):
            all_docs.append(doc)
    return all_docs

