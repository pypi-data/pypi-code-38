import os


class UnknownFileType(Exception):
    pass


class ImportFailed(Exception):
    pass


def get_file_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]
