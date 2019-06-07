"""

atomtools.file

process all file related



fileobj is frequently used
fileobj could be a StringIO, a string
extension is a string ".xxxx"
"""


import os
from io import StringIO




def get_file_content(fileobj):
    """
    get content of fileobj
    """
    if isinstance(fileobj, StringIO):
        return fileobj.read()
    elif isinstance(fileobj, str):
        if os.path.exists(fileobj): # a filename
            return open(fileobj, 'r').read()
        else:
            return fileobj


def get_filename(fileobj):
    if isinstance(fileobj, StringIO):
        return None
    elif isinstance(fileobj, str):
        if os.path.exists(fileobj): # a filename
            return fileobj
        else:
            return None

def get_extension(fileobj):
    filename = get_filename(fileobj)
    if filename is None:
        return None
    return os.path.splitext(filename)[-1]



