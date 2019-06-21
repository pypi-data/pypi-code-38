#!/usr/bin/env python
import os

from utils2devops.tools.file import opened_w_error


def get_long_description_from_file(path: str, filename: str) -> str:
    """
    get long description from file

    :param path: the path of the file
    :param filename: the name of the file
    :return: The description contained in the file or the error string
    """
    with opened_w_error(os.path.join(path, filename)) as (f, err):
        # https://www.python.org/dev/peps/pep-0343/
        if err:
            return "get_long_description_from_file: " + err.strerror
        else:
            long_description = f.read().strip()
            return long_description
