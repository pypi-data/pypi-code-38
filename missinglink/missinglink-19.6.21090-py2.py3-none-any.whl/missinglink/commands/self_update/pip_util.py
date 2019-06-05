# -*- coding: utf-8 -*-
import json
import os
import sys
import logging
import requests

is_python2 = sys.version_info[0] == 2


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


def pip_install(pip_server, require_package, user_path):
    from subprocess import Popen, PIPE

    pip_bin_path = which('pip')
    if pip_bin_path is None:
        python_bin_path = sys.executable
        pip_bin_path = os.path.join(os.path.dirname(python_bin_path), 'pip')
        if not os.path.exists(pip_bin_path):
            logging.warning("pip not found, can't self update missinglink sdk")
            return None, None

    if user_path:
        args = (pip_bin_path, 'install', '--upgrade', '--user', '-i', pip_server, require_package)
    else:
        args = (pip_bin_path, 'install', '--upgrade', '-i', pip_server, require_package)

    # noinspection PyBroadException
    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE), args


def get_pip_server(keywords):
    pypi_server_hostname = 'testpypi' if 'test' in keywords else 'pypi'

    return 'https://{hostname}.python.org/pypi'.format(hostname=pypi_server_hostname)


def get_latest_pip_version(package, keywords, throw_exception=False):
    try:
        pypi_server = get_pip_server(keywords)

        url = '{server}/{package}/json'.format(server=pypi_server, package=package)
        r = requests.get(url)  # allows to use requests

        r.raise_for_status()

        package_info = json.loads(r.text)

        return package_info['info']['version']
    except Exception as e:
        if throw_exception:
            raise

        logging.exception('could not check for new missinglink-sdk version:\n%s', e)
        return None
