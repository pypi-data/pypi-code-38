import os
import pstats
import subprocess

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
