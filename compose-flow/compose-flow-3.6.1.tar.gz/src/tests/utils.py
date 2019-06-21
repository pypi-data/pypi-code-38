import os

MODULE_DIR = os.path.dirname(__file__)


def get_content(relative_path: str) -> str:
    """
    Returns the content of the given relative path

    Args:
        relative_path: the path relative to the tests/files/ directory

    Returns:
        the file contents
    """
    full_path = os.path.join(MODULE_DIR, 'files', relative_path)

    with open(full_path) as fh:
        return fh.read()
