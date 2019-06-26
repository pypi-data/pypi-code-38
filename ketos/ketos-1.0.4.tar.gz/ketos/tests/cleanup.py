"""This program cleans the temporary files created by tests. """

import shutil
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(current_dir, 'assets/tmp')

if os.path.exists(path_to_tmp):
    shutil.rmtree(path_to_tmp)
os.makedirs(path_to_tmp)