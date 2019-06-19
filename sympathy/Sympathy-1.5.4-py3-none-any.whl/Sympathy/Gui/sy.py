# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys

import Gui.application
import Gui.settings
from Gui.log import setup_loglevel
from sympathy.platform import arg_parser
from sympathy.platform import version_support as vs


APPLICATION_DIR = vs.OS.environ['SY_APPLICATION_DIR']
SY_PYTHON_SUPPORT = vs.OS.environ['SY_PYTHON_SUPPORT']


# Place holder for parsed arguments.
args = None


def excepthook(exit_after_exception):
    org_excepthook = sys.excepthook
    excepthook_has_run = [False]

    def inner(exctype, value, traceback):
        if excepthook_has_run[0]:
            return
        excepthook_has_run[0] = True
        if org_excepthook:
            org_excepthook(exctype, value, traceback)
        sys.stdout.flush()
        sys.stderr.flush()
        if exit_after_exception:
            sys.exit(1)

    return inner


def setting_to_unicoded_path(key, settings):
    value = settings.get(key, [])
    if isinstance(value, list):
        return os.pathsep.join([x for x in value])
    else:
        return value


def append_to_path(env_path, new_path):
    # Don't append if new_path is an empty string.
    if not new_path:
        return env_path
    elif not env_path:
        return new_path
    else:
        return u'{0}{1}{2}'.format(env_path, os.pathsep, new_path)


def setup_win32(application_dir, env_path):
    """Windows specific settings. Paths to the bundled Python is setup
    properly.
    """
    python_base_dir = vs.py_file(os.path.dirname(sys.executable))
    paths = [
        python_base_dir,
        os.path.join(python_base_dir, 'Scripts'),
        os.path.join(python_base_dir, 'Lib', 'site-packages', 'PySide'),
        os.path.join(python_base_dir, 'Lib', 'site-packages',
                     'pywin32_system32'),
        os.path.join(python_base_dir, 'Lib', 'site-packages', 'numpy', 'core'),
        env_path]
    return os.pathsep.join(path for path in paths if path != '')


def use_platform_setting(win32, other):
    return win32 if sys.platform == 'win32' else other


def read_from_settings_and_update_environment(
        settings_key, env_key, settings, sy_environment):
    settings_path = setting_to_unicoded_path(settings_key, settings)
    sy_environment[env_key] = append_to_path(
        sy_environment[env_key], settings_path)


def setup_extras(sy_environment):
    """Update environment with extra settings if available."""
    settings = Gui.settings.Settings(args.extras_inifile)
    # Append extras.ini settings (if any) to PATH.
    # Append extras.ini settings (if any) to PYTHONPATH.
    for settings_key, env_key in [('path', 'PATH'),
                                  ('Python/python_path', 'PYTHONPATH')]:
        read_from_settings_and_update_environment(
            settings_key, env_key, settings, sy_environment)


def setup_environment():
    """Setup environment needed for Sympathy to execute. Paths and
    other environment variables are loaded depending on the system
    and the settings available.
    """
    env_path = vs.OS.environ['PATH']
    try:
        del os.environ['PATH']
    except KeyError:
        pass
    # Add application directory to PATH.
    new_env_path = append_to_path(APPLICATION_DIR, env_path)
    if sys.platform == 'win32':
        new_env_path = setup_win32(APPLICATION_DIR, new_env_path)

    sy_environment = {
        'SY_VALID_STARTUP': '1',
        'SY_PYTHON_SUPPORT': SY_PYTHON_SUPPORT,
        'PYTHONPATH': '',
        'PATH': new_env_path
    }

    # Read and update the current environment with optional settings
    # located at disk (if any).
    if args and args.extras_inifile is not None:
        setup_extras(sy_environment)

    vs.OS.environ.update(sy_environment)


def execute_sympathy(sympathy_app):
    """A utility function to execute Sympathy and read the return value
    independently of the host system.
    """
    setup_loglevel(args.loglevel, args.node_loglevel)
    if sympathy_app == 'syg':
        return Gui.application.start_syg(args, sys.argv)
    elif sympathy_app == 'sy':
        return Gui.application.start_sy(args, sys.argv)


def parse_arguments(using_gui=False, known=False):
    parser = arg_parser.instance(using_gui)
    global args
    args = parser.parse_args(known=known)
    if args.filename:
        # Make absolute.
        args.filename = os.path.abspath(args.filename)


def run_binary(sympathy_app):
    parse_arguments(sympathy_app == 'syg')
    sys.excepthook = excepthook(args.exit_after_exception)
    setup_environment()
    returncode = execute_sympathy(sympathy_app)
    sys.exit(returncode)


def run(sympathy_app):
    run_binary(sympathy_app)


def run_function(function):
    setup_environment()
    return function()


if __name__ == '__main__':
    run_binary()
