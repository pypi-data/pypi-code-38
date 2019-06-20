# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from contextlib import closing

import six

from ..connection_mixin import ConnectionMixin


class BaseMLIndex(ConnectionMixin):
    __metaclass__ = ABCMeta

    def __init__(self, connection):
        super(BaseMLIndex, self).__init__(connection)

        if not self._connection.read_only:
            self._create_table_if_needed()

    @abstractmethod
    def _create_table_if_needed(self):
        """

        :return:
        """

    @abstractmethod
    def begin_commit(self, commit_sha, tree_id, ts):
        """

        :return:
        """

    @abstractmethod
    def end_commit(self):
        """

        :return:
        """

    @classmethod
    def _decode_entries(cls, entries):
        for name, entry in entries.items():
            ctime, mtime, dev, ino, mode, uid, gid, size, sha, flags, url = entry

            if not isinstance(name, six.string_types):
                name = name.decode('utf8')

            if not isinstance(sha, six.string_types):
                sha = sha.decode('utf8')

            row = (name, sha, ctime, mtime, mode, uid, gid, size, url)

            yield row
