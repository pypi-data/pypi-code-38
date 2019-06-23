# -*- coding: utf-8 -*-
from ..dulwich.object_store import BaseObjectStore


class NullObjectStore(BaseObjectStore):
    def __iter__(self):
        pass

    def get_raw(self, metadata):
        raise KeyError()
