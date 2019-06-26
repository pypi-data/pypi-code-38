"""
Summary.

    Configuration Module -- configure run time parameters & exclusions

"""
import os
import sys
import inspect
import logging
from time import sleep
from xlines.usermessage import stdout_message
from xlines.common import terminal_size
from xlines.colormap import ColorMap
from xlines._version import __version__
from xlines.statics import PACKAGE, local_config
from xlines.variables import *

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

cm = ColorMap()
default_width = 4


try:

    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'

except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'


def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear')
    return True


def _init_screen(height_percent=0.25):
    """

        Initializes screen before configuration artifact display

    Returns:
        width in columns for centering artifacts on cli terminal
        right to left, TYPE: int
    """
    clearscreen()
    rows, columns = terminal_size(height=True)
    print('\n' * int(int(rows) * height_percent))
    return int(columns)


def section_header(section, width=80, tabspaces=14):
    """
        Prints section header title and function ("section") with border

    Returns:
        width of section header in chars, TYPE: int
    """
    if section.lower() in ('add', 'delete'):
        title = '{} File Type Exclusions Menu'.format(bdwt + section.title() + rst)
    else:
        title = 'high line count {} update'.format(bdwt + section + rst)

    bar = '________________________________________________________________'
    pattern_width = len(bar)
    offset = '\t'.expandtabs(int((width / 2) - (pattern_width / 2)))
    border = bbl
    tab = '\t'.expandtabs(tabspaces)
    tab4 = '\t'.expandtabs(4)
    print(offset + border + bar + '\n' + rst)
    print('{}{}{}'.format(offset, tab, title))
    print(offset + border + bar + '\n' + rst)
    return len(bar)


def display_exclusions(expath, exdirpath, offset_spaces=default_width):
    """
    Show list of all file type extensions which are excluded
    from line total calculations
    """
    tab = '\t'.expandtabs(15)
    offset = '\t'.expandtabs(offset_spaces)

    # numbering
    div = cm.bpl + ')' + rst
    adj = 10

    try:

        if os.path.exists(expath):
            with open(expath) as f1:
                exclusions = [x.strip() for x in f1.readlines()]

        stdout_message(message='File types excluded from line counts:', indent=offset_spaces + adj)

        for index, ext in enumerate(exclusions):
            print('{}{}{:>3}{}'.format(offset, tab, index + 1, div + '  ' + ext))

        sys.stdout.write('\n')
        return True

    except OSError as e:
        fx = inspect.stack()[0][3]
        stdout_message(message=f'{fx}: Error: {e}. ', prefix='WARN')
        return False


def condition_map(letter, expath, exdirpath):
    return {
        'a': _configure_add,
        'b': _configure_remove,
        'c': _configure_hicount,
        'd': lambda x, y: sys.exit
    }.get(letter, lambda x, y: None)(expath, exdirpath)


def main_menupage(expath, exdirpath):
    """
    Displays main configuration menu jump page and options
    """
    def menu():
        border = bbl
        icolor = bbl
        bar = border + '''
        ________________________________________________________________________________
        '''
        pattern_width = len(bar)
        width = _init_screen()
        offset = '\t'.expandtabs(int((width / 2) - (pattern_width / 2)))
        _menu = (bar + rst + '''\n\n
            ''' + bdwt + PACKAGE + rst + ''' configuration main menu:\n\n
                  ''' + icolor + 'a' + rst + ''')  Add file type to exclusion list\n\n
                  ''' + icolor + 'b' + rst + ''')  Remove file type from exclusion list\n\n
                  ''' + icolor + 'c' + rst + ''')  Set high line count threshold (''' + acct + 'highlight' + rst + ''' file objects)\n\n
                  ''' + icolor + 'd' + rst + ''')  quit\n
        ''' + border + bar + rst)
        for line in _menu.split('\n'):
            print('{}{}'.format(offset, line))
        return offset

    loop = True
    tab8 = '\t'.expandtabs(8)

    while loop:
        offset = menu()
        answer = input('\n{}{}Choose operation [quit]: '.format(offset, tab8)).lower()
        sys.stdout.write('\n')

        if not answer or answer == 'd':
            return True

        elif answer in ['a', 'b', 'c']:
            condition_map(answer, expath, exdirpath)

        else:
            stdout_message(
                    message='You must provide a letter a, b, c, or d',
                    indent=16,
                    prefix='INFO'
                )
            sys.stdout.write('\n')


def _configure_add(expath, exdirpath):
    """
        Add exclusions and update runtime constants

    Returns:
        Success | Failure, TYPE: bool
    """
    tab4 = '\t'.expandtabs(4)
    loop = True
    adj = 4

    try:

        with open(expath) as f1:
            exclusions = [x.strip() for x in f1.readlines()]

        while loop:
            width = _init_screen()
            pattern_width = section_header('add', width, tabspaces=16)
            offset_chars = int((width / 2) - (pattern_width / 2)) + adj
            offset = '\t'.expandtabs(offset_chars)
            display_exclusions(expath, exdirpath, offset_chars)
            # query user input for new exclusions
            msg = 'Enter file extension types separated by commas [done]: '
            offset_msg = '\t'.expandtabs(int((width / 2) - (pattern_width / 2) + adj * 2))
            response = input(f'{offset_msg}{msg}')

            if not response:
                loop = False
                sys.stdout.write('\n')
                return True
            else:
                add_list = response.split(',')

                # add new extensions to existing
                exclusions.extend([x if x.startswith('.') else '.' + x for x in add_list])

                # write out new exclusions config file
                with open(expath, 'w') as f2:
                    f2.writelines([x + '\n' for x in exclusions])

    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False


def _configure_rewrite(expath, newlist):
    """
        Rewrite existing exclusion list on local filesystem with
        modified contents from _configure operation

    Return:
        Succsss || Failure, TYPE: bool
    """
    try:
        # write new exclusion list to local disk
        with open(expath, 'w') as f1:
            list(filter(lambda x: f1.write(x + '\n'), newlist))

    except OSError as e:
        fx = inspect.stack()[0][3]
        stdout_message(
            f'{fx}: Problem writing new file type exclusion list: {expath}: {e}',
            prefix='WARN')
        return False
    return True


def continue_operation(offset_spaces):
    offset = '\t'.expandtabs(offset_spaces)
    msg = '{}Continue?  [quit]'.format(offset)
    answer = input(msg)
    if not answer or answer in ('quit', 'q', 'no', 'No'):
        return False
    return True


def _configure_remove(expath, exdirpath):
    """
        Remove file type extension from exclusion list

    Return:
        Succsss || Failure, TYPE: bool
    """
    delay_seconds = 2
    tabspaces = 4
    tab4 = '\t'.expandtabs(tabspaces)
    loop = True
    adj = tabspaces * 2

    try:

        # open current file type exclusions
        with open(expath) as f1:
            f2 = [x.strip() for x in f1.readlines()]

        while loop:
            width = _init_screen()
            pattern_width = section_header('delete', width, tabspaces=14)
            offset_chars = int((width / 2) - (pattern_width / 2)) + tabspaces
            offset = '\t'.expandtabs(offset_chars)
            display_exclusions(expath, exdirpath, offset_chars)

            answer = input(offset + tab4 + 'Pick the number of a file type to remove [done]: ')

            try:
                if not answer:
                    loop = False
                    sys.stdout.write('\n')
                    return True

                elif int(answer) in range(1, len(f2) + 1):
                    # correct for f2 list index
                    answer = int(answer) - 1
                    # remove entry selected by user
                    deprecated = f2[answer]
                    f2.pop(int(answer))

                    if not _configure_rewrite(expath, f2):
                        return False

                    # Acknowledge removal
                    if str(answer) in f2:
                        stdout_message(
                            message='Failure to remove {} - reason unknown'.format(f2[answer]),
                            indent=offset_chars + adj,
                            prefix='FAIL'
                        )
                        sleep(delay_seconds)

                else:
                    max_index = len(f2)
                    stdout_message(
                        message=f'You must pick a number between 1 and {max_index}',
                        prefix='WARN',
                        indent=offset_chars + adj
                    )
                    sleep(delay_seconds)
            except ValueError:
                continue

    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False


def _configure_hicount(expath, exdirpath):
    """
        User update high line count threshold persisted on local filesystem

    Returns:
        Success || Failure, TYPE: bool

    """
    def _exit(loop_break):
        leave = input('Exit? [quit]')
        if not leave or 'q' in leave:
            loop_break = False
            return True
        return loop_break

    tab4 = '\t'.expandtabs(4)
    tab13 = '\t'.expandtabs(13)
    loop = True
    local_linecount_file = local_config['CONFIG']['COUNT_HI_THRESHOLD_FILEPATH']
    adj = 12

    try:
        width = _init_screen()
        pattern_width = section_header('threshold', width, tabspaces=14)
        offset_chars = int((width / 2) - (pattern_width / 2))
        offset = '\t'.expandtabs(offset_chars)

        while loop:

            if os.path.exists(local_linecount_file):
                with open(local_linecount_file) as f1:
                    threshold = int(f1.read().strip())

            stdout_message(
                message='Current high line count threshold: {}{}{}'.format(bdwt, threshold, rst),
                indent=offset_chars + adj
                )
            answer = input(f'{tab4}{offset}{tab13}Enter high line count threshold [{threshold}]: ')

            try:
                if not answer:
                    stdout_message(
                            f'High line count threshold remains {threshold}',
                            prefix='ok',
                            indent=offset_chars + adj
                        )
                    loop = False
                    return mainmenu_return(offset)

                elif 'q' in answer:
                    loop = False
                    return mainmenu_return(offset)

                elif type(int(answer)) is int:
                    # rewrite threshold file on local filesystem
                    with open(local_linecount_file, 'w') as f1:
                        f1.write(str(answer) + '\n')
                    stdout_message(
                            message='high line count threshold set to {}'.format(answer),
                            prefix='ok',
                            indent=offset_chars + adj
                        )
                    loop = False
                    return mainmenu_return(offset)

                else:
                    stdout_message(
                            message='You must enter an integer number',
                            prefix='INFO',
                            indent=offset_chars + adj
                        )
            except ValueError:
                pass
    except OSError:
        fx = inspect.stack()[0][3]
        logger.exception(f'{fx}: Problem reading local hicount threshold file. Abort')
        return False
    return True


def mainmenu_return(offset):
    """Return control to configuration main menu"""
    tab = '\t'.expandtabs(17)
    answer = input(f'{offset}{tab}Return to main menu [enter]: ')
    if not answer or answer in ('yes', 'Yes'):
        return True
    return False
