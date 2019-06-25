from elasticsearch import Elasticsearch
from elasticsearch import helpers

class ESIndexError(Exception):
    pass

class ESIndex:
    # ESIndex is a generic Elasticsearch helper class
    def __init__(self, hosts=['localhost:9200'], create=True):
        self._es = Elasticsearch(hosts)
        if create and not self._exits():
            self._create_index()

    def _index_exists(func):
        def wrapper(self, *args, **kwargs):
            if not self._exits(): raise ESIndexError('Index %s does not exist'%self.Meta.index_name)
            return func(self, *args, **kwargs)
        return wrapper

    def _exits(self):
        return self._es.indices.exists(self.Meta.index_name)

    def _create_index(self):
        if self._exits(): raise ESIndexError('Index %s already exists'%self.Meta.index_name)
        self._es.indices.create(self.Meta.index_name)
        self._es.indices.put_mapping(index=self.Meta.index_name, doc_type=self.Meta.doc_type, body=self.Meta.mapping)

    @_index_exists
    def _delete_index(self, confirm=None):
        # This may seem stupid but be very sure before you delete the index.
        if confirm == 'DELETE':
            self._es.indices.delete(index=self.Meta.index_name)

    @_index_exists
    def index_object(self, obj):
        return self._es.index(index=self.Meta.index_name, id=self.Meta.doc_id_tmpl%obj, body=obj)

    @_index_exists
    def bulk(self, oblist):
        bulk_list = [
            {
                '_index': self.Meta.index_name,
                '_id': self.Meta.doc_id_tmpl%ob,
                '_type': self.Meta.doc_type,
                '_source': ob
            } for ob in oblist
        ]
        helpers.bulk(self._es, bulk_list)

    @_index_exists
    def count(self):
        return self._es.count(index=self.Meta.index_name)
