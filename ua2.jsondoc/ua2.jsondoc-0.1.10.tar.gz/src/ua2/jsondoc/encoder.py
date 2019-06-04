from __future__ import unicode_literals


class JsonDocEncoder(object):
    def __init__(self, data_object):
        self.data_object = data_object

    def key(self):
        return {
            'id': self.data_object.id,
            'module': self.data_object.__class__.__module__,
            'model': self.data_object.__class__.__name__}

    def dump(self):
        data = self.key()
        data['label'] = getattr(self.data_object, 'label', str(self.data_object))

        if hasattr(self.data_object, 'json_dump'):
            data.update(self.data_object.json_dump())

        return data
