import os
import sys
import shutil


def create_dir(path: str, p: bool=False) -> None:
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        print(f'created directory "{path}"')
    except FileExistsError:
        print(f'directory "{path}" already exists')


def copy_file(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        shutil.copy(src, dst)
        print(f'copied file "{src}" to "{dst}"')
    else:
        print(f'"{dst}" already exists')


def sanity_check_path(path: str) -> None:
    if '$' in  path:
        print(f'"$" character found in path: "{path}"; could be due to non-existant env var.')
        sys.exit(1)
