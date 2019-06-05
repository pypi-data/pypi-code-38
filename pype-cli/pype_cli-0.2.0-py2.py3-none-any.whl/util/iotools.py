# -*- coding: utf-8 -*-
"""I/O utilities."""

from os import environ, listdir, name, path
from re import IGNORECASE, match
from subprocess import call, run


def get_environ_without_pythonpath():
    """Get os.environ but with variable PYTHONPATH deleted."""
    environ_copy = environ.copy()
    del environ_copy['PYTHONPATH']
    return environ_copy


def run_interactive(cmdline, reset_pythonpath=False, *args, **kwargs):
    """Call to an interactive shell."""
    if not isinstance(cmdline, str):
        cmdline = ' '.join(cmdline)
    env = get_environ_without_pythonpath() if reset_pythonpath else environ
    try:
        return call(cmdline, shell=True, env=env, *args, **kwargs)
    except KeyboardInterrupt:
        pass


def run_and_get_output(cmdline, reset_pythonpath=False, *args, **kwargs):
    """Run a cmdline non-interactive and returns both stdout and stderr."""
    env = get_environ_without_pythonpath() if reset_pythonpath else environ
    if isinstance(cmdline, str):
        # For convenvience we split str-cmdlines into a list which is
        # required for run(). Note that this might not work due to
        # quoted arguments etc.
        cmdline = cmdline.split(' ')
    proc = run(cmdline, capture_output=True, env=env, *args, **kwargs)
    return proc.stdout.decode('utf-8'), proc.stderr.decode('utf-8')


def open_with_default(filepath):
    """Open the given filepath with the OS'es default editor."""
    try:
        # Use open command
        run(['open', filepath], check=True)
    except FileNotFoundError:
        # If not possible try to find $EDITOR or $VISUAL environment var
        editor = environ.get('EDITOR', None)
        if not editor:
            editor = environ.get('VISUAL', None)
        if not editor:
            print('Open with default editor is not supported on this OS.')
            exit(1)
        run_interactive([editor, filepath])


def resolve_path(relative_path):
    """Resolve path including home folder expanding."""
    return path.abspath(path.expanduser(relative_path))


def get_immediate_subdirs(file_path, pattern=None, ignorecase=False):
    """Return the immediate subdirectories of a path."""
    return get_immediate_subfiles(
        file_path, pattern, ignorecase, is_file=False)


def get_immediate_subfiles(
        file_path, pattern=None, ignorecase=False, is_file=True):
    """Return the immediate subfiles of a path."""
    if not file_path:
        raise TypeError('file_path not provided.')

    files = []
    for file_name in listdir(file_path):
        path_is_dir = path.isdir(path.join(file_path, file_name))
        if (path_is_dir and is_file) or (not path_is_dir and not is_file):
            continue
        if pattern:
            if ignorecase and match(pattern, file_name, IGNORECASE):
                files.append(file_name)
            elif match(pattern, file_name):
                files.append(file_name)
            continue
        files.append(file_name)
    files.sort()
    return files


def clear_screen():
    """Clear terminal window."""
    call('clear' if name == 'posix' else 'cls')
