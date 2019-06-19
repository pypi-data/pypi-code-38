# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import sys
import ctypes
import threading
import subprocess
import re
import logging
import six
import imp
import shutil
from . import qt_compat as qt
from . import version_support as vs
QtCore = qt.QtCore
core_logger = logging.getLogger('core')
cygcore = re.compile('^processor[\t]*: [0-9]*.*$')
fs_encoding = sys.getfilesystemencoding()


def thread_count():
    try:
        import psutil
        try:
            return psutil.NUM_CPUS
        except AttributeError:
            return psutil.cpu_count()
    except ImportError:
        if sys.platform == 'cygwin':
            with open('/proc/cpuinfo') as f:
                count = 0
                for line in f:
                    if cygcore.match(line):
                        count += 1
                return count

        core_logger.debug('Could not determine number of threads.')
        return 1


def Popen(args, **kwargs):
    stdin = kwargs.pop('stdin', None)
    stdout = kwargs.pop('stdout', None)
    stderr = kwargs.pop('stderr', None)
    close_fds = kwargs.pop('close_fds', None)
    env = kwargs.pop('env', None)

    if stdin is None:
        stdin = sys.stdin
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    if close_fds is None:
        close_fds = os.name == 'posix'

    if env:
        env = dict(env.items())

    if six.PY2:
        args = [arg.encode(fs_encoding)
                if isinstance(arg, six.text_type) else arg
                for arg in args]
    else:
        args = [arg if isinstance(arg, six.text_type)
                else arg.decode(fs_encoding)
                for arg in args]

    return subprocess.Popen(args,
                            stdin=stdin,
                            stdout=stdout,
                            stderr=stderr,
                            close_fds=close_fds,
                            **kwargs)


def Popen_no_console(*args, **kwargs):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = kwargs.pop('startupinfo', subprocess.STARTUPINFO())
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    stdin = kwargs.pop('stdin', subprocess.PIPE)
    stdout = kwargs.pop('stdout', subprocess.PIPE)
    stderr = kwargs.pop('stderr', subprocess.PIPE)

    return Popen(*args, stdin=stdin, stdout=stdout, stderr=stderr,
                 startupinfo=startupinfo, **kwargs)


def has_spyder2():
    try:
        imp.find_module('spyderlib')
    except ImportError:
        return False
    return True


def has_spyder3():
    try:
        imp.find_module('spyder')
    except ImportError:
        return False
    return True


def has_spyder():
    return has_spyder2() or has_spyder3()


def run_spyder(filenames=None):
    filenames = filenames or []
    # Starting spyder from user drive root. This should help to avoid unicode
    # characters in that path and probably reduces the likelyhood of getting
    # local python module conflicts.
    cwd = None
    cwd2 = os.path.expanduser('~')
    while cwd != cwd2:
        cwd = cwd2
        cwd2 = os.path.dirname(cwd)

    startup_file = os.path.abspath(os.path.join(
        vs.OS.environ['SY_APPLICATION_DIR'], 'Python', 'sympathy', 'utils',
        'python_startup.py'))

    os.environ['PYTHONPATH'] = '{}{}{}'.format(
        os.environ['PYTHONPATH'],
        os.path.pathsep,
        os.environ['SY_PYTHON_SUPPORT'])
    os.environ['PYTHONSTARTUP'] = startup_file
    Popen(
        [sys.executable, '-c', """
import sys
import os

try:
    from spyderlib import start_app
except ImportError:
    from spyder.app import start as start_app
else:
    from sympathy.platform import os_support
    os_support.set_high_dpi_unaware()

sys.argv = sys.argv[:1] + [arg for arg in sys.argv[1:]]

start_app.main()
""",
         ] + filenames,
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def run_filename(filename):
    if sys.platform.startswith('darwin'):
        args = ['open', filename]
    elif os.name == 'nt':
        args = ['cmd', '/c' 'start', '', filename]
    elif os.name == 'posix':
        args = ['xdg-open', filename]

    return Popen_no_console(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def run_editor(filename):

    if has_spyder():
        run_spyder([filename])
    else:
        run_filename(filename)


if os.name == 'nt':
    import pywintypes
    import win32api
    import win32con
    import win32file
    import win32job
    import win32process
    from ctypes import windll, wintypes
    from six.moves import winreg
    from win32com.client import Dispatch
elif os.name == 'posix':
    import fcntl


class TimeoutError(Exception):
    pass


class IFileLock(object):
    def __init__(self, file_object):
        self._file = file_object

    def aquire(self):
        raise NotImplemented

    def release(self):
        raise NotImplemented

    def __enter__(self):
        self.aquire()

    def __exit__(self, *args):
        self.release()


class FileLockUnix(IFileLock):
    def aquire(self):
        fcntl.fcntl(self._file.fileno(), fcntl.LOCK_EX)

    def release(self):
        fcntl.fcntl(self._file.fileno(), fcntl.LOCK_UN)


class FileLockCygwin(IFileLock):
    def aquire(self):
        core_logger.debug('File lock is not implemented for cygwin.')

    def release(self):
        core_logger.debug('File lock is not implemented for cygwin.')


class FileLockDarwin(IFileLock):
    def aquire(self):
        fcntl.flock(self._file.fileno(), fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)


class FileLockWindows(IFileLock):
    def aquire(self):
        win32file.LockFileEx(win32file._get_osfhandle(self._file.fileno()),
                             win32con.LOCKFILE_EXCLUSIVE_LOCK, 0, -0x10000,
                             pywintypes.OVERLAPPED())

    def release(self):
        try:
            win32file.UnlockFileEx(
                win32file._get_osfhandle(self._file.fileno()),
                0, -0x10000, pywintypes.OVERLAPPED())
        except pywintypes.error as e:
            # Do not fail unlocking unlocked file.
            if e[0] == 158:
                pass
            else:
                raise


class FileLockTimeout(IFileLock):
    def __init__(self, file_object, timeout):
        self.timeout = float(timeout)
        self._file_lock = _file_lock_factory()(file_object)

    def aquire(self):
        def run_aquire():
            self._file_lock.aquire()
            with mutex:
                if done.is_set():
                    self.release()
                done.set()

        mutex = threading.Lock()
        done = threading.Event()
        thread = threading.Thread(target=run_aquire)
        thread.daemon = True
        thread.start()
        thread.join(self.timeout)
        with mutex:
            if not done.is_set():
                done.set()
                raise TimeoutError

    def release(self):
        self._file_lock.release()


class FileLock(IFileLock):
    def __init__(self, file_object, timeout=None):
        self.timeout = timeout
        if timeout is None:
            self._file_lock = _file_lock_factory()(file_object)
        else:
            self._file_lock = FileLockTimeout(file_object, timeout)

    def aquire(self):
        self._file_lock.aquire()

    def release(self):
        self._file_lock.release()


def _file_lock_factory():
    if os.name == 'nt':
        return FileLockWindows
    elif os.name == 'posix':
        if sys.platform == 'darwin':
            return FileLockDarwin
        if sys.platform == 'cygwin':
            return FileLockCygwin
        return FileLockUnix
    assert(False)


class IProcessGroup(object):
    def __init__(self):
        raise NotImplemented

    def add_pid(self, pid):
        raise NotImplemented

    def subprocess_arguments(self):
        raise NotImplemented


class ProcessGroupWindows(IProcessGroup):
    def __init__(self):
        hJob = win32job.CreateJobObject(None, '')
        info = win32job.QueryInformationJobObject(
            hJob, win32job.JobObjectExtendedLimitInformation)
        info['BasicLimitInformation']['LimitFlags'] = (
            win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
        win32job.SetInformationJobObject(
            hJob, win32job.JobObjectExtendedLimitInformation, info)
        self._hJob = hJob

    def add_pid(self, pid):
        hProcess = win32api.OpenProcess(win32con.PROCESS_SET_QUOTA |
                                        win32con.PROCESS_TERMINATE,
                                        False, pid)
        win32job.AssignProcessToJobObject(self._hJob, hProcess)
        win32api.CloseHandle(hProcess)

    def subprocess_arguments(self):
        return {'creationflags': win32process.CREATE_BREAKAWAY_FROM_JOB}


class ProcessGroupUnix(IProcessGroup):
    def __init__(self):
        os.setpgrp()

    def add_pid(self, pid):
        # Currently inherited from the parent process.
        # For more fine grained control or to cover more usecases, this
        # Would have to be refined.
        pass

    def subprocess_arguments(self):
        return {'close_fds': True}


def process_group_factory():
    if os.name == 'nt':
        return ProcessGroupWindows()
    elif os.name == 'posix':
        return ProcessGroupUnix()
    assert(False)


def focus_widget(widget, popup_only=False):
    """
    Brings a widget window into focus on systems where it is needed
    (currently Windows). `popup_only` == True allows to raise the window to
    the top.
    """
    if sys.platform == 'win32':
        null_ptr = ctypes.POINTER(ctypes.c_int)()
        bg_hwnd = widget.winId()
        try:
            bg_pid = ctypes.windll.user32.GetWindowThreadProcessId(
                bg_hwnd, null_ptr)
        except ctypes.ArgumentError:
            ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
            bg_hwnd = ctypes.pythonapi.PyCObject_AsVoidPtr(bg_hwnd)
            bg_pid = ctypes.windll.user32.GetWindowThreadProcessId(
                bg_hwnd, null_ptr)

        fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
        fg_pid = ctypes.windll.user32.GetWindowThreadProcessId(
            fg_hwnd, null_ptr)

        if bg_pid == 0 or fg_pid == 0:
            return

        if ctypes.windll.user32.AttachThreadInput(fg_pid, bg_pid, 1) == 0:
            return

        if ctypes.windll.user32.SetForegroundWindow(bg_hwnd) == 0:
            return

        if not popup_only:
            if ctypes.windll.user32.BringWindowToTop(fg_hwnd) == 0:
                return

        if ctypes.windll.user32.BringWindowToTop(bg_hwnd) == 0:
            return

        if ctypes.windll.user32.AttachThreadInput(fg_pid, bg_pid, 0) == 0:
            return
    elif sys.platform.startswith('linux'):
        widget.setWindowFlags(
            widget.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        widget.raise_()
        widget.setWindowFlags(
            widget.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        widget.show()
        return


def raise_window(widget):
    """
    Raises the window to the top.
    """
    if sys.platform == 'win32':
        if widget.isMinimized():
            widget.showNormal()
        focus_widget(widget, True)
    elif sys.platform.startswith('linux'):
        if widget.isMinimized():
            widget.showNormal()
        old_pos = widget.pos()
        widget.setWindowFlags(
            widget.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        widget.raise_()
        widget.setWindowFlags(
            widget.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        widget.move(old_pos)
        widget.show()
    elif sys.platform == 'darwin':
        widget.raise_()


def set_application_id(identifier='Combine Control Systems AB.Sympathy.SympathyGUI'):
    if sys.platform == 'win32':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                identifier)
        except:
            # Only available on Windows 7 and later.
            pass


CSIDL_STARTMENU = 11
CSIDL_COMMON_STARTMENU = 22


def _path(csidl):
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(0, csidl, 0, 0, buf)
    return buf.value


def create_shortcut(path, target, arguments=None, working_dir=None, icon=None):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target

    if working_dir:
        shortcut.WorkingDirectory = working_dir
    if arguments:
        shortcut.Arguments = arguments

    if icon:
        shortcut.IconLocation = icon
    shortcut.save()


def register_ext(ext, cls, desc, cmd, icon=None, hive=None):
    # Not using default value due to winreg only being available on win32.
    hive = hive or winreg.HKEY_CURRENT_USER
    with winreg.OpenKey(hive, r'Software\Classes') as key:
        extkey = winreg.CreateKey(key, ext)
        winreg.SetValue(extkey, '', winreg.REG_SZ, cls)
        clskey = winreg.CreateKey(key, cls)
        winreg.SetValue(clskey, '', winreg.REG_SZ, desc)
        cmdkey = winreg.CreateKey(clskey, r'shell\open\command')
        winreg.SetValue(cmdkey, '', winreg.REG_SZ, cmd)
        if icon:
            icokey = winreg.CreateKey(clskey, r'DefaultIcon')
            winreg.SetValue(icokey, '', winreg.REG_SZ, icon)


def unregister_ext(ext, cls,  hive=None):
    # Not using default value due to winreg only being available on win32.
    hive = hive or winreg.HKEY_CURRENT_USER
    with winreg.OpenKey(hive, r'Software\Classes') as key:
        paths = [ext]
        path = ['shell', 'open', 'command']

        for i in reversed(range(1, len(path))):
            paths.append('{}\\{}'.format('\\'.join(path[:i + 1]), cls))

        paths.append('{}\\DefaultIcon'.format(cls))
        paths.append(cls)

        for path in paths:
            try:
                winreg.DeleteKey(key, path)
            except OSError:
                pass


def set_high_dpi_unaware():
    if os.name == 'nt':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(0)
        except (AttributeError, OSError):
            # For Windows 8 and later.
            # Older windows, such as, Windows 7 doesn't have this api
            # but fails with OSError.
            pass


def flush_clipboard():
    if os.name == 'nt':
        try:
            ctypes.oledll.ole32.OleFlushClipboard()
        except:
            # Extra caution to avoid failure because of clipboard
            # flushing.
            pass


def register_app(subkey, name, ver, uinst, quinst, publisher, hive=None):
    # Not using default value due to winreg only being available on win32.
    hive = hive or winreg.HKEY_CURRENT_USER
    with winreg.OpenKey(
            hive,
            r'Software\Microsoft\Windows\CurrentVersion\Uninstall') as key:
        uinkey = winreg.CreateKey(key, subkey)
        winreg.SetValueEx(uinkey, 'DisplayName', 0, winreg.REG_SZ, name)
        winreg.SetValueEx(uinkey, 'DisplayVersion', 0, winreg.REG_SZ, ver)
        winreg.SetValueEx(uinkey, 'UninstallString', 0, winreg.REG_SZ, uinst)
        winreg.SetValueEx(uinkey, 'QuietUninstallString', 0, winreg.REG_SZ,
                          quinst)
        winreg.SetValueEx(uinkey, 'Publisher', 0, winreg.REG_SZ, publisher)


def unregister_app(subkey, hive=None):
    # Not using default value due to winreg only being available on win32.
    hive = hive or winreg.HKEY_CURRENT_USER
    with winreg.OpenKey(
            hive,
            r'Software\Microsoft\Windows\CurrentVersion\Uninstall') as key:
        try:
            winreg.DeleteKey(key, subkey)
        except OSError:
            pass


def start_menu(common=False):
    loc = CSIDL_COMMON_STARTMENU if common else CSIDL_STARTMENU
    return _path(loc)


def create_start_menu_shortcuts(path, shortcuts, common=False):
    root = os.path.join(start_menu(common=common), path)
    try:
        os.makedirs(root)
    except OSError:
        pass

    for shortcut in shortcuts:
        name, target, arguments, working_dir, icon = shortcut
        fullpath = os.path.join(root, name)
        if os.path.exists(fullpath):
            os.remove(fullpath)

        create_shortcut(fullpath, target, arguments, working_dir, icon)


def delete_start_menu_shortcuts(path, common=False):
    root = os.path.join(start_menu(common=common), path)
    try:
        shutil.rmtree(root)
    except OSError:
        pass
