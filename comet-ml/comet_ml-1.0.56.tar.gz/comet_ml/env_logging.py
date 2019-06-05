# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Boris Feld

This module contains the functions dedicated to logging the environment
information

"""

import getpass
import logging
import os
import platform
import socket
import sys

import netifaces
from comet_ml.connection import get_backend_address
from six.moves.urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)


def get_pid():
    return os.getpid()


def get_hostname():
    return socket.gethostname()


def get_os():
    return platform.platform(aliased=True)


def get_os_type():
    return platform.system()


def get_python_version_verbose():
    return sys.version


def get_python_version():
    return platform.python_version()


def get_user():
    return getpass.getuser()


def get_network_interfaces_ips():
    try:
        ips = []
        for interface in netifaces.interfaces():
            for link in netifaces.ifaddresses(interface).get(netifaces.AF_INET, []):
                ips.append(link["addr"])
        return ips

    except Exception:
        LOGGER.warning("Failed to log all interfaces ips", exc_info=True)
        return None


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = get_backend_address()
        parsed = urlparse(server_address)
        host = parsed.hostname
        port = parsed.port
        if port is None:
            port = {"http": 80, "https": 443}.get(parsed.scheme, 0)
        s.connect((host, port))
        addr = s.getsockname()[0]
        s.close()
        return addr

    except socket.error:
        LOGGER.warning("Failed to log ip", exc_info=True)
        return None


def get_command():
    return sys.argv


def get_env_details():
    return {
        "pid": get_pid(),
        "hostname": get_hostname(),
        "os": get_os(),
        "os_type": get_os_type(),
        "python_version_verbose": get_python_version_verbose(),
        "python_version": get_python_version(),
        "user": get_user(),
        "network_interfaces_ips": get_network_interfaces_ips(),
        "ip": get_ip(),
        "command": get_command(),
        "python_exe": sys.executable,
    }
