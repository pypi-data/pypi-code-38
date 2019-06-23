from __future__ import unicode_literals

from importlib import import_module

from django.core.urlresolvers import reverse, NoReverseMatch
from .encoder import JsonDocEncoder


class JsonBaseManager(object):
    def __init__(self, json_data):
        self.json_data = json_data

    def get_instance(self, data):
        _module = import_module(data['module'])
        cls = getattr(_module, data['model'])
        handler = getattr(cls, 'json_get_instance', None)
        if handler and callable(handler):
            return handler(data)
        return cls.objects.get(pk=data['id'])

    def _label(self, data):
        return data.get('label', None)

    def _url(self, data):
        # FIXME: typo handling for old releases
        kwargs = data['url'].get(
                'url_parametres',
                data['url'].get('url_parameters'))
        try:
            return reverse(data['url']['url_name'],
                           kwargs=kwargs)
        except NoReverseMatch:
            return None

    def short_description(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError


class JsonObjectManager(JsonBaseManager):
    def url(self):
        return self._url(self.json_data)

    def short_description(self):
        return self._label(self.json_data)

    def description(self):
        return self._label(self.json_data)

    @property
    def instance(self):
        return self.get_instance(self.json_data)


class JsonListManager(JsonBaseManager):
    def __iter__(self):
        for item in self.json_data or []:
            yield self.get_instance(item)

    def __getitem__(self, key):
        if hasattr(self, key) and callable(getattr(self, key)):
            return getattr(self, key)

        obj = self.get_first(key)
        if obj:
            return self.get_instance(obj)
        return None

    def iter_data(self):
        for item in self.json_data or []:
            if item:
                yield item

    @property
    def instance(self):
        for item in self.iter_data():
            if item.get('model', ''):
                return self.get_instance(item)
        return None

    def get_first(self, key):
        for item in self.iter_data():
            if item.get('model', '') == key:
                return item
        return None

    def append(self, instance):
        self.json_data.append(JsonDocEncoder(instance).dump())

    def label(self):
        for item in self.iter_data():
            label = self._label(item)
            if label is not None:
                return label
        return None

    def url(self):
        for item in self.iter_data():
            if 'url' in item:
                return self._url(item)
        return None

    def description(self):
        rc = []
        for item in self.iter_data():
            label = self._label(item)
            if label:
                rc.append(label)
        return ", ".join(rc)

    def iter_items(self):
        for obj in self.iter_data():
            item = obj.copy()
            if 'url' in obj:
                url = self._url(obj)
                item['url'] = url
            item['label'] = self._label(obj)
            yield item

    def short_description(self):
        return self.description()

    def update(self, obj):
        """
        Replace object in the json_data with new provided. Keep ordering.
        :param obj: object to replace with
        """
        rc = []
        data = JsonDocEncoder(obj).dump()
        for item in self.iter_data():
            if item['model'] == data['model']:
                rc.append(obj)
            else:
                rc.append(self.get_instance(item))
        return rc


class JsonDocManager(JsonListManager):
    def __init__(self, *args, **kwargs):
        super(JsonDocManager, self).__init__(*args, **kwargs)

        raise DeprecationWarning("JsonDocManager deprecated, please use JsonListManager instead")
