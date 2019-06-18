from dataclasses import dataclass
from typing import List

from keios_protocol_common import FlatbufferObject

from .flatbuffers import ClassificationClass2Request as ClassificationClass2RequestClass
from .flatbuffers import ClassificationClass2Response as ClassificationClass2ResponseClass
from .flatbuffers import Probability as ProbabilityClass
from .flatbuffers import Vector as VectorClass


@dataclass
class Vector:
    bytes: bytearray


class VectorEntity(FlatbufferObject):
    def __init__(self, builder):
        super().__init__(Vector, VectorClass, builder)

    def dataclass_to_flatbuffer(self, dataclass):
        bytes_vector = self.build_vector('Bytes', dataclass.bytes)
        self.start()
        self['Bytes'] = bytes_vector
        return self.end()

    def flatbuffer_to_dataclass(self, flatbuffer):
        return self.dataclass(bytes=self['Bytes'].tobytes())


@dataclass
class ClassificationClass2Request:
    vectors: List[Vector]


class ClassificationClass2RequestEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(ClassificationClass2Request, ClassificationClass2RequestClass)

    def dataclass_to_flatbuffer(self, dataclass):
        vector_vector = self.build_vector('Vectors', dataclass.vectors, VectorEntity)
        self.start()
        self['Vectors'] = vector_vector
        return self.end()

    def flatbuffer_to_dataclass(self, flatbuffer):
        vector = VectorEntity(self.builder)
        vectors = [vector.build(v) for v in self['Vectors']]
        return self.dataclass(vectors=vectors)


@dataclass
class Probability:
    probability1: float
    probability2: float


class ProbabilityEntity(FlatbufferObject):
    def __init__(self, builder):
        super().__init__(Probability, ProbabilityClass, builder)

    def dataclass_to_flatbuffer(self, dataclass):
        probability1 = dataclass.probability1
        probability2 = dataclass.probability2
        offset = self.fbs.CreateProbability(self.builder, probability1, probability2)
        return offset

    def flatbuffer_to_dataclass(self, flatbuffer):
        return self.dataclass(probability1=self['Probability1'], probability2=self['Probability2'])


@dataclass
class ClassificationClass2Response:
    response: List[Probability]


class ClassificationClass2ResponseEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(ClassificationClass2Response, ClassificationClass2ResponseClass)

    def dataclass_to_flatbuffer(self, dataclass):
        response_vector = self.build_struct_vector('Response', dataclass.response, ProbabilityEntity)
        self.start()
        self['Response'] = response_vector
        return self.end()

    def flatbuffer_to_dataclass(self, flatbuffer):
        probability = ProbabilityEntity(self.builder)
        response = [probability.build(p) for p in self['Response']]
        return self.dataclass(response=response)
