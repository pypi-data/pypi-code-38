"""
Summary.

    Configuration Module -- configure run time parameters & exclusions

"""
import os
import sys
import inspect
import logging
from xlines.usermessage import stdout_message
from xlines.colormap import ColorMap
from xlines._version import __version__
from xlines.variables import *

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

cm = ColorMap()

try:

    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'

except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'


def display_exclusions(expath, exdirpath):
    """
    Show list of all file type extensions which are excluded
    from line total calculations
    """
    tab = '\t'.expandtabs(15)

    # numbering
    div = cm.bpl + ')' + rst

    try:

        if os.path.exists(expath):
            with open(expath) as f1:
                exclusions = [x.strip() for x in f1.readlines()]

        stdout_message(message='File types excluded from line totals:')

        for index, ext in enumerate(exclusions):
            print('{}{:>3}{}'.format(tab, index + 1, div + '  ' + ext))

        sys.stdout.write('\n')
        return True

    except OSError as e:
        fx = inspect.stack()[0][3]
        stdout_message(message=f'{fx}: Error: {e}. ', prefix='WARN')
        return False


def main_menupage(options):
    """Displays main configuration menu jump page and options"""
    pass
    

def _configure(expath, exdirpath):
    """
        Add exclusions and update runtime constants

    Returns:
        Success | Failure, TYPE: bool
    """
    try:

        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        display_exclusions(expath, exdirpath)

        with open(expath) as f1:
            exclusions = [x.strip() for x in f1.readlines()]

        # query user input for new exclusions
        response = input('  Enter file extension types to be excluded separated by commas [quit]: ')

        if not response:
            sys.exit(exit_codes['EX_OK']['Code'])
        else:
            add_list = response.split(',')

            # add new extensions to existing
            exclusions.extend(['.' + x for x in add_list if '.' not in x])

            # write out new exclusions config file
            with open(expath, 'w') as f2:
                f2.writelines([x + '\n' for x in exclusions])

            display_exclusions(expath, exdirpath)    # display resulting exclusions set
            return True

    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False
