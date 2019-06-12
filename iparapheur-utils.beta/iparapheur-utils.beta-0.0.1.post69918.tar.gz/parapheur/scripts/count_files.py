#!/usr/bin/env python
# coding=utf-8

from parapheur.parapheur import config
import os
from os import path as os_path

PATH = os_path.abspath(os_path.split(__file__)[0])
script = PATH + "/script/count_files.sh"

os.chmod(script, 0755)

os.system(script)