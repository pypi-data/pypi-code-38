import re
import ast
import errno
from os import listdir, makedirs
from os.path import exists, isfile, join, isdir
from datetime import datetime
from collections.abc import Mapping

DATE_FORMAT = "%Y_%m_%d_%H%M%S"

def getDateTimestampAndString():
    datetimeObj = datetime.now()
    return (datetimeObj.timestamp(), datetimeObj.strftime(DATE_FORMAT))

def strToTimestamp(str_time):
    return datetime.strptime(str_time, DATE_FORMAT).timestamp()

def yesNoPrompt(msg):
    return re.search("[Yy]$", input(msg))

def overwritePrompt(files):
    exs = list(filter(exists, files))
    if len(exs) == 0: return True
    print('\n'.join(exs))
    return yesNoPrompt("Are you sure to overwrite the above files/dirs?[y/n]")

def deletePrompt(files):
    exs = list(filter(exists, files))
    if len(exs) == 0: print("Nothing to be delete..."); return True
    print('\n'.join(exs))
    return yesNoPrompt("Are you sure to delete the above files/dirs?[y/n]")

def to_class_name(name):
    return ''.join(x.title() for x in re.split('-|_', name))

# Credit: https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise

# Credit: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def list_files(dirPath):
    if exists(dirPath):
        return [ f for f in listdir(dirPath) if isfile(join(dirPath, f)) ]
    # raise Exception('%s dir not exist....' % (dirPath))
    return []

def force_number(s):
    try:
        return ast.literal_eval(s)
    except:
        return s

# https://stackoverflow.com/questions/32935232/python-apply-function-to-values-in-nested-dictionary
def map_nested_dicts_modify(ob, func):
    for k, v in ob.items():
        if isinstance(v, Mapping):
          map_nested_dicts_modify(v, func)
        else:
          ob[k] = func(v)

def map_nested_dicts_modify_key(ob, func):
    newOb = {}
    for k, v in ob.items():
        if isinstance(v, Mapping):
            newOb[func(k)] = map_nested_dicts_modify_key(v, func)
        else:
            newOb[func(k)] = v
    return newOb