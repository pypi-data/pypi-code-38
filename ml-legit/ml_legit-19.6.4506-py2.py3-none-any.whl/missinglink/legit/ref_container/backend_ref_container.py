# -*- coding: utf-8 -*-
from missinglink.core import ApiCaller

from ..backend_mixin import BackendMixin
from ..dulwich.refs import RefsContainer


SYMREF = b'ref: '


class BackendRefContainer(BackendMixin, RefsContainer):
    def __init__(self, connection, config, session):
        super(BackendRefContainer, self).__init__(connection, config, session)

    def get_packed_refs(self):
        return {}

    def set_if_equals(self, name, old_ref, new_ref):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/ref/%s' % (self._volume_id, name)

            msg = {
                'old_ref': old_ref,
                'new_ref': new_ref,
            }

            result = ApiCaller.call(self._config, session, 'patch', url, msg)

            return result.get('ok')

    def add_if_new(self, name, ref):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/ref/%s' % (self._volume_id, name)

            msg = {
                'ref': ref
            }

            result = ApiCaller.call(self._config, session, 'post', url, msg)

            return result.get('ok')

    def read_loose_ref(self, name):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/ref/%s' % (self._volume_id, name)

            result = ApiCaller.call(self._config, session, 'get', url)

            commit_sha = result.get('commit_sha')

            if commit_sha is None:
                raise KeyError(name)

    def set_symbolic_ref(self, name, other):
        raise NotImplementedError(self.set_symbolic_ref)

    def allkeys(self):
        raise NotImplementedError(self.allkeys)

    def remove_if_equals(self, name, old_ref):
        raise NotImplementedError(self.remove_if_equals)
