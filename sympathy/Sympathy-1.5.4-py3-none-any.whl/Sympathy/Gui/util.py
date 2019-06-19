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
"""
Utility functions
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
import os
import sys
import collections
import logging
import datetime
import unicodedata
import shutil
import PySide.QtGui as QtGui

from . import version
from . import settings
from sympathy.utils.prim import nativepath, absolute_paths
from sympathy.platform import version_support as vs
from sympathy.utils import process


core_logger = logging.getLogger('core')

LOG = False
call_level = 0


class OrderedSet(object):

    def __init__(self, items=None):
        if items:
            self._data = collections.OrderedDict.fromkeys(items)
        else:
            self._data = collections.OrderedDict()

    def add(self, item):
        self._data[item] = None

    def remove(self, item):
        del self._data[item]

    def update(self, items):
        for item in items:
            self.add(item)

    def __iter__(self):
        return iter(self._data.keys())


class Component(object):
    def __init__(self, ctypes=None):
        self._ctypes = ctypes or []
        self._comps = {}

    def register(self, component):
        if self._ctypes:
            ctypes = [ctype for ctype in self._ctypes if
                      isinstance(component, ctype)]
        else:
            ctypes = [None]

        for ctype in ctypes:
            components = self._comps.setdefault(ctype, [])
            if component not in components:
                components.append(component)

    def get(self, ctype=None):
        return list(self._comps.get(ctype, []))


def log_info(f):
    """Decorator - put around a function to log when called."""
    if core_logger.isEnabledFor(logging.INFO):
        return f

    def logged(*args, **kwargs):
        global call_level
        args_to_print = [six.text_type(a) for a in args]
        indent = ' ' * (2 * call_level)
        call_level += 1
        core_logger.info(
            '{}@CALLING {}:{}():{} ARGS ({}), {} '.format(
                indent,
                f.func_code.co_filename, f.func_name,
                f.func_code.co_firstlineno + 1, ', '.join(args_to_print),
                kwargs))
        retval = f(*args, **kwargs)
        if hasattr(retval, '__iter__'):
            core_logger.info('{}@RETURNING {}: {}'.format(
                indent, f.func_name, [six.text_type(a) for a in retval]))
        else:
            core_logger.info('{}@RETURNING {}: {}'.format(
                indent, f.func_name, six.text_type(retval)))
        call_level -= 1
        return retval
    return logged


def log_message(message, data=None, level=logging.INFO):
    if core_logger.isEnabledFor(level):
        core_logger.log(level, message if data is None else '{} {}'.format(
            message, vs.str_(data)))


def log_critical_message(message, data=None):
    log_message(message, data, logging.CRITICAL)


def log_info_message(message, data=None):
    log_message(message, data, logging.INFO)


def log_debug_message(message, data=None):
    log_message(message, data, logging.DEBUG)


def datetime_to_time_string(datetime_):
    return datetime_.strftime('%Y-%m-%d-%H-%M-%S-%f')


def time_string_to_datetime(time_string):
    try:
        return datetime.datetime.now().strptime(time_string,
                                                '%Y-%m-%d-%H-%M-%S-%f')
    except ValueError:
        # Fallback support for old, bad time format which was missing seconds.
        return datetime.datetime.strptime(
            time_string, '%Y-%m-%d-%H-%M-%f')


def now_time_string():
    return datetime_to_time_string(datetime.datetime.now())


def sessions_folder():
    return settings.instance()['temp_folder']


def create_session_folder():
    temp_folder = sessions_folder()
    vs.OS.environ['SY_TEMP'] = nativepath(temp_folder)
    try:
        # Create the temp folder if it does not exist.
        os.makedirs(temp_folder)
    except OSError:
        pass

    pid_str = str(os.getpid()).encode('ascii')

    while True:
        # Making sure to create a unique session folder.
        session_folder = os.path.join(temp_folder, now_time_string())
        try:
            os.makedirs(session_folder)
        except OSError:
            pass
        else:
            break

    with open(os.path.join(session_folder, 'owner'), 'wb') as f:
        # Create owner file used during cleanup.
        f.write(pid_str)

    vs.OS.environ['SY_TEMP_SESSION'] = nativepath(session_folder)
    settings.instance()['session_folder'] = session_folder


def remove_sessions_folder():
    temp_folder = settings.instance()['temp_folder']
    shutil.rmtree(temp_folder)


def create_default_folder():
    default_folder = settings.instance()['default_folder']
    vs.OS.environ['SY_DEFAULT'] = nativepath(default_folder)
    try:
        # Create the default folder if it does not exist.
        os.makedirs(default_folder)
    except OSError:
        pass


def storage_folder(storage=None):
    version_ = 'py{}-{}.{}.{}'.format(
        sys.version_info[0], version.major, version.minor, version.micro)
    if storage is None:
        storage = os.path.normpath(QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.StandardLocation.DataLocation))
    return os.path.normpath(os.path.join(storage, version_))


def create_storage_folder(storage=None):
    storage_folder_ = storage_folder(storage)
    try:
        # Create the temp folder if it does not exist.
        os.makedirs(storage_folder_)
    except OSError:
        pass
    settings.instance()['storage_folder'] = storage_folder_
    vs.OS.environ['SY_STORAGE'] = nativepath(storage_folder_)


def remove_storage_folders():
    shutil.rmtree(storage_folder())


ICON_PATH = None


def icon_path(icon):
    global ICON_PATH
    if ICON_PATH is None:
        if 'resource_folder' not in settings.instance():
            setup_resource_folder()
        ICON_PATH = os.path.join(
            settings.instance()['resource_folder'], 'icons')
    return os.path.join(ICON_PATH, icon)


def create_install_folder():
    install_folder = vs.OS.environ['SY_APPLICATION_DIR']
    settings.instance()['install_folder'] = install_folder


def setup_resource_folder():
    settings.instance()['resource_folder'] = os.path.abspath(
        os.path.join(vs.py_file_dir(__file__), 'Resources'))


def remove_duplicates(items):
    res = []
    for item in items:
        if item not in res:
            res.append(item)
    return res


def _parent_root_flows(flow):
    flows = []
    prev = None

    while flow is not None and flow is not prev:
        prev = flow
        flow = flow.root_or_linked_flow()
        flows.append(flow)
        flow = flow.flow
    return flows


def library_paths(flow=None):
    install_folder = settings.instance()['install_folder']
    paths = absolute_paths(install_folder, ['Internal'])
    paths.extend(_global_paths('Python/library_path'))
    if flow:
        paths.extend([p for f in _parent_root_flows(flow)
                      for p in f.library_paths(True)])
    else:
        paths.extend(_flow_paths('Python/workflow_library_paths'))
    return [unicodedata.normalize('NFC', path)
            for path in remove_duplicates(paths)]


def python_paths(flow=None):
    paths = _global_paths('Python/python_path')
    if flow:
        paths.extend([p for f in _parent_root_flows(flow)
                      for p in f.python_paths(True)])
    else:
        paths.extend(_flow_paths('Python/workflow_python_paths'))
    return remove_duplicates(paths)


def _global_paths(global_key):
    settings_ = settings.instance()
    install_folder = settings_['install_folder']
    return absolute_paths(
        install_folder, settings_[global_key])


def _flow_paths(workflow_key):
    settings_ = settings.instance()
    paths = []
    if workflow_key in settings_:
        for workflow_paths in settings_[workflow_key].values():
            for path in workflow_paths:
                if path not in paths:
                    paths.append(path)
    return paths


@six.python_2_unicode_compatible
class Enum(object):
    def __init__(self, index, value):
        self._index = index
        self._value = value

    @property
    def name(self):
        return self._value

    @property
    def index(self):
        return self._index

    def __str__(self):
        return self._value


def make_enum(name, *fields):
    """
    Generate a new enum class inheriting from EnumBase.
    The class has the following properties:

    New instances can be created using the provided names.
    numbered and named namames must be strings.

    On successive constructions with the same name, the same instance is always
    returned.
    """
    return collections.namedtuple(
        name, fields)(*[Enum(i, field) for i, field in enumerate(fields)])


def post_execution():
    """Perform temporary folder clean-up after the application has finished."""
    def date_list(file_list):
        return sorted((
            time_string_to_datetime(
                os.path.basename(f_name)),
            f_name) for f_name in file_list)

    def size_list(file_list):
        result = []
        for date, f_name in file_list:
            size = 0
            for root_, dirs_, files_ in os.walk(f_name):
                try:
                    size += sum([os.stat(os.path.join(root_, f)).st_size
                                 for f in files_])
                    result.append((f_name, size))
                except OSError:
                    pass
        return result

    settings_ = settings.instance()

    temp_folder = settings_['temp_folder']
    if not os.path.exists(temp_folder):
        return

    max_folders = settings_['max_temp_folder_number']

    folders = [os.path.join(temp_folder, d)
               for d in os.listdir(temp_folder)]
    folders = [d for d in folders
               if os.path.basename(d).startswith('20') and os.path.isdir(d)]

    remove_dirs = folders
    # Remove folders with dates older than today minus the given age limit.
    dates = date_list(folders)
    if not settings_['remove_temp_files'] and not settings_.get(
            'clear_caches'):
        date_limit = (datetime.datetime.now() -
                      datetime.timedelta(settings_['max_temp_folder_age']))

        if max_folders:
            keep = dates[-max_folders:]
            remove = dates[:-max_folders]
        else:
            keep = dates
            remove = []

        expired = 0
        for date, fname in keep:
            if date < date_limit:
                expired += 1
            else:
                break

        if expired:
            remove += keep[:expired]
            keep = keep[expired:]

        # Remove folders with if the specified size limit is exceded.
        max_size = settings_['max_temp_folder_size']
        size_limit = int(max_size[:-1])
        modifier = max_size[-1]
        if modifier in ('k', 'K'):
            size_limit *= 1024
        elif modifier in ('M', 'm'):
            size_limit *= 1024 ** 2
        elif modifier in ('G', 'g'):
            size_limit *= 1024 ** 3

        cumulative_size = 0
        remove_dirs = [fname for date, fname in remove]
        for fname, size in reversed(size_list(keep)):
            cumulative_size += size
            if cumulative_size >= size_limit:
                remove_dirs.append(fname)

    remove_own_session = False
    session_folder = os.path.abspath(settings.instance()['session_folder'])

    for dir_name in remove_dirs:
        owner = os.path.join(dir_name, 'owner')
        if vs.samefile(session_folder, dir_name):
            remove_own_session = True
        else:
            if process.expire(owner, 10):
                shutil.rmtree(dir_name, ignore_errors=True)
            elif process.age(dir_name) > 10 and not os.path.exists(owner):
                shutil.rmtree(dir_name, ignore_errors=True)

    if remove_own_session:
        shutil.rmtree(session_folder, ignore_errors=True)
    else:
        try:
            os.remove(os.path.join(session_folder, 'owner'))
        except:
            pass

    storage_folder = settings_['storage_folder']

    if settings_.get('clear_caches'):
        if storage_folder:
            shutil.rmtree(storage_folder, ignore_errors=True)

    if settings_.get('clear_settings'):
        settings_.clear()
