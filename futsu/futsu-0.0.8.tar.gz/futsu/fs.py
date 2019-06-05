import os
import shutil
import filecmp

def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def reset_dir(out_dir):
    shutil.rmtree(out_dir,ignore_errors=True)
    os.makedirs(out_dir)

def diff(fn0,fn1):
    return not filecmp.cmp(fn0,fn1)
