"""
Specific guidance for this use case:
  https://stackoverflow.com/a/24176022
More comprehensive guidance:
  https://docs.python.org/3.7/library/contextlib.html
"""
from contextlib import contextmanager
from os import chdir, getcwd, path

class Directory():
    """Provide file system directory operations"""

    @staticmethod
    @contextmanager
    def cd(newdir):
        """
        In a context, change to newdir. Exiting that context, return to prevdir.
        Behaves similarly to pushd/popd on Linux.
        """
        prevdir = getcwd()
        chdir(path.expanduser(newdir))
        try:
            yield
        finally:
            chdir(prevdir)
