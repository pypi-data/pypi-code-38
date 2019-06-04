# -*- coding: utf-8 -*-
import logging
import os
import sys

is_python2 = sys.version_info[0] == 2
pypi_request_timeout_seconds = 3.0

logger = logging.getLogger('missinglink')


#  taken from python 3.3 source code
def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.
    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    """
    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, current_mode):
        return os.path.exists(fn) and os.access(fn, current_mode) and not os.path.isdir(fn)

    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    if os.path.dirname(cmd):
        if _access_check(cmd, mode):
            return cmd
        return None

    if path is None:
        path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for current_dir in path:
        normal_dir = os.path.normcase(current_dir)
        if normal_dir not in seen:
            seen.add(normal_dir)
            for the_file in files:
                name = os.path.join(current_dir, the_file)
                if _access_check(name, mode):
                    return name
    return None


def _validate_user_path(index_of_path=None, path_insert=None):
    import site
    getusersitepackages = getattr(site, 'getusersitepackages', None)

    if getusersitepackages is None:
        return None

    paths = getusersitepackages() or []
    if len(paths) == 0:
        logging.info('getusersitepackages has no user paths')
        return None

    user_site_packages = getusersitepackages()
    if isinstance(user_site_packages, (list, tuple)):
        user_site_packages = user_site_packages[0]

    index_of_path = index_of_path or sys.path.index

    try:
        index_of_path(user_site_packages)
    except ValueError:
        path_insert = path_insert or sys.path.insert
        path_insert(0, user_site_packages)
        return True

    return False


def in_venv():
    if hasattr(sys, 'real_prefix'):
        # virtualenv venvs
        result = True
    else:
        # PEP 405 venvs
        result = sys.prefix != getattr(sys, 'base_prefix', sys.prefix)

    return result


def _get_pip_command():
    def does_pip3_exist():
        return which('pip3') is not None

    is_python3 = sys.version_info[0] == 3

    if is_python3 and does_pip3_exist():
        return 'pip3'

    return 'pip'


def get_pip_host(staging):
    return 'https://test.pypi.org' if staging else 'https://pypi.org'


def get_pip_index_url(staging):
    return 'https://test.pypi.org/simple/' if staging else None
