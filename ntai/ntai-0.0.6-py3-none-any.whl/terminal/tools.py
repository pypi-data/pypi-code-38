import os, sys, subprocess, uuid
from .utils import variable_name, error_message
from .popen import POPEN_DEFAULTS


def line_arg(arg, name=None):
    if name is None: name = variable_name(arg)
    return '{} {}'.format(name, arg)

def short_arg(arg, name=None):
    return '-{}'.format(line_arg(arg, name)).split(' ')

def long_arg(arg, name=None):
    return '--{}'.format(line_arg(arg, name)).split(' ')

def flag_arg(flag, name=None, short=True):
    if name is None: name = variable_name(flag)
    dashes = '-' if short else '--'
    return '{}{}'.format(dashes, name) if flag else ''

def clean_command(command:list):
    cleaned = [
        sub
        for part in command
        for sub in part.split(' ')
        if sub != ''
    ]
    return cleaned



def process(command:list, stdin:str, popen_options={}):
    '''
    Arguments:
        command (list): a list of strings indicating the command and its
            arguments to spawn as a subprocess.

        stdin (str): passed as stdin to the subprocess. Assumed to be utf-8
            encoded.

        popen_options (dict): used to configure the subprocess.Popen command

    Returns:
        stdout, stderr
    '''
    command = clean_command(command)
    popen_config = POPEN_DEFAULTS.copy()
    popen_config.update(popen_options)
    try:
        pid = subprocess.Popen(args = command, **popen_config)
        stdout_data, stderr_data = pid.communicate(stdin)
    except OSError as err:
        error_message(command, err)
        sys.exit(1)
    if pid.returncode != 0:
        error_message(command, 'pid code {}'.format(pid.returncode), stdout_data, stderr_data)
    return stdout_data, stderr_data
