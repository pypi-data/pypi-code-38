"""
Summary.

    Userdata module: displays userdata script files found
    on the local filesystem from which user can choose

"""

import os
import sys
import json
import inspect
from pyaws.utils import stdout_message, userchoice_mapping
from pyaws import Colors
from ec2tools.statics import local_config
from ec2tools import logd, __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes


logger = logd.getLogger(__version__)


def range_test(min, max, value):
    """
    Summary.

        Tests value to determine if in range (min, max)

    Args:
        :min (int):  integer representing minimum acceptable value
        :max (int):  integer representing maximum acceptable value
        :value (int): value tested

    Returns:
        Success | Failure, TYPE: bool

    """
    if isinstance(value, int):
        if value in range(min, max + 1):
            return True
    return False


def choose_resource(choices, selector='letters', default='a'):
    """

    Summary.

        validate user choice of options

    Args:
        :choices (dict): lookup table by key, for value selected
            from options displayed via stdout

    Returns:
        user selected resource identifier
    """
    def safe_choice(sel_index, user_choice):
        if sel_index == 'letters':
            return user_choice
        elif isinstance(user_choice, int):
            return user_choice
        elif isinstance(user_choice, str):
            try:
                return int(user_choice)
            except TypeError:
                return userchoice_mapping(user_choice)

    validate = True

    try:
        while validate:
            choice = input(
                '\n\tEnter a letter to select [%s]: '.expandtabs(8) %
                (choices[userchoice_mapping(default)] if selector == 'letters' else choices[int(default)])
            ) or default

            # prevent entering of letters for choice if numbered selector index
            choice = safe_choice(selector, choice)

            index_range = [x for x in choices]

            if range_test(0, max(index_range), userchoice_mapping(choice) if selector == 'letters' else int(choice)):
                resourceid = choices[userchoice_mapping(choice)] if selector == 'letters' else choices[int(choice)]
                validate = False
            else:
                stdout_message(
                    'You must enter a %s between %s and %s' %
                    (
                        'letter' if selector == 'letters' else 'number',
                        userchoice_mapping(index_range[0]) if selector == 'letters' else index_range[0],
                        userchoice_mapping(index_range[-1]) if selector == 'letters' else index_range[-1]
                    )
                )
    except KeyError:
        resourceid = None
        choice = [k for k, v in choices.items() if v is None]
    except TypeError as e:
        logger.exception(f'Typed input caused an exception. Error {e}')
        sys.exit(1)
    stdout_message('You selected choice {}, {}'.format(choice, resourceid))
    return resourceid
