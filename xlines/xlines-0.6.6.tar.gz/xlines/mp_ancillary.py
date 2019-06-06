"""
Summary.

    Commons Module -- Common Functionality

"""
import os
import logging
from xlines.colors import Colors
from xlines.statics import local_config
from xlines._version import __version__


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

try:
    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                             # character for splitting paths (linux)
    acct = Colors.ORANGE
    text = Colors.BRIGHT_PURPLE
    TITLE = Colors.WHITE + Colors.BOLD
except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                            # character for splitting paths (windows)
    acct = Colors.CYAN
    text = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD


# universal colors
rd = Colors.RED + Colors.BOLD
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHT_GREEN
title = Colors.BRIGHT_WHITE + Colors.BOLD
bbc = bd + Colors.BRIGHT_CYAN
frame = gn + bd
btext = text + Colors.BOLD
bwt = Colors.BRIGHT_WHITE
bdwt = Colors.BOLD + Colors.BRIGHT_WHITE
ub = Colors.UNBOLD
rst = Colors.RESET

# globals
expath = local_config['EXCLUSIONS']['EX_EXT_PATH']
div = text + '/' + rst
div_len = 2
horiz = text + '-' + rst
arrow = bwt + '-> ' + rst
BUFFER = local_config['PROJECT']['BUFFER']


def linecount(path, whitespace=True):
    if whitespace:
        return len(open(path).readlines())
    return len(list(filter(lambda x: x != '\n', open(path).readlines())))


def remove_duplicates(duplicates):
    """
    Summary.

        Module function utilsing a generator to remove duplicates
        from large scale lists with minimal resource use

    Args:
        duplicates (list): contains repeated elements

    Returns:
        list object (iter)
    """
    uniq = []

    def dedup(d):
        for element in d:
            if element not in uniq:
                uniq.append(element)
                yield element
    return [x for x in dedup(duplicates)]


def remove_illegal(d, illegal):
    """
        Removes excluded file types

    Args:
        :d (list): list of filesystem paths ending with object
        :illegal (list):  list of file type extensions for ommission

    Returns:
        legal filesystem paths (str)
    """
    def parse_list(path):
        """Reads in list from file object"""
        with open(path) as f1:
            return [x.strip() for x in f1.readlines()]

    bad = []

    try:
        illegal_dirs = parse_list(local_config['EXCLUSIONS']['EX_DIR_PATH'])
    except KeyError:
        illegal_dirs = ['pycache', 'venv']

    for fpath in d:

        # filter for illegal file extensions
        fobject = os.path.split(fpath)[1]
        if ('.' in fobject) and ('.' + fobject.split('.')[1] in illegal):
            bad.append(fpath)

        # filter for illegal dirs
        elif list(filter(lambda x: x in fpath, illegal_dirs)):
            bad.append(fpath)
    return sorted(list(set(d) - set(bad)))


def locate_fileobjects(origin, path=expath):
    """
    Summary.

        - Walks local fs directories identifying all git repositories

    Args:
        - origin (str): filesystem directory location

    Returns:
        - paths, TYPE: list
        - Format:

         .. code-block:: json

                [
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/utils_email.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/slack_delivery.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/datadog_delivery.py',
                    '/cloud-custodian/tools/c7n_sentry/setup.py',
                    '/cloud-custodian/tools/c7n_sentry/test_sentry.py',
                    '/cloud-custodian/tools/c7n_kube/setup.py',
                    '...
                ]

    """
    fobjects = []

    if os.path.isfile(origin):
        return [origin]

    for root, dirs, files in os.walk(origin):
        for file in [f for f in files if '.git' not in root]:
            try:

                full_path = os.path.abspath(os.path.join(root, file))

                #if not ex.excluded(full_path):
                fobjects.append(full_path)

            except OSError:
                logger.exception(
                    '%s: Read error while examining local filesystem path (%s)' %
                    (inspect.stack()[0][3], path)
                )
                continue
    return remove_duplicates(fobjects)


def print_header(w):
    total_width = w + local_config['PROJECT']['COUNT_COLUMN_WIDTH']
    header_lhs = 'object'
    header_rhs = 'line count'
    tab = '\t'.expandtabs(total_width - len(header_lhs) - len(header_rhs))
    tab4 = '\t'.expandtabs(4)
    print(tab4 + (horiz * (total_width)))
    print(f'{tab4}{header_lhs}{tab}{header_rhs}')
    print(tab4 + (horiz * (total_width)))


def print_footer(total, object_count, w):
    total_width = w + local_config['PROJECT']['COUNT_COLUMN_WIDTH']
    msg = 'Total ({} objects):'.format(str(object_count))
    tab = '\t'.expandtabs(total_width - len(msg) - len(str(total)) - 1)

    # redefine with color codes added
    msg = f'Total ({title + "{:,}".format(object_count) + rst} objects):'
    tab4 = '\t'.expandtabs(4)
    print(tab4 + (horiz * (total_width)))
    print(f'{tab4}{msg}{tab}{bd + "{:,}".format(total) + rst:>6}' + '\n')
