import pytest
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from typing import Callable


@pytest.mark.parametrize('log_level, starts_with, message', [
    (DEBUG, '[DEBUG]', 'first message'),
    (INFO, 'second message', 'second message'),
    (WARNING, '\x1b[33m[WARNING]', 'third message'),
    (ERROR, '\x1b[31m[ERROR]', 'fourth message'),
    (CRITICAL, '\x1b[31;1m[CRITICAL]', 'fifth message'),
])
def test_log_levels(log_level: int,
                    starts_with: str,
                    message: str,
                    logger: Callable,
                    capture_stdout: dict[str, str | int]) -> None:
    logger.log(log_level, message)
    assert str(capture_stdout['stdout']).startswith(starts_with)
    assert message in str(capture_stdout['stdout'])
