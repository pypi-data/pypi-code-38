import numbers
import os
import re
from numbers import Number

from . import find, parse


try:
    from collections import Optional
except ImportError:
    Optional = None


def get(package_directory_or_setup_script=None):
    # type: (Optional[str]) -> Union[str, float, int]
    """
    Get the version # of a package
    """
    setup_script_path = find.setup_script_path(package_directory_or_setup_script)

    for setup_call in parse.SetupScript(setup_script_path).setup_calls:

        try:
            version = setup_call['version']
            break
        except KeyError:
            pass

    return version


def increment(package_directory_or_setup_script=None, amount=None):
    # type: (Optional[str],Optional[Union[str, int, Sequence[int]]]) -> bool
    """
    Increment the version # of the referenced package by the least significant amount possible
    """

    if isinstance(amount, int):
        amount = (amount,)
    elif isinstance(amount, str):
        amount = tuple(int(i) for i in amount.split('.'))
    elif isinstance(amount, numbers.Number):
        amount = tuple(int(i) for i in str(amount).split('.'))

    setup_script_path = find.setup_script_path(package_directory_or_setup_script)

    with parse.SetupScript(setup_script_path) as setup_script:

        for setup_call in setup_script.setup_calls:

            try:
                version = setup_call['version']
            except KeyError:
                version = None

            if isinstance(version, str):

                dot_version_etc = re.split(r'([^\d.]+)', version)

                if dot_version_etc:

                    dot_version = dot_version_etc[0]
                    etc = ''.join(dot_version_etc[1:])
                    version_list = list(dot_version.split('.'))
                    if amount:
                        version_list_length = len(version_list)
                        for index in range(len(amount)):
                            if index < version_list_length:
                                version_list[index] += amount[index]
                            else:
                                version_list[index].append(amount[index])
                    else:
                        version_list[-1] = str(int(version_list[-1]) + 1)
                    new_version = '.'.join(version_list) + etc

                    setup_call['version'] = new_version

            elif isinstance(version, int):

                setup_call['version'] += 1

            elif isinstance(version, Number):

                version_string = str(version)

                if '.' in version_string:
                    setup_call['version'] += 1.0/(10.0**len(version_string.split('.')[-1]))
                else:
                    setup_call['version'] += 1

        modified = setup_script.save()

    return modified
