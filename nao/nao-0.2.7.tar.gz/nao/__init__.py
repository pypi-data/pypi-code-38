"""
Universal tools enhancing Python

Not related to any third party packages

The aim is to contribute these pieces into other
major projects
"""
import os
import re
import sys
import time
import pathlib
import contextlib
import collections
import yaml as pyyaml


__version__ = '0.2.7'


@contextlib.contextmanager
def chdir(path):
    """Change directory temporarily"""
    old_dir = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(old_dir)


@contextlib.contextmanager
def benchmark(arg):
    """Measure time inside with statement"""
    # TODO use log instead
    print("Benchmark <{}> started...".format(arg))
    begin = time.time()
        
    try:
        yield 
    finally:
        last = human_time(time.time() - begin)
        print("Benchmark <{}> finished in: {}".format(arg, last))


def human_time(seconds):
    """Format seconds human readably

    TODO use `babel.dates.format_timedelta` with `datetime.timedelta(seconds=...)`
    """
    t = []
    
    if seconds > 60*60:
        hours, seconds = divmod(seconds, 60*60)
        t.append("{:.0f}h".format(hours))
    
    if seconds > 60:
        mins, seconds = divmod(seconds, 60)
        t.append("{:.0f}m".format(mins))

    t.append("{:.3f}s".format(seconds))

    return ' '.join(t)



# import time
# import functools
# import contextlib


# # TIMING CONTEXTMANAGER AND DECORATOR
# def benchmark(arg):

#     # print('ba', arg, callable(arg))

#     # normal use returns a context manager
#     if not callable(arg):
#         return Benchmark(str(arg))

#     # decorator use: wrapped into a benchmark context
#     func = arg
#     @functools.wraps(func)
#     def wrapper(*args, **kwds):
#         with Benchmark('FUNC ' + func.__name__):
#             return func(*args, **kwds)

#     return wrapper

# class Benchmark(object):
#     """
#     Based on something similar found long time ago on the internet
#     """
#     def __init__(self, name):
#         self._name = name
#         self._time = None

#     def __enter__(self):
#         self._begin = time.time()
#         print("Benchmark <{}> started ...".format(self._name))
          # return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         self._time = time.time()-self._begin
#         print("Benchmark <{}> finished in: {}".format(self._name, self.time))
#         return False

#     @property
#     def time(self, raw=False):
#         if time is None:
#             raise ValueError('Not run yet')

#         return self._time if raw else human_time(self._time)
    





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Recursive dictionary and list update
# TODO add support for list append
# move this to separate python package and import it from there


def recursive_update(base, other, recurse_lists=True):
    """
    Recursively updates base with other.

    Appends to lists as well.

    Returns the updated base data structure

    """
    if dictlike(base, other):
        for key, value in other.items():
            if key in base:
                base[key] = recursive_update(base[key], value)
            else:
                base[key] = value

    if listlike(base, other):
        if recurse_lists:
            for val in other:
                try:
                    idx = base.index(val)
                except ValueError:
                    base.append(val)
                else:
                    base[idx] = recursive_update(base[idx], val)
        else:
            base.extend(other)

    if setlike(base, other):
        for val in other:
            base.add(val)

    return base


def dictlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (dict,)): return False
    return True

def listlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (list,)): return False
    return True

def setlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (set,)): return False
    return True



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# OrderedDict YAML version
# from https://github.com/wimglenn/oyaml
# hopefully it will soon gets integrated into pyYAML
# Python 3.7 supports ordered dict natively
# check for native C YAML lib for optimization
# v0.2.1

_items = 'viewitems' if sys.version_info < (3,) else 'items'


def map_representer(dumper, data):
    return dumper.represent_dict(getattr(data, _items)())


def map_constructor(loader, node):
    loader.flatten_mapping(node)
    return odict(loader.construct_pairs(node))


if pyyaml.safe_dump is pyyaml.dump:
    # PyYAML v4.1
    SafeDumper = pyyaml.dumper.Dumper
    DangerDumper = pyyaml.dumper.DangerDumper
    SafeLoader = pyyaml.loader.Loader
    DangerLoader = pyyaml.loader.DangerLoader
else:
    SafeDumper = pyyaml.dumper.SafeDumper
    DangerDumper = pyyaml.dumper.Dumper
    SafeLoader = pyyaml.loader.SafeLoader
    DangerLoader = pyyaml.loader.Loader

pyyaml.add_representer(dict, map_representer, Dumper=SafeDumper)
pyyaml.add_representer(collections.OrderedDict, map_representer, Dumper=SafeDumper)
pyyaml.add_representer(dict, map_representer, Dumper=DangerDumper)
pyyaml.add_representer(collections.OrderedDict, map_representer, Dumper=DangerDumper)


if sys.version_info < (3, 7):
    pyyaml.add_constructor('tag:yaml.org,2002:map', map_constructor, Loader=SafeLoader)
    pyyaml.add_constructor('tag:yaml.org,2002:map', map_constructor, Loader=DangerLoader)


del map_constructor, map_representer


# public function overrides
def yaml_load(stream):
    if isinstance(stream, pathlib.Path):
        return pyyaml.load(stream.open(), Loader=SafeLoader)
    return pyyaml.load(stream, Loader=SafeLoader)

def yaml_dump(data, stream=None, **kwds):
    kwds.setdefault('default_flow_style', False)
    if isinstance(stream, pathlib.Path):
        with stream.open('w') as x:
            return pyyaml.dump_all([data], x, **kwds)
    return pyyaml.dump_all([data], stream, **kwds)

def yaml_print(*args, **kwds):
    if len(args) == 1:
        print(yaml_dump(args[0]))
    else:
        print(yaml_dump(args))
    if kwds:
        print(yaml_dump(kwds))



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Convert to under_score style


u1reg = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
u2reg1 = re.compile(r'(.)([A-Z][a-z]+)')
u2reg2 = re.compile(r'(a-z0-9])([A-Z])')

def underscore(text, method='single_reg'):
    """
    Largely based on Stack Overflow.
    Two methods are only implemented out of curiosity.

    Converts `CamelCase` or `camelCase` to under_score style.
    Able to handle `camelAndHTTPResponse` as `camel_and_http_response`.
    Avoids multiple underscores, so `under_Score` remains `under_score`
    does not become `under__score`.
    """

    if method == 'single_reg':
        return u1reg.sub(r'_\1', text).lower().replace('__', '_')

    if method == 'double_reg':
        temp = u2reg1.sub(r'\1_\2', text)
        return u2reg2.sub(r'\1_\2', temp).lower().replace('__', '_')

    raise ValueError("Method not recognized: {}".format(method))


# replace all fancy characters with underscore

def to_filename(name):
    return re.sub(r'[^\w\-_\.]', '_', str(name))


# padding strings
def padded(string, spaces=4):

    return '\n'.join([' '*spaces+l for l in string.split('\n')])

# flatten Python data structure
def flatten(d, parent_key='', sep='.'):
    """
    FROM http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten(d):
    """
    TODO implement
    """



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Quaternion implementation

# import numpy as np

# class Quaternion:
#     """Quaternions for 3D rotations"""
#     def __init__(self, x):
#         self.x = np.asarray(x, dtype=float)
        
#     @classmethod
#     def from_v_theta(cls, v, theta):
#         """
#         Construct quaternion from unit vector v and rotation angle theta
#         """
#         theta = np.asarray(theta)
#         v = np.asarray(v)
        
#         s = np.sin(0.5 * theta)
#         c = np.cos(0.5 * theta)
#         vnrm = np.sqrt(np.sum(v * v))  # np.linalg.norm ???

#         # print([c], s*v/vnrm)

#         q = np.concatenate([[c], s * v / vnrm])
#         # print('raw data', q)
#         return cls(q)

#     def __repr__(self):
#         return "Quaternion:\n" + self.x.__repr__()

#     def __mul__(self, other):
#         # multiplication of two quaternions.
#         prod = self.x[:, None] * other.x

#         return self.__class__([(prod[0, 0] - prod[1, 1]
#                                  - prod[2, 2] - prod[3, 3]),
#                                 (prod[0, 1] + prod[1, 0]
#                                  + prod[2, 3] - prod[3, 2]),
#                                 (prod[0, 2] - prod[1, 3]
#                                  + prod[2, 0] + prod[3, 1]),
#                                 (prod[0, 3] + prod[1, 2]
#                                  - prod[2, 1] + prod[3, 0])])

#     def as_v_theta(self):
#         """Return the v, theta equivalent of the (normalized) quaternion"""
#         # compute theta
#         norm = np.sqrt((self.x ** 2).sum(0))
#         theta = 2 * np.arccos(self.x[0] / norm)

#         # compute the unit vector
#         v = np.array(self.x[1:], order='F', copy=True)
#         v /= np.sqrt(np.sum(v ** 2, 0))

#         return v, theta

#     def as_rotation_matrix(self):
#         """Return the rotation matrix of the (normalized) quaternion"""
#         v, theta = self.as_v_theta()
#         c = np.cos(theta)
#         s = np.sin(theta)

#         return np.array([[v[0] * v[0] * (1. - c) + c,
#                           v[0] * v[1] * (1. - c) - v[2] * s,
#                           v[0] * v[2] * (1. - c) + v[1] * s],
#                          [v[1] * v[0] * (1. - c) + v[2] * s,
#                           v[1] * v[1] * (1. - c) + c,
#                           v[1] * v[2] * (1. - c) - v[0] * s],
#                          [v[2] * v[0] * (1. - c) - v[1] * s,
#                           v[2] * v[1] * (1. - c) + v[0] * s,
#                           v[2] * v[2] * (1. - c) + c]]) 