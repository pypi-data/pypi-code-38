import os

__all__ = [
    'get_data_folder',
    'get_file_path',
]


def get_data_folder():
    """
    Returns the absolute path to the data directory.
    """
    return os.path.dirname(os.path.abspath(__file__))


def get_file_path(name):
    """
    Returns the Error Solver file path for the specified file name. If the
    file name does not include the `.ef` extension, the extension will be
    added.

    Parameters
    ----------
    name : str
        The file name.
    """
    return os.path.join(get_data_folder(), name)
