import os
from argparse import ArgumentParser, Namespace

from .file_discovery import get_md_files
from .file_structure import create_structure


def get_options() -> Namespace:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that reads
                            Markdown files and creates HTML files.''')
    parser.add_argument('-d', '--directory',
                        default='.',
                        type=str,
                        help='''root directory for all site files,
                        defaults to "." (cwd), uses relative or absolute
                        resolution''')
    parser.add_argument('-i', '--init',
                        action='store_true',
                        help='''initialize the directory structure where -d
                        specifies''')

    return parser.parse_args()


def main():
    opts = vars(get_options())
    directory = opts['directory']

    if opts['init']:
        create_structure(directory)

    os.chdir(directory)
    root_dir = os.getcwd()
