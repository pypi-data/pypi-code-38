#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import os.path

import yaml

__version__ = '0.0.6'


def _load_conf():
    from joker.default import under_home_dir
    paths = [under_home_dir('.m14-default.yml'), '/etc/m14-default.yml']
    for path in paths:
        if os.path.isfile(path):
            return yaml.load(open(path))
    return {}


def under_default_dir(package, *paths):
    conf = _load_conf()
    name = getattr(package, '__name__', str(package)).split('.')[-1]
    try:
        dir_ = conf[name]
    except LookupError:
        dir_ = os.path.join(conf.get('default', '/data'), name)
    return os.path.join(dir_, *paths)


