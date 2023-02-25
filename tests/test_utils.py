import pytest
from pytest import LogCaptureFixture
from pathlib import Path
from logging import INFO
from pyssg.utils import (get_expanded_path, get_checksum, copy_file, create_dir,
                         get_dir_structure, get_file_list)


# $PYSSG_HOME is the only env var set
#   in the project settings that resemble a path
@pytest.mark.parametrize('path, expected_expanded', [
    ('$PYSSG_HOME', '/tmp/pyssg'),
    ('$PYSSG_HOME/', '/tmp/pyssg'),
    ('/test$PYSSG_HOME/', '/test/tmp/pyssg'),
    ('/test/$PYSSG_HOME/', '/test/tmp/pyssg'),
    ('/test/$PYSSG_HOME/test', '/test/tmp/pyssg/test')
])
def test_path_expansion(path: str, expected_expanded: str) -> None:
    expanded: str = get_expanded_path(path)
    assert expanded == expected_expanded


@pytest.mark.parametrize('path', [
    ('$'),
    ('$NON_EXISTENT_VARIABLE'),
    ('/path/to/something/$'),
    ('/path/to/something/$NON_EXISTENT_VARIABLE')
])
def test_path_expansion_failure(path: str) -> None:
    with pytest.raises(SystemExit) as system_exit:
        get_expanded_path(path)
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 1


def test_checksum(test_dir: str, simple_yaml: str) -> None:
    path: str = f'{test_dir}/io_files/{simple_yaml}'
    simple_yaml_checksum: str = 'd4f0a3ed56fd530d3ea485dced25534c'
    checksum: str = get_checksum(path)
    assert checksum == simple_yaml_checksum


def test_copy_file(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    src: Path = tmp_path/'src'
    dst: Path = tmp_path/'dst'
    src.mkdir()
    dst.mkdir()
    src_file: Path = src/'tmp_file.txt'
    dst_file: Path = dst/'tmp_file.txt'
    src_file.write_text('something')
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'copied file "{src_file}" to "{dst_file}"')
    copy_file(str(src_file), str(dst_file))
    assert caplog.record_tuples[-1] == inf


def test_copy_file_failure(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    src: Path = tmp_path/'src'
    dst: Path = tmp_path/'dst'
    src.mkdir()
    dst.mkdir()
    src_file: Path = src/'tmp_file.txt'
    dst_file: Path = dst/'tmp_file.txt'
    src_file.write_text('something')
    dst_file.write_text('something')
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'file "{dst_file}" already exists, ignoring')
    copy_file(str(src_file), str(dst_file))
    assert caplog.record_tuples[-1] == inf


def test_create_dir(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    path: Path = tmp_path/'new_dir'
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'created directory "{path}"')
    assert path.exists() is False
    create_dir(str(path), False, False)
    assert path.exists() is True
    assert caplog.record_tuples[-1] == inf


def test_create_dir_failure(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    path: Path = tmp_path/'new_dir'
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'directory "{path}" exists, ignoring')
    path.mkdir()
    create_dir(str(path), False, False)
    assert caplog.record_tuples[-1] == inf


def test_create_dirs(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    path: Path = tmp_path/'new_dir'
    sub_path: Path = path/'sub_dir'
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'created directory "{sub_path}"')
    assert path.exists() is False
    assert sub_path.exists() is False
    create_dir(str(sub_path), True, False)
    assert path.exists() is True
    assert sub_path.exists() is True
    assert caplog.record_tuples[-1] == inf


def test_create_dirs_failure(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    path: Path = tmp_path/'new_dir'
    sub_path: Path = path/'sub_dir'
    inf: tuple[str, int, str] = ('pyssg.utils',
                                 INFO,
                                 f'directory "{sub_path}" exists, ignoring')
    path.mkdir()
    sub_path.mkdir()
    create_dir(str(sub_path), True, False)
    assert caplog.record_tuples[-1] == inf


@pytest.mark.parametrize('exclude, exp_dir_str', [
    ([], ['second/s1', 'first/f1/f2']),
    (['f2'], ['second/s1', 'first/f1']),
    (['f1'], ['second/s1', 'first']),
    (['second'], ['first/f1/f2']),
    (['s1', 'f2'], ['second', 'first/f1']),
    (['s1', 'f1'], ['second', 'first']),
    (['s1', 'first'], ['second'])
])
def test_dir_structure(tmp_dir_structure: Path,
                       exclude: list[str],
                       exp_dir_str: list[str]) -> None:
    dir_str: list[str] = get_dir_structure(str(tmp_dir_structure), exclude)
    # order doesn't matter
    assert sorted(dir_str) == sorted(exp_dir_str)


@pytest.mark.parametrize('exts, exclude_dirs, exp_flist', [
    (('txt',), [], ['f0.txt', 'second/f4.txt',
                    'second/s1/f5.txt', 'first/f1.txt',
                    'first/f1/f2.txt', 'first/f1/f2/f3.txt']),
    (('txt', 'html'), [], ['f0.html', 'f0.txt',
                           'second/f4.txt', 'second/f4.html',
                           'second/s1/f5.html', 'second/s1/f5.txt',
                           'first/f1.html', 'first/f1.txt',
                           'first/f1/f2.txt', 'first/f1/f2.html',
                           'first/f1/f2/f3.txt', 'first/f1/f2/f3.html']),
    (('md',), [], ['f0.md', 'second/f4.md',
                   'second/s1/f5.md', 'first/f1.md',
                   'first/f1/f2.md', 'first/f1/f2/f3.md']),
    (('md',), ['first'], ['f0.md', 'second/f4.md', 'second/s1/f5.md']),
    (('md',), ['first', 's1'], ['f0.md', 'second/f4.md']),
    (('md',), ['f2', 's1'], ['f0.md', 'second/f4.md',
                             'first/f1.md', 'first/f1/f2.md',])
])
def test_file_list(tmp_dir_structure: Path,
                   exts: tuple[str],
                   exclude_dirs: list[str],
                   exp_flist: list[str]) -> None:
    flist: list[str] = get_file_list(str(tmp_dir_structure), exts, exclude_dirs)
    # order doesn't matter
    assert sorted(flist) == sorted(exp_flist)
