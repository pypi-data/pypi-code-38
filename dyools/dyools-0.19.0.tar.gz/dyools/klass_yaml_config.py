from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

import yaml

from .klass_path import Path


class YamlConfig(object):
    def __init__(self, path, defaults={}, create_if_not_exists=False, many=False):
        self.path = path
        if create_if_not_exists:
            Path.touch(path)
        assert os.path.isfile(path), "The file [%s] not found" % path
        with open(path) as f:
            if many:
                yaml_load = yaml.load_all
            else:
                yaml_load = yaml.load
            if hasattr(yaml, 'UnsafeLoader'):
                self.__data = yaml_load(f.read(), Loader=yaml.UnsafeLoader) or {}
            else:
                self.__data = yaml_load(f.read()) or {}
        self.defaults = defaults

    def set_defaults(self, name=False):
        for key, values in self.__data.items():
            if name and name != key:
                continue
            defaults = self.defaults.copy()
            defaults.update(values)
            self.__data[key] = defaults

    def dump(self):
        with open(self.path, 'w+') as f:
            f.write(yaml.dump(self.__data, default_flow_style=False, allow_unicode=True))

    def set_data(self, data):
        if not isinstance(data, dict):
            data = {'root': data}
        self.__data = data

    def get_data(self):
        return self.__data

    def get(self, **kwargs):
        res = {}
        name = kwargs.pop('_name', False)
        if name:
            self.set_defaults(name)
        for key, values in self.__data.items():
            if name and name != key:
                continue
            if name and not kwargs and name == key:
                res.update({key: values})
                continue
            if not kwargs:
                continue
            found = []
            for k, v in kwargs.items():
                if k in values:
                    if values[k] == v:
                        found.append(True)
                    else:
                        found.append(False)
            if found and all(found):
                res.update({key: values})
        return res

    def get_values(self, **kwargs):
        res = {}
        data = self.get(**kwargs)
        for k, v in data.items():
            res.update(v)
        return res

    def add(self, _name, **kwargs):
        item = self.get(_name=_name)
        values = kwargs.copy()
        if item:
            item[_name].update(kwargs)
            values = item[_name]
        self.__data.update({
            _name: values
        })
        self.set_defaults(_name)
        return self.__data

    def delete(self, **kwargs):
        items = self.get(**kwargs)
        for item in items:
            self.__data.pop(item)

    def get_list(self, **kwargs):
        if kwargs:
            items = self.get(**kwargs)
        else:
            items = self.__data
        res = []
        for k, v in items.items():
            d = dict(name=k)
            if isinstance(v, dict):
                d.update(v)
            res.append(d)
        return res

    def switch(self, name, attr, value, inverse):
        for key, values in self.__data.items():
            for k, v in values.items():
                if k == attr:
                    if key == name:
                        self.__data[key][k] = value
                    else:
                        self.__data[key][k] = inverse
