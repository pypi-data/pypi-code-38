# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import os
import getpass
import sys

try:
    import pwd
except ImportError:
    pwd = None


def python_version_string():
    try:
        return sys.version.split("\n")[0]
    except Exception:
        return None


def current_username():
    if pwd:  # not available on windows
        return pwd.getpwuid(os.geteuid()).pw_name

    return getpass.getuser()


def current_user_id():
    return os.getuid()


def current_process_id():
    return os.getpid()


def current_group_id():
    return str(os.getegid())


def get_packages(callback=None):
    try:
        from pip import get_installed_distributions
    except ImportError:
        # pip decided to hide this internal api in version 10.0.0+
        from pip._internal.utils.misc import get_installed_distributions

    installed_packages = get_installed_distributions()
    for installed_package in installed_packages:
        if callback:
            callback(installed_package)
    return installed_packages
