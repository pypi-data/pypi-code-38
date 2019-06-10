from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join, dirname, realpath, basename
import json
from os.path import splitext

import yaml



def load_test_config():
    task_path = join(dirname(realpath(__file__)), "test_config.yaml")
    with open(task_path) as f:
        config = yaml.load(f)

    return config


