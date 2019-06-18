import weakref
from collections import Mapping


class MetaData:
    pass


class ObjectsMetaData(Mapping):
    metadata_class = MetaData

    def __init__(self):
        self.objects_dict = dict()

    def __getitem__(self, item):
        try:
            return self.objects_dict[id(item)][1]
        except KeyError:
            md = self.metadata_class()

            self.objects_dict[id(item)] = (weakref.ref(item), md)
            return md

    def __iter__(self):
        for key, elem in self.objects_dict.items():
            value = elem[0]()
            if value is not None:
                yield value
            else:
                # We can remove this
                del self.objects_dict[key]

    def __len__(self):
        return len(self.objects_dict)

    def __contains__(self, item):
        return id(item) in self.objects_dict
