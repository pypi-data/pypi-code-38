from __future__ import unicode_literals

from .manager import JsonListManager, JsonObjectManager
from .encoder import JsonDocEncoder


class JsonListHandler(object):
    MANAGER = JsonListManager

    def __init__(self, field_name):
        self.field_name = field_name

    @property
    def cache_key(self):
        return '_js_list_%s' % self.field_name

    def __get__(self, model, obj_type=None):
        if hasattr(model, self.cache_key):
            return getattr(model, self.cache_key)

        manager = self.MANAGER(getattr(model, self.field_name))
        setattr(model, self.cache_key, manager)
        return manager

    def __set__(self, model, value):
        data = [JsonDocEncoder(item).dump() for item in value]
        if hasattr(model, self.cache_key):
            delattr(model, self.cache_key)
        setattr(model, self.field_name, data)


class JsonObjectHandler(object):
    MANAGER = JsonObjectManager

    def __init__(self, field_name):
        self.field_name = field_name

    @property
    def cache_key(self):
        return '_js_obj_%s' % self.field_name

    def __get__(self, model, obj_type=None):
        if hasattr(model, self.cache_key):
            return getattr(model, self.cache_key)

        manager = self.MANAGER(getattr(model, self.field_name))
        setattr(model, self.cache_key, manager)
        return manager

    def __set__(self, model, value):
        data = JsonDocEncoder(value).dump()
        if hasattr(model, self.cache_key):
            delattr(model, self.cache_key)
        setattr(model, self.field_name, data)
