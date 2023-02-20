import sys
import pytest
from unittest.mock import patch
from argparse import ArgumentParser


# these tests don't really show any coverage, so not sure how useful they're
#   but I'm including them as at least these should work
@pytest.mark.parametrize('args, arg_name, exp_result', [
    (['--version'], 'version', True),
    (['-v'], 'version', True),
    # config really just inputs a string
    (['--config', 'value'], 'config', 'value'),
    (['-c', 'value'], 'config', 'value'),
    (['--copy-default-config'], 'copy_default_config', True),
    (['--init'], 'init', True),
    (['-i'], 'init', True),
    (['--build'], 'build', True),
    (['-b'], 'build', True),
    (['--debug'], 'debug', True)
])
def test_valid_args(args: list[str],
                    arg_name: str,
                    exp_result: str | bool,
                    arg_parser: ArgumentParser) -> None:
    with patch.object(sys, 'argv', ['pyssg'] + args):
        parsed_args: dict[str, str | bool] = vars(arg_parser.parse_args())
        assert parsed_args[arg_name] == exp_result


@pytest.mark.parametrize('args', [
    (['--something-random']),
    (['-z']),
    (['help']),
    (['h'])
])
def test_invalid_args(args: list[str],
                      arg_parser: ArgumentParser) -> None:
    with pytest.raises(SystemExit) as system_exit:
        arg_parser.parse_args(args)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 2
