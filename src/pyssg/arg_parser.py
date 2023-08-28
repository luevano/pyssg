from argparse import ArgumentParser


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that parses
                            Markdown files into HTML files.''')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='''print program version''')
    parser.add_argument('-c', '--config',
                        type=str,
                        help='''config file path; if not passed, './config.yaml'
                        is assumed''')
    parser.add_argument('-b', '--build',
                        action='store_true',
                        help='''generates all HTML files by parsing MD files
                        present in source directory and copies over manually
                        written HTML files''')
    parser.add_argument('-i', '--init',
                        type=str,
                        help='''initializes the directory structures and copies
                        default templates and config''')
    parser.add_argument('--debug',
                        action='store_true',
                        help='''change logging level from info to debug''')

    return parser
