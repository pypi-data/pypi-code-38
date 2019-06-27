"""

atomtools.file

process all file related



fileobj is frequently used
fileobj could be a StringIO, a string
extension is a string ".xxxx"
"""


import os
import time
from io import StringIO
import chardet



MAX_FILENAME_LENGTH = 200
MAX_DETECT_LENGTH = 300000
MAX_ACTIVE_TIME = 3600




def get_file_content(fileobj):
    """
    get content of fileobj
    """
    if hasattr(fileobj, 'read'):
        fileobj.seek(0)
        return fileobj.read().replace('\r', '')
    elif isinstance(fileobj, str):
        if len(fileobj) < MAX_FILENAME_LENGTH and os.path.exists(fileobj): # a filename
            with open(fileobj, 'rb') as fd:
                data = fd.read()
            code = chardet.detect(data[:MAX_DETECT_LENGTH])['encoding']
            return data.decode(code).replace('\r', '')
        else:
            return fileobj
    else:
        raise ValueError('fileobj should be filename/filecontent/StringIO object')


def get_filename(fileobj):
    if hasattr(fileobj, 'read'):
        return getattr(fileobj, 'name', None)
    elif isinstance(fileobj, str):
        if len(fileobj) < MAX_FILENAME_LENGTH:
            return os.path.basename(fileobj)
        else:
            return None # a string has no filename
    else:
        raise ValueError('fileobj should be filename/filecontent/StringIO object')


def get_file_basename(fileobj):
    return os.path.splitext(get_filename(fileobj))[0]



def get_extension(fileobj):
    filename = get_filename(fileobj)
    if filename is None:
        return None
    return os.path.splitext(filename)[-1]



def get_time_since_lastmod(filename):
    filename = get_filename(filename)
    if not os.path.exists(filename):
        return 0
    return time.time() - os.stat(filename).st_mtime



def file_active(filename):
    filename = get_filename(filename)
    lastmod = get_time_since_lastmod(filename)
    if lastmod > MAX_ACTIVE_TIME:
        return False
    return True



def file_exist(filename):
    filename = get_filename(filename)
    if filename is None:
        return False
    return os.path.exists(filename)

