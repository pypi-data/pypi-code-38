from pyrediseasyio.reader_writer import ReaderWriter
from pyrediseasyio.single_io import SingleIO
import json


class IOGroup(ReaderWriter):

    def __init__(self, host='localhost', port=6379, db=0):
        super().__init__(host=host, port=port, db=db)
        member_names = [d for d in dir(self) if not d.startswith('__')]
        self.members = []
        for name in member_names:
            try:
                attr = getattr(self, name)
                if not isinstance(attr, SingleIO):
                    continue
                attr._reader_writer = self
                self.members.append(name)
                attr.write(attr.default)
            except AttributeError:
                pass

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

    def dumps(self) -> str:
        """
        Returns a json string containing a list of dict(name/addr/value) of all members.
        """
        members = []
        for m in self.members:
            attr = getattr(self, m)
            members.append(dict(name=attr.name, addr=attr.addr, value=attr.value))
        return json.dumps(members)




