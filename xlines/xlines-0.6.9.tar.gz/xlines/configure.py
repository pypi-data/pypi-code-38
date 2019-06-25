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
from xlines.statics import PACKAGE, local_config
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


def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear')
    return True


def section_header(section, tabspaces=12):
    """
    Prints section header title and function ("section") with border
    """
    if section.lower() in ('add', 'delete'):
        title = '{} File Type Exclusions Menu'.format(bdwt + section.title() + rst)
    else:
        title = 'high line count {} update'.format(bdwt + section + rst)

    border = bbl
    tab = '\t'.expandtabs(tabspaces)
    tab4 = '\t'.expandtabs(4)
    print(border + tab4 + '____________________________________________\n' + rst)
    print('{}{}'.format(tab, title))
    print(border + tab4 + '____________________________________________\n' + rst)
    return True


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

        stdout_message(message='File types excluded from line counts:')

        for index, ext in enumerate(exclusions):
            print('{}{:>3}{}'.format(tab, index + 1, div + '  ' + ext))

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
        clearscreen()
        print(border + '''
        ________________________________________________________________________________
        ''' + rst + '''

            ''' + bdwt + PACKAGE + rst + ''' configuration main menu:


                  ''' + icolor + 'a' + rst + ''')  Add file type to exclusion list

                  ''' + icolor + 'b' + rst + ''')  Remove file type from exclusion list

                  ''' + icolor + 'c' + rst + ''')  Set high line count threshold (''' + acct + 'highlight' + rst + ''' file objects)

                  ''' + icolor + 'd' + rst + ''')  quit
        ''' + border + '''
        ________________________________________________________________________________
        ''' + rst)
    loop = True
    tab8 = '\t'.expandtabs(8)

    while loop:
        menu()
        answer = input('\n{}Choose operation [quit]: '.format(tab8)).lower()
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
    loop = True

    try:

        with open(expath) as f1:
            exclusions = [x.strip() for x in f1.readlines()]

        while loop:

            clearscreen()
            section_header('add')
            display_exclusions(expath, exdirpath)
            # query user input for new exclusions
            response = input('  Enter file extension types separated by commas [done]: ')

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


def _configure_remove(expath, exdirpath):
    """
        Remove file type extension from exclusion list

    Return:
        Succsss || Failure, TYPE: bool
    """
    tab4 = '\t'.expandtabs(4)
    tab8 = '\t'.expandtabs(8)
    loop = True

    try:

        # open current file type exclusions
        with open(expath) as f1:
            f2 = [x.strip() for x in f1.readlines()]

        while loop:
            clearscreen()
            section_header('delete', tabspaces=10)
            display_exclusions(expath, exdirpath)

            answer = input(tab4 + 'Pick the number of a file type to remove [done]: ')

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
                        indent=16,
                        prefix='FAIL'
                    )
                else:
                    stdout_message(
                        message='Successfully removed file type exclusion: {}'.format(deprecated),
                        indent=16,
                        prefix='ok'
                    )

            else:
                max_index = len(f2)
                stdout_message(
                    message=f'You must pick a number between 1 and {max_index}',
                    prefix='WARN'
                )
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
    tab8 = '\t'.expandtabs(8)
    loop = True
    local_linecount_file = local_config['CONFIG']['COUNT_HI_THRESHOLD_FILEPATH']

    try:
        clearscreen()
        section_header('threshold', tabspaces=10)

        while loop:

            if os.path.exists(local_linecount_file):
                with open(local_linecount_file) as f1:
                    threshold = int(f1.read().strip())

            stdout_message(message='Current high line count threshold is {}{}{}'.format(bdwt, threshold, rst))
            answer = input(f'{tab4}Enter high line count threshold [{threshold}]: ')

            try:
                if not answer:
                    stdout_message(f'High line count threshold remains {threshold}', prefix='ok')
                    sys.exit(exit_codes['EX_OK']['Code'])

                elif 'q' in answer:
                    loop = False
                    return True

                elif type(int(answer)) is int:
                    # rewrite threshold file on local filesystem
                    with open(local_linecount_file, 'w') as f1:
                        f1.write(str(answer) + '\n')
                    stdout_message(message='high line count threshold set to {}'.format(answer), prefix='ok')
                    sys.exit(exit_codes['EX_OK']['Code'])

                else:
                    stdout_message(message='You must enter an integer number', prefix='INFO')
            except ValueError:
                pass
    except OSError:
        fx = inspect.stack()[0][3]
        logger.exception(f'{fx}: Problem reading local hicount threshold file. Abort')
        return False
    return True
