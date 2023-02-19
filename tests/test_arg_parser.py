import pytest
from argparse import ArgumentParser


@pytest.mark.parametrize('args, arg_name, exp_result', [
    (['--version'], 'version', True),
    (['-v'], 'version', True),
    (['--config', 'value'], 'config', 'value'),
    (['-c', 'value'], 'config', 'value'),
])
def test_individual_args(args: list[str],
                         arg_name: str,
                         exp_result: str | bool,
                         arg_parser: ArgumentParser) -> None:
    parsed_args: dict[str, str | bool] = vars(arg_parser.parse_args(args))
    assert parsed_args[arg_name] == exp_result
