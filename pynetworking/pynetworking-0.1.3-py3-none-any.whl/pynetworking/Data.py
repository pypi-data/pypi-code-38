"""
:module: pynetworking.Data
:synopsis: Lowest level module, that manages important data for packets, mostly in bytes.
:author: Julian Sobott

public functions
----------------

.. autofunction:: general_pack

.. autofunction:: general_unpack

.. autofunction:: pack_int_type

.. autofunction:: unpack_int_type

.. autofunction:: pack_int

public classes
--------------

.. autoclass:: ByteStream
    :members:
    :undoc-members:

.. autoclass:: File
    :members:
    :undoc-members:

private functions
-----------------

.. autofunction:: _pack

.. autofunction:: _unpack

"""
import os
import pickle
from typing import Any, Union
import dill

from pynetworking.utils import Ddict, load_dict_from_json, dump_dict_to_json
from pynetworking.Logging import logger

NUM_TYPE_BYTES = 3
ENCODING = "utf-8"
BYTEORDER = "big"
NUM_INT_BYTES = 4

types = Ddict({
    int:    0x001,
    float:  0x002,
    str:    0x003,
    list:   0x004,
    dict:   0x005,
    tuple:  0x006,
    bytes:  0x007,
    bool:   0x008,
    type(None):   0x009,
})


def general_pack(*args) -> bytes:
    """Converts all args into a bytes string. If there are non builtin data types pickle is taken for converting."""
    try:
        specific_byte_string = b"0"
        specific_byte_string += _pack(*args)
    except Exception:
        specific_byte_string = b"1"
        specific_byte_string += dill.dumps(args)
    return specific_byte_string


def general_unpack(byte_stream: 'ByteStream', num_bytes=None) -> tuple:
    """Take in a bytestream, with the bytes string from :func:`general_pack`, and converts it back into a tuple with
    all args."""
    uses_pickle = byte_stream.next_bytes(1)
    if str(uses_pickle, ENCODING) == "1":
        num_bytes = byte_stream.remaining_length if num_bytes is None else num_bytes - 1
        bytes_string = byte_stream.next_bytes(num_bytes)
        data = dill.loads(bytes_string)
    else:
        all_data = _unpack(byte_stream)
        data = all_data
    return data


def _pack(*args) -> bytes:
    """Converts all args into a bytes string, like :func:`pickle.dumps`. It only supports the builtin data types.
    See the `types` variable at the top of this module for all supported types."""
    byte_string = b""

    for value in args:
        val_type: type = type(value)
        try:
            type_num = types[val_type]
        except KeyError:
            raise KeyError()
        byte_string += type_num.to_bytes(NUM_TYPE_BYTES, BYTEORDER)

        if val_type is int:
            byte_string += int.to_bytes(value, NUM_INT_BYTES, BYTEORDER, signed=True)
        elif val_type is float:
            b_value = bytes(value.hex(), ENCODING)
            byte_string += int.to_bytes(len(b_value), NUM_INT_BYTES, BYTEORDER)
            byte_string += b_value
        elif val_type is str:
            value_bytes = bytes(value, ENCODING)
            byte_string += int.to_bytes(len(value_bytes), NUM_INT_BYTES, BYTEORDER)
            byte_string += value_bytes
        elif val_type is list:
            list_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(list_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += list_byte_string
        elif val_type is dict:
            try:
                dict_byte_string = dump_dict_to_json(value).encode(ENCODING)
            except TypeError as e:
                e.args = (f"Only objects of the following types are packable: ({types.keys()}",)
                raise
            byte_string += int.to_bytes(len(dict_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += dict_byte_string
        elif val_type is tuple:
            tuple_byte_string = _pack(*value)
            byte_string += int.to_bytes(len(tuple_byte_string), NUM_INT_BYTES, BYTEORDER)
            byte_string += tuple_byte_string
        elif val_type is bytes:
            byte_string += int.to_bytes(len(value), NUM_INT_BYTES, BYTEORDER)
            byte_string += value
        elif val_type is bool:
            byte_string += int.to_bytes(1, 1, BYTEORDER, signed=False) if value else int.to_bytes(0, 1, BYTEORDER,
                                                                                                  signed=False)
        elif isinstance(val_type(), type(None)):
            pass
        else:
            raise Exception("Unknown data type: " + str(val_type) + "\t(in Datatypes.Main.pack_values()")
    return byte_string


def _unpack(bytes_: Union[bytes, 'ByteStream']) -> tuple:
    """Converts back a bytes like object to its original objects"""
    if isinstance(bytes_, bytes):
        byte_stream = ByteStream(bytes_)
    else:
        byte_stream = bytes_
    if byte_stream.reached_end:
        return ()
    values = []
    while not byte_stream.reached_end:
        type_num = int.from_bytes(byte_stream.next_bytes(NUM_TYPE_BYTES), BYTEORDER)
        try:
            val_type = types[type_num]
        except KeyError:
            raise KeyError()
        value: Any
        if val_type is int:
            value = byte_stream.next_int()
        elif val_type is float:
            val_len = byte_stream.next_int()
            value = float.fromhex(str(byte_stream.next_bytes(val_len), ENCODING))
        elif val_type is str:
            val_len = byte_stream.next_int()
            value = str(byte_stream.next_bytes(val_len), ENCODING)
        elif val_type is list:
            len_list_string = byte_stream.next_int()
            value = list(_unpack(byte_stream.next_bytes(len_list_string)))
        elif val_type is dict:
            len_dict_string = byte_stream.next_int()
            value = load_dict_from_json(byte_stream.next_bytes(len_dict_string).decode(ENCODING))
        elif val_type is tuple:
            len_tuple_string = byte_stream.next_int()
            value = tuple(_unpack(byte_stream.next_bytes(len_tuple_string)))
        elif val_type is bytes:
            val_len = byte_stream.next_int()
            value = byte_stream.next_bytes(val_len)
        elif val_type is bool:
            value = True if int.from_bytes(byte_stream.next_bytes(1), BYTEORDER, signed=False) == 1 else False
        elif isinstance(val_type(), type(None)):
            value = None
        else:
            raise Exception("Unknown data type: " + str(val_type) + "\t(in " + str(__name__) + ".pack_values()")
        values.append(value)
    return tuple(values)


class ByteStream:
    """This class utilises the bytes object. Among other things, it stores the bytes string and the idx. All `next`
    functions move the idx."""

    def __init__(self, byte_string: bytes) -> None:
        self.byte_string = byte_string
        self.idx = 0
        self.length = len(byte_string)
        self.remaining_length = self.length
        self.reached_end = self.remaining_length <= 0

    def next_int(self) -> int:
        """Converts the next bytes into an integer."""
        byte_string = self.next_bytes(NUM_INT_BYTES)
        return int.from_bytes(byte_string, BYTEORDER, signed=True)

    def next_bytes(self, num_bytes: int) -> bytes:
        assert num_bytes >= 0, f"This function is not meant to be called with negative values ({num_bytes})"
        try:
            return self.byte_string[self.idx: self.idx + num_bytes]
        finally:
            self._inc_idx(num_bytes)
            if self.reached_end and self.idx > self.length:
                raise IndexError(f"Byte string ran out of scope: {self.idx} > {self.length}")

    def next_all_bytes(self) -> bytes:
        return self.next_bytes(self.remaining_length)

    def _inc_idx(self, amount: int) -> None:
        self.idx += amount
        self.remaining_length -= amount
        if self.remaining_length <= 0:
            self.reached_end = True

    def remove_consumed_bytes(self) -> None:
        """Deletes all bytes, that are before the idx. Resets all values to fit the new bytes string"""
        self.byte_string = self.byte_string[self.idx:]
        self.length = len(self.byte_string)
        self.remaining_length = self.length
        self.reached_end = self.length == 0
        self.idx = 0

    def __iadd__(self, other: bytes) -> 'ByteStream':
        if not isinstance(other, bytes):
            raise TypeError(f"{type(other)} is not type: bytes")
        self.byte_string += other
        added_length = len(other)
        self.length += added_length
        self.remaining_length += added_length
        self.reached_end = self.remaining_length <= 0
        return self

    def __repr__(self):
        return str(self.byte_string[:self.idx]) + "|" + str(self.byte_string[self.idx:])


class File:
    """This class represents a file that should be sent. If a file is to be sent, an object of this class shall be
    sent with the proper paths. This internally sends the file."""

    def __init__(self, src_path: str, dst_path: str) -> None:
        self.src_path = src_path
        self.dst_path = dst_path
        self.size = os.path.getsize(src_path)

    @classmethod
    def from_meta_packet(cls, file_meta_packet):
        return cls(file_meta_packet.src_path, file_meta_packet.dst_path)


def pack_int_type(int_type: int) -> bytes:
    """Packs a type described as an integer into bytes"""
    return int.to_bytes(int_type, NUM_TYPE_BYTES, BYTEORDER)


def unpack_int_type(full_byte_string: bytes) -> int:
    """Unpacks bytes into a type described as an integer"""
    return int.from_bytes(full_byte_string[:NUM_TYPE_BYTES], BYTEORDER)


def pack_int(num: int) -> bytes:
    """Packs any integer number into bytes"""
    return int.to_bytes(num, NUM_INT_BYTES, BYTEORDER, signed=True)
