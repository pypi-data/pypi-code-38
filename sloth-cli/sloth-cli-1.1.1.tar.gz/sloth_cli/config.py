import os

my_directory = os.path.realpath(os.path.dirname(__file__))


def get_path(*args: str) -> str:
    """Returns a joined path relative to the root of this package"""
    return os.path.realpath(os.path.join(my_directory, *args))
