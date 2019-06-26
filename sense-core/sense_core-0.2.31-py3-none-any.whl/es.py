from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from .config import config
from .log import log_exception, raise_exception, log_info, log_error
from elasticsearch import NotFoundError


def create_connection(label='es'):
    try:
        host = config(label, 'host')
        user = config(label, 'user', '')
        password = config(label, 'pass', '')
        if user and password:
            return connections.create_connection(alias=label, hosts=[host], http_auth=(user, password))
        return connections.create_connection(alias=label, hosts=[host])
    except Exception as e:
        log_exception(e)


__es_clients = {}


def get_es_client(label='es'):
    global __es_clients
    if label not in __es_clients:
        __es_clients[label] = create_connection(label)
    return __es_clients[label]


class BaseSearcher(object):

    def __init__(self, label, doc_model=None):
        self.conn = get_es_client(label)
        self.doc_model = doc_model

    def search_by_id(self, id):
        if self.doc_model is None:
            raise Exception('no doc model found')
        try:
            return self.doc_model.get(id)
        except NotFoundError as ex:
            return None
        except Exception as e:
            raise e


class BaseIndexer(object):

    def __init__(self, label, doc_model, keep_index_num=2):
        self.conn = get_es_client(label)
        self.doc_model = doc_model
        self.bulk_list = []
        self.old_index_list = []
        self.bulk_num = None
        self.alias_index = None
        self.new_index = None
        self.keep_index_num = keep_index_num
        self.index_name = self.doc_model._index._name  # hard trick
        if keep_index_num >= 10:
            self.keep_index_num = 10
        elif keep_index_num <= 1:
            self.keep_index_num = 1

    def init_rebuild_index(self, bulk_num=100):
        self.bulk_num = bulk_num
        self.old_index_list = self._get_all_exist_index()
        self.alias_index = self._get_alias_index()
        self.new_index = self._get_new_index_name()
        self.doc_model.init(index=self.new_index)
        self.delete_expired_indexes()
        log_info(
            "init_rebuild_index new_index={0} alias_index={1} old_index_list={2}".format(self.new_index,
                                                                                         self.alias_index,
                                                                                         self.old_index_list))

    def add_bulk_data(self, id, data):
        self._filter_data(id, data)
        self.bulk_list.append(data)
        self.flush_bulk(False)

    def _filter_data(self, id, data):
        data['_index'] = self.new_index
        if '_type' not in data:
            data['_type'] = 'doc'
        data['_id'] = id
        return data

    def save_data(self, id, data):
        self._filter_data(id, data)
        bulk(self.conn, [data], index=self.index_name, doc_type=self.doc_model)

    def flush_bulk(self, must=False):
        if len(self.bulk_list) == 0:
            return
        if len(self.bulk_list) >= self.bulk_num or must:
            bulk(self.conn, self.bulk_list, index=self.new_index, doc_type=self.doc_model)
            self.bulk_list = []

    def done_rebuild_index(self):
        self.flush_bulk(True)
        self._update_alias()
        log_info('done_rebuild_index for ' + self.index_name)

    def _get_new_index_name(self):
        index_name = self.index_name
        old_index = ''
        if len(self.old_index_list) > 0:
            old_index = self.old_index_list[0]
        if old_index == '' or index_name == old_index:
            return index_name + '_v1'
        version = self._get_index_version(old_index)
        if version is None:
            raise_exception('bad old_index name ' + old_index)
            return
        times = 5
        while times >= 0:
            times -= 1
            version += 1
            if version > 10:
                version = 1
            name = index_name + '_v' + str(version)
            if name in self.old_index_list:
                continue
            return name
        raise_exception("cannot found valid new index for {}".format(self.old_index_list))

    def _get_index_version(self, index_name):
        pos = index_name.rfind('_v')
        if pos < 0 or pos >= len(index_name) - 2:
            return None
        version = int(index_name[pos + 2:len(index_name)])
        return version

    def _update_alias(self):
        if self.new_index != self.index_name:
            self.conn.indices.put_alias(index=self.new_index, name=self.index_name)
            log_info('put_alias ' + self.new_index + ' for ' + self.index_name)
        if self.alias_index == '':
            log_info('no old_index need to update')
            return
        self.conn.indices.delete_alias(index=self.alias_index, name=self.index_name, ignore=[400, 404])
        log_info('delete_alias ' + self.alias_index + ' for ' + self.index_name)

    def _get_all_exist_index(self):
        result = list()
        indices = self.conn.indices.get('*')
        for index in indices:
            if index.find(self.index_name) == 0:
                result.append(index)
        result.sort(key=self._sort_index)
        return result

    def _sort_index(self, index_name):
        version = self._get_index_version(index_name)
        if not version:
            return 0
        return -version

    def delete_expired_indexes(self):
        if len(self.old_index_list) <= self.keep_index_num or len(self.alias_index) == 0:
            log_info("no need delete_expired_indexes")
            return
        pos = self.old_index_list.index(self.alias_index)
        pos1 = pos - 1
        if pos1 < 0:
            pos1 = len(self.old_index_list) - 1
        if pos == pos1:
            log_error("found bad pos for delete_expired_indexes")
            return
        self._delete_index(self.old_index_list[pos1])

    def _delete_index(self, index_name):
        self.conn.indices.delete(index_name)
        log_info("_delete_index " + index_name)

    def _get_alias_index(self):
        if len(self.old_index_list) == 0:
            return ''
        if self.index_name in self.old_index_list:
            return self.index_name
        try:
            aliases = self.conn.indices.get_alias(",".join(self.old_index_list), self.index_name)
            if len(aliases) == 0:
                return ''
            if len(aliases) >= 2:
                raise_exception("_get_alias_index found dup alias")
            keys = list(aliases.keys())
            return keys[0]
        except NotFoundError as ex:
            pass
        return ''
