"""
Load a dict from disk & populate a YacoDict

"""
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import pkg_resources
import sys

import requests
from .core import FantailConf

import yaml

from yaml.representer import Representer

class literal_str(str):
    pass

class literal_unicode(str):
    pass

def literal_str_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

#yaml.add_representer(literal_unicode, literal_unicode_representer)
yaml.add_representer(literal_str, literal_str_representer)

yaml.add_representer(FantailConf, Representer.represent_dict)


PY3 = sys.version_info[0] > 2

lg = logging.getLogger(__name__)
# lg.setLevel(logging.DEBUG)

_demo_object = yaml.safe_load("""
a:
  b1:
    c1: v1
    c2: v2
    c3: v3
  b2: v4
""")

ALLOWED_TXT_EXTENSIONS = """
txt py pl R sh bash
""".strip().split()


def guess_loader(data):
    if isinstance(data, dict):
        return dict_loader
    elif not isinstance(data, str):
        raise Exception("Invalid data type {0} ({1}".format(
            str(data)[:50], type(data)))
    elif data.startswith('http://'):
        return request_loader
    elif data.startswith('https://'):
        return request_loader
    elif os.path.isdir(data):
        return dir_loader
    elif data[:6] == 'pkg://':
        return package_loader
    elif os.path.isfile(data):
        try:
            name, ext = data.rsplit('.', 1)
            if ext.lower() in ['yaml', 'config', 'conf']:
                return yaml_file_loader
            else:
                raise Exception("unknown file type: {0}".format(data))
        except:
            # just go for it :/
            return yaml_file_loader
    elif data[0] == '/' or data[0] == '~':
        # looks like a file or dir - but may not exists..
        return dummy_loader
    else:
        # assume it's just plain yaml
        return yaml_string_loader


def dummy_loader(data):
    """
    Do not do anything - just pretend
    """
    pass


def load(data):
    """
    Generic loader - tries to be smart
    """
    return guess_loader(data)(data)


def dict_loader(dictionary):
    """
    Populate a yaco object from a dictionary
    """
    #lg.debug("load dict %s", " ".join(str(dictionary).split())[:50])

    if isinstance(dictionary, str):
        raise Exception("invalid dictionary: {0}".format(
            str(dictionary)[:80]))
        exit(-1)

    rv = FantailConf()
    rv.update(dictionary)
    return rv


def request_loader(path):
    raw = requests.get(path).text
    return yaml.safe_load(raw)


def yaml_string_loader(data):
    """
    Populate a yaco object from a yaml string
    """
    # lg.debug("load string %s",
    #         b" ".join(data.split())[:50])
    parsed = yaml.safe_load(data)
    return dict_loader(parsed)


def yaml_file_loader(filename):
    """
    Populate a yaco object from a yaml string
    """
    with open(filename) as F:
        data = yaml.safe_load(F)
    return dict_loader(data)


def yaml_file_save(ft_object, filename):
    """
    Save a file to yaml
    """
    lg.debug("saving to %s", filename)
    with open(filename, 'w') as F:
        d = yaml.dump(dict(ft_object),
                      encoding=('ascii'),
                      default_flow_style=False)
        F.write(d.decode('ascii'))


def dir_loader(path):
    """
    Populate a yaco object from a directory of yaml files

    * loading is depth first - this results in values in a
      directory being overwritten by overlapping definitions
      in a file higher in the tree
    * directory names are interpreted as keys in the tree

    """

    rv = FantailConf()

    if not os.path.isdir(path):
        raise Exception("Expected a directory: {0}".format(path))
        return

    for name in os.listdir(path):
        fullpath = os.path.join(path, name)
        basename, file_ext = name, ''
        if '.' in name:
            basename, file_ext = name.rsplit('.', 1)

        load_in_root = False

        if (not basename) or basename[0] == '_':
            load_in_root = True

        if os.path.isdir(fullpath):
            if load_in_root:
                rv.update(dir_loader(fullpath))
            else:
                rv[name] = dir_loader(fullpath)

        elif file_ext.lower() in ['yaml', 'conf', 'config']:
            data = yaml_file_loader(fullpath)
            if load_in_root:
                rv.update(data)
            else:
                rv[basename].update(data)
        elif file_ext.lower() in ['txt', 'py', 'sh', 'bash']:
            with open(fullpath) as F:
                rv[basename] = F.read()
    return rv


def package_loader(uri):
    lg.debug("package load %s", uri)

    ori_uri = uri

    if uri[:6] == "pkg://":
        uri = uri[6:]

    uri = uri.rstrip('/')
    pkg_name, path = uri.split('/', 1)
    try:
        if not pkg_resources.resource_exists(pkg_name, path):
            # requested resource does not exist
            return FantailConf()
    except ModuleNotFoundError as e:
        # or the complete module does not exist -
        return FantailConf()

    # check if we're looking at a single file in a package -
    # if so - load that.
    if not pkg_resources.resource_isdir(pkg_name, path):

        if '/' in path:
            base_path, filename = os.path.split(path)
        else:
            lg.warning("problem?? %s %s %s %s", ori_uri, pkg_name, uri, path)
            base_path, filename = '', path

        if '.' in filename:
            file_base, file_ext = filename.rsplit('.', 1)
        else:
            file_base, file_ext = filename, ''

        data = pkg_resources.resource_string(pkg_name, path)

        if PY3:
            if isinstance(data, bytes):
                data = data.decode('ascii')

        if file_ext in ['yaml', 'conf', 'config']:
            return yaml_string_loader(data)
        elif file_ext in ['txt', '']:
            return data
        elif file_ext in ['pickle']:
            return
        else:
            lg.warning("unknown object in package, ignoring: {0}".format(path))
        return

    # It's a directory
    rv = FantailConf()

    # start loading - depth first - so do directories
    for obj in pkg_resources.resource_listdir(pkg_name, path):
        new_path = os.path.join(path, obj)

        load_in_root = False
        if obj[0] == '_':
            load_in_root = True

        if pkg_resources.resource_isdir(pkg_name, new_path):
            data = package_loader('pkg://{0}/{1}'.format(pkg_name, new_path))
            if load_in_root:
                rv.update(data)
            else:
                rv[obj].update(data)

    # and now files
    for obj in pkg_resources.resource_listdir(pkg_name, path):
        new_path = os.path.join(path, obj)

        if not pkg_resources.resource_isdir(pkg_name, new_path):

            file_base, file_ext = obj, ''
            if '.' in obj:
                file_base, file_ext = obj.split('.', 1)

            load_in_root = False
            if obj[0] == '_':
                load_in_root = True

            if file_ext == 'txt':
                if load_in_root:
                    lg.warning("cannot load txt in root")
                rv[file_base] = package_loader(
                    'pkg://{0}/{1}'.format(pkg_name, new_path))
            elif file_ext in ['yaml', 'conf', 'config']:
                data = package_loader(
                    'pkg://{0}/{1}'.format(pkg_name, new_path))
                if load_in_root:
                    rv.update(data)
                else:
                    rv[file_base].update(data)
            else:
                # ignore
                pass
    return rv
