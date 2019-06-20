import os
import struct
import setuptools.command.easy_install
from pkg_resources import resource_string


def is_64bit():
    return struct.calcsize("P") == 8


def get_win_launcher(type):
    """
    Load the Windows launcher (executable) suitable for launching a script.

    `type` should be either 'cli' or 'gui'

    Returns the executable as a byte string.
    """
    launcher_fn = "%s%s.exe" % (
        ('w' if type == "gui" else 't'), 
        ('64' if is_64bit() else '32')
    )
    return resource_string('windows_entry_exe', launcher_fn)


_orig = setuptools.command.easy_install.get_win_launcher


def enable(dist, kw, en):
    if en:
        setuptools.command.easy_install.get_win_launcher = get_win_launcher
    else:
        setuptools.command.easy_install.get_win_launcher = _orig
