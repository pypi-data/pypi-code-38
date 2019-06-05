# -*- coding: utf-8 -*-

import os


def is_windows_containers():
    return os.environ.get('ML_WINDOWS_CONTAINERS') is not None
