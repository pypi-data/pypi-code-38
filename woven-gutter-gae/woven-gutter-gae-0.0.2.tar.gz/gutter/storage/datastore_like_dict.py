import logging

from google.cloud import datastore
import pickle
import codecs

LOG_TOKEN = '[DATASTORE_LIKE_DICT] {}'


def encode(obj):
    return codecs.encode(pickle.dumps(obj), 'base64').decode()


def decode(string):
    return pickle.loads(codecs.decode(string.encode(), "base64"))


class DatastoreDict(dict):

    def __init__(self, namespace=None, kind=None):
        self.client = datastore.Client()
        self.kind = kind
        self.namespace = namespace
        logging.info(LOG_TOKEN.format(
            'Init :: Namespace {} :: Kind {}'.format(
                namespace,
                kind
            )
        ))

    def __setitem__(self, key, item):
        logging.info(LOG_TOKEN.format(
            'Insert :: key {} :: value {}'.format(
                key,
                item
            )
        ))

        _key = self.client.key(self.kind, key, namespace=self.namespace)
        _item = {
            'value': encode(item)
        }

        _entity = datastore.Entity(key=_key)
        _entity.update(_item)

        self.client.put(entity=_entity)

        # self.__dict__[key] = item

    def __getitem__(self, key):
        logging.info(LOG_TOKEN.format(
            'Get Item :: key {}'.format(
                key
            )
        ))

        _key = self.client.key(self.kind, key, namespace=self.namespace)
        _entity = self.client.get(_key)

        if _entity:
            return decode(_entity['value'])

        raise KeyError('Key not found')

    def __delitem__(self, key):
        logging.info(LOG_TOKEN.format(
            'Delete :: key {}'.format(
                key
            )
        ))

        _key = self.client.key(self.kind, key, namespace=self.namespace)
        self.client.delete(_key)

    def keys(self):
        logging.info(LOG_TOKEN.format(
            'Keys'
        ))

        _query = self.client.query(kind=self.kind, namespace=self.namespace)
        _result = list(_query.fetch())
        _return = dict()

        for _r in _result:
            _return[_r.key.name] = decode(_r['value'])

        return _return.keys()

    def items(self):
        logging.info(LOG_TOKEN.format(
            'Itens'
        ))

        _query = self.client.query(kind=self.kind, namespace=self.namespace)
        _result = list(_query.fetch())
        _return = dict()

        for _r in _result:
            _return[_r.key.name] = decode(_r['value'])

        return _return.items()

    def __contains__(self, item):
        logging.info(LOG_TOKEN.format(
            'Contains :: Key {}'.format(
                item
            )
        ))

        _key = self.client.key(self.kind, item, namespace=self.namespace)
        _entity = self.client.get(_key)

        if _entity:
            return True

        raise False
