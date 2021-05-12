import os
from argparse import ArgumentParser, Namespace

from .database import Database
from .template import Template
from .builder import build_static_site


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


def main() -> None:
    opts: dict[str] = vars(get_options())
    src: str = opts['src']
    dst: str = opts['dst']

    if opts['init']:
        try:
            os.mkdir(src)
            os.makedirs(os.path.join(dst, 'tag'))
        except FileExistsError:
            pass

        template: Template = Template(src)
        template.write()
        return

    if opts['build']:
        db: Database = Database(os.path.join(src, '.files'))

        build_static_site(src, dst, db)

        db.write()
        return
