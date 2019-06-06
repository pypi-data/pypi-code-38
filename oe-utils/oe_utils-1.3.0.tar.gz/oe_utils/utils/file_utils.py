# -*- coding: utf8 -*-
import os
import datetime
import math


def get_last_modified_date(filename):
    """
    Get the last modified date of a given file

    :param filename: string: pathname of a file
    :return: Date
    """
    if os.path.isfile(filename):
        t = os.path.getmtime(filename)
        return datetime.date.fromtimestamp(t).strftime('%d/%m/%Y')
    return None


def get_file_size(filename):
    """
    Get the file size of a given file

    :param filename: string: pathname of a file
    :return: human readable filesize
    """
    if os.path.isfile(filename):
        return convert_size(os.path.getsize(filename))
    return None


def convert_size(size_bytes):
    """
    Transform bytesize to a human readable filesize

    :param size_bytes: bytesize
    :return: human readable filesize
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
