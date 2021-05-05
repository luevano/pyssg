import os


def get_md_files(directory: str) -> list:
    return os.listdir(directory)
