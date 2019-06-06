#  encoding: utf-8
from __future__ import absolute_import, division, print_function

import io
import os
import re
import sys
import tempfile
from collections import ChainMap, OrderedDict
from configparser import ConfigParser


class Config(OrderedDict):
    """augments a nested dictionary by accessing keys as attributes + some methods
    for output and to-string conversion.
    """

    __getattr__ = OrderedDict.__getitem__
    __setattr__ = OrderedDict.__setitem__
    __delattr__ = OrderedDict.__delitem__

    def print_(self, indent=0, fh=sys.stdout):
        for (k, v) in self.items():
            if isinstance(v, Config):
                print(" " * indent, "{}:".format(k), file=fh)
                v.print_(indent + 4, fh)
            else:
                print(" " * indent, "{}: {}".format(k, v), file=fh)

    def __str__(self):
        fh = io.StringIO()
        self.print_(0, fh)
        return fh.getvalue()

    def as_dict(self):
        result = OrderedDict()
        for name, value in self.items():
            if isinstance(value, Config):
                value = value.as_dict()
            result[name] = value

        return result

    def __eq__(self, other):
        return isinstance(other, Config) and self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return not (self == other)


class MagicConfig(Config):
    """allows nested setting and access of attributes without explicitly constructing
    the intermediate objects:

    >>> c = Config()
    >>> c.logger.level = 10
    >>> c.logger.file = "~/datapool.config"
    >>> print(c.logger.level)
    >>> 10

    instead of attributes, dictionary key style can be used:
    >>> c.logger["file"] = "~/datapool.config"

    This is only an example, levels might be 1, 2 or more and mixed !
    """

    def __getitem__(self, name):
        if name not in self.keys():
            self[name] = self.__class__()
        return super().__getitem__(name)

    __getattr__ = __getitem__


def write_ini(config, path_or_handle):
    """
    writes a Config object `config` or nested dict (Config is such a nested dict)
    in .ini file style to `path`.
    """
    assert isinstance(config, dict)
    if isinstance(path_or_handle, str):
        with open(path_or_handle, "w") as fh:
            _write_ini(config, fh)
    else:
        _write_ini(config, path_or_handle)


def _write_ini(config, fh):

    cp = ConfigParser()
    for section, mapping in config.items():
        if section.startswith("__"):
            # eg skip __file__ attribute on config objects
            continue
        assert isinstance(mapping, dict)
        cp.add_section(section)
        for (key, value) in mapping.items():
            cp.set(section, key, str(value))

    cp.write(fh)
    if hasattr(fh, "name"):
        config.__file__ = fh.name


def _convert_and_resolve_variables(v, variable_settings):
    """tries to convert `v` to int, float, str in this order"""
    for type_ in (int, float):
        try:
            return type_(v)
        except ValueError:
            pass

    tmpdir = tempfile.mkdtemp()

    fallbacks = {"TMP": tmpdir}

    lookup = ChainMap(variable_settings or {}, dict(os.environ), fallbacks)

    def resolve(match):
        s, e = match.start(), match.end()
        var = match.string[s + 1 : e]
        return lookup.get(var, "<invalid var ${}>".format(var))

    return re.sub(r"\$[A-Z]+", resolve, v)


def read_ini(path, variable_settings=None):
    """reads a ini file as a Config object.

    features:
    - sets attribute __file__ so relative pathes in the config file might be
      resolved

    value handling:
    - resolves environment variables in the value fields
    - resoles fallback variables as $TMP which are not defined on every system
    - tries best conversion, so "10" will be converted to int, and "1.23" to
      float
    """
    cp = ConfigParser()
    cp.read(path)
    config = Config()
    for section in cp.sections():
        for key, value in cp.items(section):
            value = _convert_and_resolve_variables(value, variable_settings)
            if section not in config:
                config[section] = Config()
            config[section][key] = value
    config.__file__ = os.path.abspath(path)
    return config
