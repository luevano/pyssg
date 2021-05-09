import os
import shutil
from .discovery import get_all_files
from .converter import create_html_files


def create_dir_structure(dst: str, dirs: list[str]) -> None:
    iwd = os.getcwd()

    os.chdir(dst)
    cwd = os.getcwd()

    for d in dirs:
        # for the dir structure,
        # doesn't matter if the dir already exists
        try:
            os.makedirs(os.path.join(cwd, d))
        except FileExistsError:
            pass

    os.chdir(iwd)


def copy_html_files(src: str, dst: str, files: list[str]) -> None:
    src_file = None
    dst_file = None

    for f in files:
        src_file = os.path.join(src, f)
        dst_file = os.path.join(dst, f)

        shutil.copy2(src_file, dst_file)


def generate_static_site(src: str, dst: str) -> None:
    dirs, md_files, html_files = get_all_files(src)
    create_dir_structure(dst, dirs)

    copy_html_files(src, dst, html_files)
    create_html_files(src, dst, md_files)
