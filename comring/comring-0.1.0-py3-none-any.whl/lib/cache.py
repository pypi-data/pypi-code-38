from . import odoo

class SimpleCache(object):
    def __init__(self, client, model, fields, key_field='id', key_is_pk=True):
        self._client = client
        self._model = model
        self._fields = fields
        self._key_field = key_field
        self._key_is_pk = True
        self._cache_data = {}

    def _fetch(self, key_value):
        if self._key_is_pk:
            res = self._client.read_one(self._model, key_value, self._fields)
        else:
            domain = [[self._key_field, '=', key_value]]
            res = self._client.search_read_one(self._model, domain, self._fields)
        cache_key = str(key_value)
        self._cache_data[cache_key] = res
        return res

    def read(self, key_value):
        cache_key = str(key_value)
        if cache_key not in self._cache_data:
            return self._fetch(key_value)
        return self._cache_data[cache_key]

    def prefetch(self, key_values):
        if self._key_is_pk:
            records = self._client.read(self._model, key_values, self._fields)
        else:
            domain = [[self._key_field, 'in', key_values]]
            records = self._client.search_read(self._model, domain, self._fields)
        for rec in records:
            cache_key = str(rec[self._key_field])
            self._cache_data[cache_key] = rec


    def __iter__(self):
        for key in self._cache_data:
            yield self._cache_data[key]


