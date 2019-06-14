from re      import sub
from os      import walk, mkdir, rename, remove
from sys     import stderr
from shutil  import rmtree
from os.path import isfile, isdir, join, basename, splitext, exists
from filecmp import dircmp

import mekpie.debug    as debug
import mekpie.messages as messages

from .cli import panic, log

# Numerical
# ---------------------------------------------------------------------------- #

def clamp(value, bottom, top):
    return max(bottom, min(top, value))

# Collections
# ---------------------------------------------------------------------------- #

def empty(collection):
    return len(collection) == 0

def first(collection):
    if not empty(collection):
        return collection[0]

def rest(collection):
    if not empty(collection):
        return collection[1:]

def last(collection):
    if not empty(collection):
        return collection[-1]

def shift(collection, n=1):
    for _ in range(n):
        if not empty(collection):
            collection.pop(0)

def flatten(collection):
    return sum(collection, [])

def split(collection, item):
    if item not in collection:
        return collection, []
    index  = collection.index(item)
    first  = collection[:index]
    second = collection[index + 1:] 
    return first, second


# Strings
# ---------------------------------------------------------------------------- #

def tab(string, spaces=4):
    return sub(r'^|\n', '\n' + (spaces * ' '), string)

def underline(element, collection):
    top    = ' '.join(collection)
    bottom = ' '.join(underlined_collection(element, collection))
    return f'{top}\n{bottom}'

def underlined_collection(underlined_element, collection):
    def underline_or_hide(element):
        rep = '^' if element == underlined_element else ' '
        return sub(r'.', rep, str(element))
    return map(underline_or_hide, collection)

# Files
# ---------------------------------------------------------------------------- #

def smkdir(path):
    log(f'Creating directory {path}...')
    if not exists(path):
        mkdir(path)

def srmtree(path):
    if exists(path):
        rmtree(path)


def smv(source, destination):
    log(f'Moving {source} to {destination}')
    remove(destination)
    if exists(source):
        rename(source, destination)

def list_files(path, with_filter=None, with_ext=None, recursive=False):
    if with_filter is None:
        with_filter = lambda _ : True
    if with_ext is not None:
        with_filter = lambda filename : filename.endswith(with_ext)
    return list(filter(with_filter, list_all_files(path)))

def list_all_files(path):
    return flatten([[join(pre, post)
            for post
            in posts]
        for (pre, _, posts)
        in walk(path)
    ])

def list_all_dirs(path):
    return flatten([[join(path, pre)
            for pre 
            in pres]
        for (_, pres, posts)
        in walk(path)
    ])

def filename(path):
    return splitext(basename(path))[0]

def file_as_str(path):
    check_is_file(path)
    log(f'Reading the contents of {path}...')
    with open(path) as resource:
        return resource.read()

def remove_contents(path):
    log(f'Deleting the contents of {path}...')
    srmtree(path)
    smkdir(path)

def check_is_file(path):
    if isfile(path):
        return path
    panic(messages.file_not_found.format(path))

def check_is_dir(path):
    if isdir(path):
        return path
    panic(messages.directory_not_found.format(path))

def same_dir(dir1, dir2):
    def recursive(dcmp):
        if dcmp.diff_files:
            return False
        return all([recursive(sub_dcmp)
            for sub_dcmp
            in dcmp.subdirs.values()
        ])
    return recursive(dircmp(dir1, dir2))

def exec_str(source, handle, ctx={}):
    try:
        exec(source, ctx)
    except Exception as err:
        panic(messages.execution_error.format(handle, tab(str(err))))
    return ctx

def exec_file(path, ctx={}):
    return exec_str(file_as_str(path), path, ctx)

# Types
# ---------------------------------------------------------------------------- #

def type_name(x):
    return type(x).__name__
