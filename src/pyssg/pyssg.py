import os
from argparse import ArgumentParser, Namespace

from .templates import create_templates
from .parser import generate_static_site


def get_options() -> Namespace:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that reads
                            Markdown files and creates HTML files.''')
    parser.add_argument('-s', '--src',
                        default='src',
                        type=str,
                        help='''src directory; handmade files, templates and
                        metadata directory; defaults to 'src' ''')
    parser.add_argument('-d', '--dst',
                        default='dst',
                        type=str,
                        help='''dst directory; generated (and transfered html)
                        files; defaults to 'dst' ''')
    parser.add_argument('-i', '--init',
                        action='store_true',
                        help='''initializes the dir structure, templates,
                        as well as the 'src' and 'dst' directories''')
    parser.add_argument('-b', '--build',
                        action='store_true',
                        help='''generates all html files and passes over
                        existing (handmade) ones''')

    return parser.parse_args()


def main():
    opts = vars(get_options())
    src = opts['src']
    dst = opts['dst']

    if opts['init']:
        create_templates(src, dst)
        return

    if opts['build']:
        generate_static_site(src, dst)
        return
