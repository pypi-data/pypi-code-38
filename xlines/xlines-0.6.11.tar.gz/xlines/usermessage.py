"""
Python3 Module

Facility for printing messages to stdout
    - Python3 only
    - Developed & Tested under Python3.6

Message Prefixes:

     Status                 Color
  -----------------      ------------------
    - INFO                  Cyan (DEFAULT)
    - ERROR                 Red
    - WARN                  Orange
    - OK                    Green
    - <user defined>        Cyan

Severity
"""
import inspect
from xlines.colors import Colors


# prefix handling
critical_status = ('ERROR', 'FAIL', 'WTF', 'STOP', 'HALT', 'EXIT', 'F*CK')
warning_status = (
    'WARN', 'WARNING', 'CAUTION', 'SLOW', 'DBUG', 'DEBUG', 'AUTH')


def stdout_message(message, prefix='INFO', quiet=False, multiline=False, indent=4, severity=''):
    """
    Summary:
        Prints message to cli stdout while indicating type and severity

    Args:
        :message (str): text characters to be printed to stdout
        :prefix (str):  4-letter string message type identifier.
        :quiet (bool):  Flag to suppress all output
        :multiline (bool): indicates multiline message; removes blank lines
            on either side of printed message
        :indent (int): left justified number of spaces to indent before
            printing message ouput
        :severity (str): header status msg determines color instead of prefix

    .. code-block:: python

        # Examples:

            - INFO (default)
            - ERROR (error, problem occurred)
            - WARN (warning)
            - NOTE (important to know)

    Returns:
        TYPE: bool, Success (printed) | Failure (no output)
    """
    prefix = prefix.upper()
    tabspaces = int(indent)

    if quiet:

        return True

    else:

        try:

            if prefix in critical_status or severity.upper() == 'CRITICAL':
                header = (Colors.YELLOW + '\t[ ' + Colors.RED + prefix +
                          Colors.YELLOW + ' ]' + Colors.RESET + ': ')

            elif prefix in warning_status or severity.upper() == 'WARNING':
                header = (Colors.YELLOW + '\t[ ' + Colors.ORANGE + prefix +
                          Colors.YELLOW + ' ]' + Colors.RESET + ': ')

            elif prefix in ('OK') or severity.upper() == 'OK':
                header = (Colors.YELLOW + '\t[  ' + Colors.BOLD + Colors.GREEN + prefix +
                          Colors.YELLOW + '  ]' + Colors.RESET + ': ')

            elif prefix in ('DONE', 'GOOD') or severity.upper() == 'OK':
                header = (Colors.YELLOW + '\t[ ' + Colors.BOLD + Colors.GREEN + prefix +
                          Colors.YELLOW + ' ]' + Colors.RESET + ': ')

            else:    # default color scheme
                header = (Colors.YELLOW + '\t[ ' + Colors.DARK_CYAN + prefix +
                          Colors.YELLOW + ' ]' + Colors.RESET + ': ')

            if multiline:
                print(header.expandtabs(tabspaces) + str(message))
            else:
                print('\n' + header.expandtabs(tabspaces) + str(message) + '\n')

        except Exception as e:
            print(f'{inspect.stack()[0][3]}: Problem sending msg to stdout: {e}')
            return False

    return True
