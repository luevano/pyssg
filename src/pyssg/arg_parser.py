from argparse import ArgumentParser


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that parses
                            Markdown files into HTML files. For datetime
                            formats see:
                            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes''')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='''print program version''')
    parser.add_argument('-c', '--config',
                        # don't give a default here, as it would seem like
                        #   --config was passed
                        # default='$XDG_CONFIG_HOME/pyssg/config.ini',
                        type=str,
                        help='''config file (path) to read from; if not passed,
                        '$XDG_CONFIG_HOME/pyssg/config.yaml' is used''')
    parser.add_argument('--copy-default-config',
                        action='store_true',
                        help='''copies the default config to path specified in
                        --config flag''')
    parser.add_argument('-i', '--init',
                        action='store_true',
                        help='''initializes the directory structures and copies
                        over default templates''')
    parser.add_argument('-b', '--build',
                        action='store_true',
                        help='''generates all HTML files by parsing MD files
                        present in source directory and copies over manually
                        written HTML files''')
    parser.add_argument('--debug',
                        action='store_true',
                        help='''change logging level from info to debug''')

    return parser
