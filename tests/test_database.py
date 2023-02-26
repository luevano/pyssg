from pathlib import Path
import pytest
from logging import DEBUG, WARNING, ERROR, CRITICAL
from pytest import LogCaptureFixture
from pyssg.database import Database
from pyssg.database_entry import DatabaseEntry


def test_read_database_no_db(test_dir: str, caplog: LogCaptureFixture) -> None:
    path: str = f'{test_dir}/non_existent_db.psv'
    war: tuple[str, int, str] = ('pyssg.database',
                                 WARNING,
                                 f'"{path}" doesn\'t exist, will be created '
                                 'once process finishes, ignore if it\'s the '
                                 'first run')
    db: Database = Database(path)
    db.read()
    assert caplog.record_tuples[-1] == war


def test_read_database_not_a_file(test_dir: str,
                                  caplog: LogCaptureFixture) -> None:
    path: str = test_dir
    err: tuple[str, int, str] = ('pyssg.database',
                                 ERROR,
                                 f'"{path}" is not a file')
    db: Database = Database(path)
    with pytest.raises(SystemExit) as system_exit:
        db.read()
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_read_database(tmp_db: Path,
                       tmp_db_e1: DatabaseEntry,
                       tmp_db_e2: DatabaseEntry) -> None:
    db: Database = Database(str(tmp_db))
    db.read()
    exp_db_e: dict[str, DatabaseEntry] = {tmp_db_e1.fname: tmp_db_e1,
                                          tmp_db_e2.fname: tmp_db_e2}
    for fname in db.e.keys():
        assert str(db.e[fname]) == str(exp_db_e[fname])


def test_read_database_wrong_col_num(tmp_db_wrong_col_num: Path,
                                     caplog: LogCaptureFixture) -> None:
    cri: tuple[str, int, str] = ('pyssg.database',
                                 CRITICAL,
                                 'row 1 doesn\'t contain 5 columns, '
                                 'contains 4 columns: '
                                 '"[\'name\', \'0.0\', \'0.0\', \'cksm\']"')
    db: Database = Database(str(tmp_db_wrong_col_num))
    with pytest.raises(SystemExit) as system_exit:
        db.read()
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == cri


def test_update_entry_tags(tmp_db: Path,
                           tmp_db_e1: DatabaseEntry,
                           caplog: LogCaptureFixture) -> None:
    caplog.set_level(DEBUG, logger='pyssg.database')
    fname: str = tmp_db_e1.fname
    new_tags: set[str] = {'tag1', 'tag2', 'tag3'}
    deb: tuple[str, int, str] = ('pyssg.database',
                                 DEBUG,
                                 f'entry "{fname}" new tags: {new_tags}')
    db: Database = Database(str(tmp_db))
    db.read()
    db.update_tags(fname, new_tags)
    assert db.e[fname].tags == new_tags
    assert caplog.record_tuples[-1] == deb


def test_update_entry_tags_failure(tmp_db: Path,
                                   caplog: LogCaptureFixture) -> None:
    fname: str = 'non_existent_file.md'
    new_tags: set[str] = {'tag1', 'tag2', 'tag3'}
    err: tuple[str, int, str] = ('pyssg.database',
                                 ERROR,
                                 f'can\'t update tags for entry "{fname}",'
                                 ' as it is not present in db')
    db: Database = Database(str(tmp_db))
    db.read()
    with pytest.raises(SystemExit) as system_exit:
        db.update_tags(fname, new_tags)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1
    assert caplog.record_tuples[-1] == err


def test_update_entry_new_entry_full_path(tmp_db: Path,
                                          tmp_src_dir: Path,
                                          caplog: LogCaptureFixture) -> None:
    caplog.set_level(DEBUG, logger='pyssg.database')
    fname: str = f'{tmp_src_dir}/new.md'
    deb: tuple[str, int, str] = ('pyssg.database',
                                 DEBUG,
                                 f'entry "{fname}" didn\'t exist, adding with'
                                 ' defaults')
    db: Database = Database(str(tmp_db))
    db.read()
    db.update(fname)
    assert caplog.record_tuples[-1] == deb


def test_update_entry_new_entry_fname_only(tmp_db: Path,
                                           tmp_src_dir: Path,
                                           caplog: LogCaptureFixture) -> None:
    caplog.set_level(DEBUG, logger='pyssg.database')
    fname: str = f'{tmp_src_dir}/new.md'
    deb: tuple[str, int, str] = ('pyssg.database',
                                 DEBUG,
                                 'entry "new.md" didn\'t exist, adding with'
                                 ' defaults')
    db: Database = Database(str(tmp_db))
    db.read()
    db.update(fname, f'{tmp_src_dir}/')
    assert caplog.record_tuples[-1] == deb


def test_update_entry_no_mod(tmp_db: Path,
                             tmp_src_dir: Path,
                             caplog: LogCaptureFixture) -> None:
    caplog.set_level(DEBUG, logger='pyssg.database')
    fname: str = f'{tmp_src_dir}/first.md'
    deb: tuple[str, int, str] = ('pyssg.database',
                                 DEBUG,
                                 'entry "first.md" hasn\'t been modified')
    db: Database = Database(str(tmp_db))
    db.read()
    db.update(fname, f'{tmp_src_dir}/')
    assert caplog.record_tuples[-1] == deb


def test_update_entry_modified(tmp_db: Path,
                               tmp_src_dir: Path,
                               caplog: LogCaptureFixture) -> None:
    caplog.set_level(DEBUG, logger='pyssg.database')
    fname: str = f'{tmp_src_dir}/a/second.md'
    with open(fname, 'a') as f:
        f.write('Added modification.\n')
    deb: tuple[str, int, str] = ('pyssg.database',
                                 DEBUG,
                                 'entry "a/second.md" new content: ')
    db: Database = Database(str(tmp_db))
    db.read()
    db.update(fname, f'{tmp_src_dir}/')
    # instead of checking the whole deb tuple, check that the message starts
    #   with the "new content", as getting the same timestamp will be difficult
    assert caplog.record_tuples[-1][1] == DEBUG
    assert caplog.record_tuples[-1][2].startswith(deb[2])


def test_write_database_no_change(tmp_db: Path,
                                  tmp_db_e1: DatabaseEntry,
                                  tmp_db_e2: DatabaseEntry) -> None:
    db: Database = Database(str(tmp_db))
    db.read()
    db.write()
    exp_db_e: dict[str, DatabaseEntry] = {tmp_db_e1.fname: tmp_db_e1,
                                          tmp_db_e2.fname: tmp_db_e2}
    db2: Database = Database(str(tmp_db))
    db2.read()
    for fname in db2.e.keys():
        assert str(db2.e[fname]) == str(exp_db_e[fname])


def test_write_database_new_entry(tmp_db: Path,
                                  tmp_src_dir: Path,
                                  tmp_db_e1: DatabaseEntry,
                                  tmp_db_e2: DatabaseEntry) -> None:
    fname: str = 'new.md'
    full_path: str = f'{tmp_src_dir}/{fname}'
    db: Database = Database(str(tmp_db))
    db.read()
    db.update(full_path, f'{tmp_src_dir}/')
    db_e2: DatabaseEntry = db.e[fname]
    db.write()
    exp_db_e: dict[str, DatabaseEntry] = {tmp_db_e1.fname: tmp_db_e1,
                                          tmp_db_e2.fname: tmp_db_e2,
                                          fname: db_e2}
    db2: Database = Database(str(tmp_db))
    db2.read()
    for fname in db2.e.keys():
        assert str(db2.e[fname]) == str(exp_db_e[fname])
