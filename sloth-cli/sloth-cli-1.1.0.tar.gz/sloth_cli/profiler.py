import cProfile
import os
import pstats
import subprocess
from functools import wraps

PROFILE_OUTPUT_FILE = 'profileOutput.profile'


def run(filename: str, lines: int, sort: str, **kwargs):
    """
    Runs cProfile for the script filename and prints the data based on the sort
    specified.

    :param filename:
        The script file name. E.g.: tester.py
    :param lines:
        The number of lines to print
    :param sort:
        How to sort the values: time, cumulative, calls, and filename. Defaults
        to cumulative'
    :param kwargs:
        Additional kwargs
    """
    absolute_path = os.path.abspath(filename)
    directory = os.path.dirname(absolute_path)
    os.chdir(directory)

    cmd = kwargs.get('cmd') or []
    is_help_command = (
        True if set(cmd).intersection({'-h', '--help'})
        else False
    )
    try:
        cmd = [
            'python3', '-m', 'cProfile', '-o', PROFILE_OUTPUT_FILE, filename
        ]
        if kwargs.get('cmd'):
            cmd.extend(kwargs['cmd'])
        print('CMD:', ' '.join(cmd))
        subprocess.run(cmd).check_returncode()
        if not is_help_command:
            p = pstats.Stats(PROFILE_OUTPUT_FILE)
            p.strip_dirs().sort_stats(sort).print_stats(lines)
    finally:
        if not is_help_command:
            os.remove(PROFILE_OUTPUT_FILE)


def profile(
    enable: bool = False,
    sort: str = 'cumulative',
    lines: int = 100,
    builtins: bool = False
):
    """
    Decorates the function to gather time spent in functions. This can be turned
    on by using the environment variable SLOTH_PROFILE='True' or by using this
    function enable variable

    :param enable:
        To gather time using cProfile
    :param lines:
        The number of lines to print
    :param sort:
        How to sort the values: time, cumulative, calls, and filename. Defaults
        to cumulative'
    :param builtins:
        To include builtins or not
    """
    def profile_decorator(func):
        @wraps(func)
        def profile_wrapper(*args, **kwargs):
            is_on = enable or os.environ.get('SLOTH_PROFILE') == 'True'
            pr = cProfile.Profile()
            if is_on:
                pr.enable(builtins=builtins)
            func(*args, **kwargs)
            if is_on:
                pr.disable()
                pstats.Stats(
                    pr
                ).strip_dirs().sort_stats(sort).print_stats(lines)
        return profile_wrapper
    return profile_decorator
