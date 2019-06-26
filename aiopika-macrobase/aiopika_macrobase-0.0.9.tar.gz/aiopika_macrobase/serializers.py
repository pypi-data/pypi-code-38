from abc import ABC, abstractmethod
from typing import List, Dict, Type, Tuple

from .exceptions import SerializeFailedException, DeserializeFailedException, ContentTypeNotSupportedException, \
    PayloadTypeNotSupportedException

import pickle
import rapidjson


class Serializer(ABC):
    input_type = None
    content_type = None

    @staticmethod
    @abstractmethod
    def serialize(value) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def deserialize(raw: bytes):
        pass


class StringSerializer(Serializer):
    input_type = str
    content_type = 'text/plain'

    @staticmethod
    def serialize(value: str) -> bytes:
        return value.encode()

    @staticmethod
    def deserialize(raw: bytes) -> str:
        return raw.decode()


class JSONSerializer(Serializer):
    input_type = dict
    content_type = 'application/json'

    @staticmethod
    def serialize(value: dict) -> bytes:
        return rapidjson.dumps(value).encode()

    @staticmethod
    def deserialize(raw: bytes) -> dict:
        return rapidjson.loads(raw)


class ExceptionSerializer(Serializer):
    input_type = Exception
    content_type = 'application/python-pickle'

    @staticmethod
    def serialize(value: Exception) -> bytes:
        return pickle.dumps(value)

    @staticmethod
    def deserialize(raw: bytes) -> Exception:
        return pickle.loads(raw)


_serializers: List[Serializer] = [StringSerializer, JSONSerializer, ExceptionSerializer]
deserializers: Dict[str, Serializer] = {s.content_type: s for s in _serializers}


def serialize(value) -> Tuple[bytes, str]:
    serializer = [s for s in _serializers if isinstance(value, s.input_type)]
    serializer = serializer[0] if serializer else None

    if serializer is None:
        # TODO: add more info about value (short desc) and his type
        raise PayloadTypeNotSupportedException

    try:
        return serializer.serialize(value), serializer.content_type
    except Exception as e:
        raise SerializeFailedException


def deserialize(raw: bytes, content_type: str):
    serializer = deserializers.get(content_type)

    if serializer is None:
        # TODO: add more info about value (short desc) and his type
        raise ContentTypeNotSupportedException

    try:
        return serializer.deserialize(raw)
    except Exception as e:
        raise DeserializeFailedException
