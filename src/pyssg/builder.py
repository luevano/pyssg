import os
import shutil

from .database import Database
from .discovery import get_all_files
from .converter import create_html_files


def create_dir_structure(dst: str,
                         dirs: list[str]) -> None:
    for d in dirs:
        # for the dir structure,
        # doesn't matter if the dir already exists
        try:
            os.makedirs(os.path.join(dst, d))
        except FileExistsError:
            pass


def copy_html_files(src: str,
                    dst: str,
                    files: list[str],
                    db: Database) -> None:
    src_file = None
    dst_file = None

    for f in files:
        src_file = os.path.join(src, f)
        dst_file = os.path.join(dst, f)

        # only copy files if they have been modified (or are new)
        if db.update(src_file, remove=f'{src}/'):
            shutil.copy2(src_file, dst_file)


def build_static_site(src: str,
                      dst: str,
                      db: Database) -> None:
    # get all file data and create necessary dir structure
    dirs, md_files, html_files = get_all_files(src)
    create_dir_structure(dst, dirs)

    copy_html_files(src, dst, html_files, db)
    create_html_files(src, dst, md_files, db)
