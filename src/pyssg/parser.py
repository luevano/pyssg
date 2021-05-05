import os
from .discovery import get_all_files


def create_dir_structure(dirs: list[str]):
    cwd = os.getcwd()

    for d in dirs:
        try:
            os.makedirs(os.path.join(cwd, d[1:]))
        except FileExistsError:
            pass


def generate_static_site(src: str, dst: str):
    iwd = os.getcwd()

    os.chdir(src)
    dirs, md_files, html_files = get_all_files()
    os.chdir(iwd)

    os.chdir(dst)
    create_dir_structure(dirs)
    os.chdir(iwd)
