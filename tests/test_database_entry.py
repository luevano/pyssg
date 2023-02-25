import pytest
from typing import Any
from logging import ERROR
from pytest import LogCaptureFixture
from pyssg.database_entry import DatabaseEntry


@pytest.mark.parametrize('entry, exp_str', [
    (('t', 0.0, 0.0, '1', set()), "['t', 0.0, 0.0, '1', []]"),
    (('t', 0, 1, '1', set()), "['t', 0.0, 1.0, '1', []]"),
    (('t', 0.0, 0.0, '1', '-'), "['t', 0.0, 0.0, '1', []]"),
    (('t', 0.0, 0.0, 1, '-'), "['t', 0.0, 0.0, '1', []]"),
    (('t', 0.0, 0.0, '1', {'-', 'tag'}), "['t', 0.0, 0.0, '1', ['tag']]"),
    (('t', 0.0, 0.0, '1', '-,tag'), "['t', 0.0, 0.0, '1', ['tag']]"),
    (('t', 0.0, 0.0, '1', 'tag,-,-'), "['t', 0.0, 0.0, '1', ['tag']]"),
    (('t', 0.0, 0.0, '1', 'tag1,tag2'), "['t', 0.0, 0.0, '1', ['tag1', 'tag2']]"),
    (('t', 0.0, 0.0, '1', {'tag1', 'tag2'}), "['t', 0.0, 0.0, '1', ['tag1', 'tag2']]"),
    (('t', 0.0, 0.0, '1', ' tag1 , tag2,tag3'), "['t', 0.0, 0.0, '1', ['tag1', 'tag2', 'tag3']]"),
    (('t', 0.0, 0.0, '1', 'tag3,tag2,tag1'), "['t', 0.0, 0.0, '1', ['tag1', 'tag2', 'tag3']]"),
    (('t', 0.0, 0.0, '1', 'tag2,tag3,tag1'), "['t', 0.0, 0.0, '1', ['tag1', 'tag2', 'tag3']]")
])
def test_db_entry_obj(entry: tuple[str, float, float, str, str | set[str]],
                      exp_str: str) -> None:
    db_entry: DatabaseEntry = DatabaseEntry(entry)
    assert str(db_entry) == exp_str


@pytest.mark.parametrize('entry, exp_str', [
    (('t', 0.0, 0.0, '1', set()), ['t', '0.0', '0.0', '1', '-']),
    (('t', 0, 1, '1', set()), ['t', '0.0', '1.0', '1', '-']),
    (('t', 0.0, 0.0, '1', '-'), ['t', '0.0', '0.0', '1', '-']),
    (('t', 0.0, 0.0, 1, '-'), ['t', '0.0', '0.0', '1', '-']),
    (('t', 0.0, 0.0, '1', '-,tag'), ['t', '0.0', '0.0', '1', 'tag']),
    (('t', 0.0, 0.0, '1', {'-', 'tag'}), ['t', '0.0', '0.0', '1', 'tag']),
    (('t', 0.0, 0.0, '1', 'tag,-,-'), ['t', '0.0', '0.0', '1', 'tag']),
    (('t', 0.0, 0.0, '1', 'tag1,tag2'), ['t', '0.0', '0.0', '1', 'tag1,tag2']),
    (('t', 0.0, 0.0, '1', {'tag1', 'tag2'}), ['t', '0.0', '0.0', '1', 'tag1,tag2']),
    (('t', 0.0, 0.0, '1', ' tag1 , tag2,tag3'), ['t', '0.0', '0.0', '1', 'tag1,tag2,tag3']),
    (('t', 0.0, 0.0, '1', 'tag3,tag2,tag1'), ['t', '0.0', '0.0', '1', 'tag1,tag2,tag3']),
    (('t', 0.0, 0.0, '1', 'tag2,tag3,tag1'), ['t', '0.0', '0.0', '1', 'tag1,tag2,tag3'])
])
def test_db_entry_get_raw(entry: tuple[str, float, float, str, str | set[str]],
                          exp_str: list[str]) -> None:
    db_entry: DatabaseEntry = DatabaseEntry(entry)
    db_entry_raw: list[str] = db_entry.get_raw_entry()
    assert db_entry_raw == exp_str


# not sure if this is enough to test tag updating,
#   it's a bit redundant as the set functionality is doing all the work
@pytest.mark.parametrize('new_tags', [
    ({'tag'}),
    ({'tag1', 'tag2'}),
    ({'tag1', 'tag2', 'tag3'}),
    ({'-'}),
    ({'-', '-'}),
    (set()),
    ({'-', '-'}),
])
def test_db_entry_update_tags(new_tags: set[str]) -> None:
    db_entry: DatabaseEntry = DatabaseEntry(('t', 0.0, 0.0, '1', {'just', 'something'}))
    db_entry.update_tags(new_tags)
    assert db_entry.tags == new_tags


# just a few random tests for things that are not str or set
@pytest.mark.parametrize('tags', [
    ({}),
    (tuple()),
    (1),
    (1.0),
])
def test_db_entry_bad_tags(tags: Any, caplog: LogCaptureFixture) -> None:
    err: tuple[str, int, str] = ('pyssg.database_entry',
                                 ERROR,
                                 'tags has to be either a set or string (comma separated)')
    with pytest.raises(SystemExit) as system_exit:
        DatabaseEntry(('t', 0.0, 0.0, '1', tags))
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err
