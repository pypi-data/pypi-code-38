import os
import sys


def is_in_virtualenv():
    """
    Returns ``True`` if we are in a virtualenv.
    """
    return hasattr(sys, 'real_prefix')


def get_virtualenv_directory():
    """
    Get the root directory of the current virtualenv.

    Raises OSError if not in a virtualenv.
    """
    if is_in_virtualenv():
        return os.path.abspath(sys.prefix)
    else:
        raise OSError('Not in a virtualenv.')


def add_virtualenv_bin_directory_to_path():
    """
    Add :func:`get_virtualenv_directory` to ``os.environ['PATH']``.

    Why do we need this? This is used to work around limitations
    in how certain IDE's implement virtualenv support. They may
    add the virtualenv to PYTHONPATH, but to to PATH.
    """
    bin_directory = os.path.join(get_virtualenv_directory(), 'bin')
    if bin_directory not in os.environ['PATH'].split(os.pathsep):
        os.environ["PATH"] += os.pathsep + bin_directory
