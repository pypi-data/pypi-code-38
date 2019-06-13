import os
import shutil
from distutils import dir_util
from collections.abc import Iterable   # import directly from collections for Python < 3.3



def clean_dir(dir_path):
    print("cleaning ",dir_path)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

def force_copy_tree(src,dst):
    dir_util.copy_tree(src,dst,preserve_symlinks=1)

def copy_as_softlink(src,dst):
    pass
    
def check_exist(data_name):
    if type(data_name)==str:
        assert(os.path.exists(os.path.abspath(data_name)))
    else:
        for obj in data_name:
            check_exist(obj)
    