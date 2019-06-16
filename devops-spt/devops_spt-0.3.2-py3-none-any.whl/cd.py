"""
Specific guidance for this use case:
  https://stackoverflow.com/a/24176022
More comprehensive guidance:
  https://docs.python.org/3.7/library/contextlib.html
"""
from contextlib import contextmanager
import os

@contextmanager
def chdir(newdir):
    """
    In a context, change to newdir. Exiting that context, return to prevdir.
    Behaves similarly to pushd/popd on Linux.
    """
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
