from pyrediseasyio.reader_writer import ReaderWriter
from pyrediseasyio.io.single_io import SingleIO
from typing import List, Callable
import json


class IOGroup(ReaderWriter):

    def __init__(self, host='localhost', port=6379, db=0,
                 set_defaults_on_startup: bool = False,
                 delete_keys_on_startup: bool = False,
                 namespace: str = None, *args, **kwargs):

        super().__init__(host=host, port=port, db=db, **kwargs)

        self.namespace = 'easyio' if namespace is None else namespace
        member_names = [d for d in dir(self) if not d.startswith('_')]
        self.members = []
        for name in member_names:
            try:
                attr = getattr(self, name)
                if not isinstance(attr, SingleIO):
                    continue
                attr._reader_writer = self
                self.members.append(name)
                if attr.addr is None:
                    attr.addr = name
                if namespace is not None:
                    attr.namespace = namespace
                if delete_keys_on_startup:
                    self.delete_key(attr.addr)
                if set_defaults_on_startup:
                    attr.write(attr.default)
            except AttributeError:
                pass

    def __len__(self):
        return len(self.members)

    def __setattr__(self, key, value):
        if hasattr(self, 'members') and key in self.members:
            attr = getattr(self, key)
            attr.write(value)
            return
        return super().__setattr__(key, value)

    def dump(self, key: str) -> str:
        """
        Creates a json string containing a list of dict(name/addr/value) of all members and stores it in-memory
        using the given key. The value can later be retrieved by a call to the 'read' method.
        :param key: A unique key for storing the dumped value
        :return: Returns the json string that is stored - for convenience sake.
        """
        s = self.dumps()
        self.write(key, s)
        return s

    def dumps(self, by_names: List = None, by_type: List = None, by_lambda: Callable = None) -> str:
        """
        Returns a json string containing a list of dict(name/addr/value) of all members.
        """
        attrs = self.get_attributes(by_names, by_type, by_lambda)
        members = [dict(name=attr.name, addr=attr.addr, value=attr.value) for attr in attrs]
        return json.dumps(members)

    def get_attributes(self, by_names: List = None, by_type: List = None,
                       by_lambda_each: Callable = None, by_lambda_results: Callable = None):

        names = self.members if by_names is None else by_names
        attrs = [getattr(self, name) for name in names]
        if by_type:
            attrs = [a for a in attrs if type(a) in by_type]
        if by_lambda_each:
            attrs = [a for a in attrs if by_lambda_each(a)]
        if by_lambda_results:
            attrs = by_lambda_results(attrs)

        return attrs







