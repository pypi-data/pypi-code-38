import abc
import collections
from typing import TypeVar, Type, List

import flatbuffers

T = TypeVar('T')


class FlatbufferObject(collections.MutableMapping, dict):
    __metaclass__ = abc.ABCMeta

    def __init__(self, dataclass, flatbuffer, builder=flatbuffers.Builder(0)):
        self.dataclass = dataclass
        self.fbs = flatbuffer
        self.builder = builder
        self.classname = self.fbs.__name__.split('.')[-1]

    @abc.abstractmethod
    def dataclass_to_flatbuffer(self, dataclass):
        """ convert given dataclass to the right fbs object """

    @abc.abstractmethod
    def flatbuffer_to_dataclass(self, flatbuffer):
        """ convert given fbs object to the right dataclass """

    def serialize(self, item: Type[T]) -> bytearray:
        self.builder.Finish(self.dataclass_to_flatbuffer(item))
        return self.builder.Output()

    def build(self, item):
        self._flatbuffer = item
        return self.flatbuffer_to_dataclass(item)

    def deserialize(self, item: bytearray) -> T:
        self._flatbuffer = getattr(getattr(self.fbs, self.classname), f'GetRootAs{self.classname}')(item, 0)
        return self.flatbuffer_to_dataclass(self._flatbuffer)

    def __getitem__(self, key):
        if hasattr(getattr(self.fbs, self.classname), f'{key}AsNumpy'):
            return getattr(self._flatbuffer, f'{key}AsNumpy')()
        elif hasattr(getattr(self.fbs, self.classname), f'{key}Length'):
            length = getattr(self._flatbuffer, f'{key}Length')()
            return [getattr(self._flatbuffer, f'{key}')(i) for i in range(length)]
        else:
            return getattr(self._flatbuffer, f'{key}')()

    def __setitem__(self, key, value):
        getattr(self.fbs, f'{self.classname}Add{key}')(self.builder, value)

    def start(self):
        getattr(self.fbs, f'{self.classname}Start')(self.builder)

    def end(self):
        return getattr(self.fbs, f'{self.classname}End')(self.builder)

    def build_vector(self, key: str, values: List, entity=None):
        vector_len = len(values)
        if vector_len > 0:
            val_0 = values[0]
            if hasattr(val_0, '__dict__'):
                if entity is None:
                    raise ValueError('cannot build dataclass vector without its entity, pass entity to build_vector')
                else:
                    entity_obj = entity(self.builder)
                    values = [entity_obj.dataclass_to_flatbuffer(val) for val in values]
        getattr(self.fbs, f'{self.classname}Start{key}Vector')(self.builder, vector_len)
        for val in reversed(values):
            if entity is not None:
                self.builder.PrependUOffsetTRelative(val)
            else:
                self.builder.PrependByte(val)
        return self.builder.EndVector(vector_len)

    def build_string(self, value):
        return self.builder.CreateString(value)
