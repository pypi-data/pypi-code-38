import contextlib
import os
import sys


@contextlib.contextmanager
def cd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    except:
        print('Exception caught: ', sys.exc_info()[0])
    finally:
        os.chdir(cwd)
