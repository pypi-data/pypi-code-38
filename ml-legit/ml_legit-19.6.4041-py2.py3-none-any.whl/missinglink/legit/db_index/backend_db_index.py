# -*- coding: utf-8 -*-
import csv
import logging
import six
from missinglink.core import ApiCaller

from .base_db_index import BaseMLIndex
from ..backend_mixin import BackendMixin


class BackendMLIndex(BackendMixin, BaseMLIndex):
    def __init__(self, connection, config, session):
        self.__multi_process_control = None
        super(BackendMLIndex, self).__init__(connection, config, session)

    def _create_table_if_needed(self):
        pass

    def set_entries_from_url(self, file_name, isolation_token):
        url = 'data_volumes/%s/index/stage' % self._volume_id

        msg = {
            'index_url': file_name,
            'isolation_token': isolation_token,
        }

        ApiCaller.call(self._config, self._session, 'post', url, msg, is_async=True)

    @staticmethod
    def _sync_set_entries_from_list(config, session, volume_id, decoded_entries, isolation_token):
        rows = []
        for name, sha, ctime, mtime, mode, uid, gid, size, url in decoded_entries:
            row = {
                'name': name,
                'sha': sha,
                'ctime': ctime,
                'mtime': mtime,
                'mode': mode,
                'uid': uid,
                'gid': gid,
                'size': size,
                'url': url,
            }

            rows.append(row)

        url = 'data_volumes/%s/index/stage' % volume_id
        msg = {
            'entries': rows,
            'isolation_token': isolation_token,
        }

        ApiCaller.call(config, session, 'post', url, msg, is_async=True)

    def set_multi_process_control(self, multi_process_control):
        self.__multi_process_control = multi_process_control

    def set_entries_from_list_async(self, entries, isolation_token, callback=None):
        args = (self._config, self._session, self._volume_id, list(self._decode_entries(entries)), isolation_token)

        self.__multi_process_control.execute(_sync_set_entries_from_list, args=args, callback=callback, high=True)

    def set_entries_from_list(self, entries, isolation_token):
        BackendMLIndex._sync_set_entries_from_list(self._config, self._session, self._volume_id, self._decode_entries(entries), isolation_token)

    class ChangeSetIter(object):
        def __init__(self, data, data_type=None):
            self.__data = data
            data_type = data_type or 'csv'

            if data_type.lower() == 'csv':
                self.__reader = csv.DictReader(data)

        def __iter__(self):
            return self

        def next(self):
            data = next(self.__reader)
            return data

        def __next__(self):
            return self.next()

    def get_changeset(self, index_url, isolation_token):
        if not index_url:
            logging.debug('no data provided')
            return

        logging.debug('add data %s', index_url)

        def decode_iter(gen):
            for line in gen:
                if not isinstance(line, six.string_types):
                    line = line.decode()

                yield line

        url = 'data_volumes/%s/index/stage' % self._volume_id

        msg = {
            'index_url': index_url,
            'dry_mode': True,
            'isolation_token': isolation_token,
        }

        result = ApiCaller.call(self._config, self._session, 'post', url, msg, is_async=True)

        r = self._session.get(result['change_set_url'], stream=True)
        r.raise_for_status()

        return self.ChangeSetIter(decode_iter(r.iter_lines()))

    def begin_commit(self, commit_sha, tree_id, ts):
        raise NotImplementedError(self.begin_commit)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)


_sync_set_entries_from_list = BackendMLIndex._sync_set_entries_from_list
