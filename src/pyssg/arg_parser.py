from argparse import ArgumentParser, Namespace


def get_parsed_arguments() -> Namespace:
    parser = ArgumentParser(prog='pyssg',
                            description='''Static Site Generator that reads
                            Markdown files and creates HTML files.\nIf
                            [-c]onfig file is provided (or exists in default
                            location) all other options are ignored.\nFor
                            datetime formats see:
                            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes''')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='''print program version''')
    parser.add_argument('-c', '--config',
                        default='$XDG_CONFIG_HOME/pyssg/pyssgrc',
                        type=str,
                        help='''config file (path) to read from; defaults to
                        'pyssgrc' first, then
                        '$XDG_CONFIG_HOME/pyssg/pyssgrc' ''')
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
    parser.add_argument('-t', '--plt',
                        default='plt',
                        type=str,
                        help='''plt directory; all template files; defaults to
                        'plt' ''')
    parser.add_argument('-u', '--url',
                        default='',
                        type=str,
                        help='''base url without trailing slash''')
    parser.add_argument('--static-url',
                        default='',
                        type=str,
                        help='''base static url without trailing slash''')
    parser.add_argument('--default-image-url',
                        default='',
                        type=str,
                        help='''default image url''')
    parser.add_argument('--title',
                        default='Blog',
                        type=str,
                        help='''general title for the website; defaults to
                        'Blog' ''')
    parser.add_argument('--date-format',
                        default='%a, %b %d, %Y @ %H:%M %Z',
                        type=str,
                        help='''date format used inside pages (for creation and
                        modification times, for example); defaults to '%%a, %%b
                        %%d, %%Y @ %%H:%%M %%Z' ('Tue, Mar 16, 2021 @ 02:46 UTC',
                        for example)''')
    parser.add_argument('--list-date-format',
                        default='%b %d',
                        type=str,
                        help='''date format used for page entries in a list;
                        defaults to '%%b %%d' ('Mar 16', for example)''')
    parser.add_argument('--list-sep-date-format',
                        default='%B %Y',
                        type=str,
                        help='''date format used for the separator between page
                        entries in a list; defaults to '%%B %%Y' ('March 2021',
                        for example)''')
    parser.add_argument('-i', '--init',
                        action='store_true',
                        help='''initializes the dir structure, templates,
                        as well as the 'src' and 'dst' directories''')
    parser.add_argument('-b', '--build',
                        action='store_true',
                        help='''generates all html files and passes over
                        existing (handmade) ones''')
    parser.add_argument('-f', '--force',
                        action='store_true',
                        help='''force building all pages and not only the
                        updated ones''')

    return parser.parse_args()
