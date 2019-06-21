#!/usr/bin/env python

import os
import re
from typing import Optional

from utils2devops.tools.file import opened_w_error


def get_version(path: str, filename: Optional[str] = 'version.py') -> str:
    """
    Return package version as listed in `__version__` in `init.py`.
    :param path: the path of the file
    :param filename: the name of the file
    :return: string package version
    """
    with opened_w_error(os.path.join(path, filename)) as (f, err):
        # https://www.python.org/dev/peps/pep-0343/
        if err:
            return "get_version: " + err.strerror
        else:
            init_py = f.read().strip()
            return re.search(
                "__version__ = ['\"]([^'\"]+)['\"]",
                init_py
            ).group(1)
