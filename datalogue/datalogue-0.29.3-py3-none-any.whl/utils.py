from typing import TypeVar, List, Callable, Union, Dict, Type
from enum import Enum
from abc import abstractmethod, ABC
from io import BytesIO, SEEK_SET, SEEK_END

from datalogue.errors import DtlError

T = TypeVar('T')
Json = Union[Dict, str, int, List]


def _parse_list(parse_function: Callable[[Json], Union[DtlError, T]]) -> Callable[[List[Json]], Union[DtlError, List[T]]]:
    """
    Returns another function that can be used to parse a list of json with the specified parse function

    :param parse_function: function to be used for parsing
    :return:
    """
    def parse_concrete(objects: List[Json]) -> Union[DtlError, List[T]]:
        """
        Applies the parse function specified in the parent function to each element of the list of json

        :param objects: list to apply the parse function to
        :return:
        """
        parsed_list = []
        for obj in objects:
            parsed_obj = parse_function(obj)

            if isinstance(parsed_obj, DtlError):
                return parsed_obj
            else:
                parsed_list.append(parsed_obj)

        return parsed_list
    return parse_concrete


def _parse_string_list(objects: List[Json]) -> Union[DtlError, List[str]]:
    parsed_list = []

    for obj in objects:
        if isinstance(obj, str):
            parsed_list.append(obj)
        else:
            return DtlError("The following object is not a string: %s" % obj)

    return parsed_list


def not_implemented() -> NotImplemented:
    return NotImplemented


class SerializableStringEnum(Enum):

    @staticmethod
    def from_str(enum: Type['SerializableStringEnum']) -> Callable[[str], Union[DtlError, 'SerializableStringEnum']]:
        """
        Builds a function to parse the string enum `enum`
        :param enum: enum to create a parser for
        :return:
        """
        def inner_sanctum(s: str) -> Union[DtlError, 'SerializableStringEnum']:
            """
            Parses a string and returns the instance of the Enum it corresponds to or a string with an error message

            :param s: string to be parsed
            :return:
            """
            for blob_type in enum:
                if blob_type.value == s:
                    return blob_type

            return enum.parse_error(s)

        return inner_sanctum

    def __repr__(self):
        return f"{self._value_}"

    @staticmethod
    @abstractmethod
    def parse_error(s: str) -> DtlError:
        """
        Returns the error to be used if the parsing fails
        :return: string error
        """
        return NotImplemented


class ResponseStream(object):

    def __init__(self, request_iterator):
        """
        Class used internally to be able to transform a `requests` iterator into a File like object.

        :param request_iterator: Iterator to pull the data from
        """

        # In memory bytes buffer
        self._bytes = BytesIO()
        # Iterator to use to retrieve data
        self._iterator = request_iterator

        self.closed = self._bytes.closed

    def close(self):
        return self._bytes.close()

    def _load_all(self) -> int:
        """
        Loads all the data into the buffer

        :return: new absolute position in the buffer
        """
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position: int) -> None:
        """
        Loads the data into the inner buffer until the goal position

        :param goal_position: Byte index to go to
        :return:
        """

        # End of the byte buffer
        current_position = self._bytes.seek(0, SEEK_END)

        # Fill the buffer with more data until we reach the new byte index goal
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self) -> int:
        """
        Current file position, an integer.

        :return:
        """
        return self._bytes.tell()

    def read(self, size=None) -> bytes:
        """
        Read at most size bytes, returned as a bytes object.

        :param size: in bytes to retrieve, if negative reads all
        :return: byte object
        """
        left_off_at = self._bytes.tell()

        # Fill the buffer with new data from the iterator
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        # make sure we are reading from the right position
        self._bytes.seek(left_off_at)

        # return the size bytes from the buffer
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET) -> int:
        """

        :param position:
        :param whence:
        :return:
        """
        if whence == SEEK_END:
            self._load_all()
            return self._bytes.seek(position, whence)
        else:
            return self._bytes.seek(position, whence)
