"""
:module: pynetworking.Packets
:synopsis: Provides classes that are used to send data over the network. The data is packed into packets.
:author: Julian Sobott

Packets:
*********

- `FunctionPacket`: Sends function calls
- `DataPacket`: Sends return messages
- `FileMetaPacket`: Sends file meta data that is needed, when files are transmitted

Every packet class can convert its data to bytes, that can be send over the socket and can convert it back.

**General packet structure:**

- Header:
    - PacketType (Function, Data, FileMeta)
    - ID's
    - specific data size
- Specific Data: (Individual for each packet class

**General packet byte string:**

<function_id><global_id><packet_cls_id><specific_data_len><specific_packet_data>



External_use:
--------------

.. code-block:: python

    packet_one = <cls>Packet(*args, **kwargs) # Look at the individual class for exact signature
    byte_string = packet_one.pack()
    byte_stream = ByteStream(byte_string)
    header = Header.from_bytes(byte_stream)
    packet_two = Packet.from_bytes(header, byte_stream)
    self.assertEqual(packet_one, packet_two)

public classes
-----------------

.. autoclass:: Header
    :members:
    :undoc-members:

.. autoclass:: Packet
    :members:
    :undoc-members:

.. autoclass:: FunctionPacket
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: DataPacket
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: FileMetaPacket
    :members:
    :undoc-members:
    :show-inheritance:

private constants
--------------------

.. autodata:: packets

    Ddict that have for every Packetclass a unique id
"""
from typing import Union, Dict, Any, Callable, Optional

from pynetworking.utils import Ddict
from pynetworking.Logging import logger
from pynetworking.Data import pack_int_type, unpack_int_type, NUM_TYPE_BYTES, \
    general_unpack, general_pack, ByteStream, pack_int


class Header:
    """Every packet has a header. Defines meta data for each packet, that is necessary for network communication.

    :ivar id_container:
    :ivar packet_type:
    :ivar specific_data_size:
    """
    LENGTH_BYTES = 19

    def __init__(self, id_container: 'IDContainer', packet_type: int, specific_data_size: int) -> None:
        self.id_container = id_container
        self.packet_type = packet_type
        self.specific_data_size = specific_data_size

    @classmethod
    def from_packet(cls, packet: 'Packet') -> 'Header':
        from pynetworking.ID_management import IDContainer
        packet_type = packets[packet.__class__]
        id_container = IDContainer.default_init()
        specific_data_size = 0
        return cls.__call__(id_container, packet_type, specific_data_size)

    @classmethod
    def from_bytes(cls, byte_stream: ByteStream) -> 'Header':
        from pynetworking.ID_management import IDContainer
        id_container = IDContainer.from_bytes(byte_stream)
        packet_type = unpack_int_type(byte_stream.next_bytes(NUM_TYPE_BYTES))
        specific_data_size = byte_stream.next_int()
        return cls.__call__(id_container, packet_type, specific_data_size)

    def pack(self, len_packet_data: int) -> bytes:
        """id's + packet_type + len_packet_data"""
        self.specific_data_size = len_packet_data
        byte_string = b""
        byte_string += self.id_container.pack()
        byte_string += pack_int_type(self.packet_type)
        byte_string += pack_int(len_packet_data)
        return byte_string

    def __eq__(self, other):
        if not isinstance(other, Header):
            return False
        return (self.id_container == other.id_container and
                self.packet_type == other.packet_type and
                self.specific_data_size == other.specific_data_size)

    def __repr__(self):
        return (f"Header({self.id_container.__repr__()}, "
                f"{packets[self.packet_type].__name__}, {self.specific_data_size})\n\t")


class Packet:
    """Abstract super class for all packet classes. A Packet is used to pack and unpack data, to send it over a
    tcp-connection.
    :ivar header:
    """

    def __init__(self, packet: Union['FunctionPacket', 'DataPacket', 'FileMetaPacket']) -> None:
        self.header = Header.from_packet(packet)

    def pack(self) -> bytes:
        raise NotImplementedError()

    def _pack_all(self, specific_data_bytes: bytes) -> bytes:
        """Takes in the packed data from the child-class and creates a fully packed packet from it. Adds header."""
        byte_string = b""
        data_length = len(specific_data_bytes)
        byte_string += self.header.pack(data_length)
        byte_string += specific_data_bytes
        return byte_string

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> \
            Union['FunctionPacket', 'DataPacket', 'FileMetaPacket']:
        if header.packet_type not in packets.values():
            raise ValueError("Unknown packet ID: (" + str(header.packet_type) + ")")
        packet = packets[header.packet_type].from_bytes(header, byte_stream)
        packet.header = header
        return packet

    def set_ids(self, function_id: int, outer_id: int) -> None:
        assert isinstance(function_id, int) and isinstance(outer_id, int), f"Ids must be int: ({function_id, outer_id}"
        self.header.id_container.set_ids(function_id, outer_id)

    def __eq__(self, other):
        if isinstance(other, Packet):
            return self.header == other.header
        else:
            return False

    def __repr__(self):
        return str(self.header)


class DataPacket(Packet):
    """Packet to send named data.

    :ivar data: dict with all data."""

    def __init__(self, **kwargs) -> None:
        super().__init__(self)
        self.data = kwargs

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> 'DataPacket':
        num_bytes = header.specific_data_size
        data = general_unpack(byte_stream, num_bytes)[0]
        return cls.__call__(**data)

    def pack(self) -> bytes:
        specific_byte_string = general_pack(self.data)
        return super()._pack_all(specific_byte_string)

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, DataPacket):
            return self.data == other.data
        else:
            return False

    def __repr__(self):
        string = super().__repr__()
        string += str(self.data)
        return string


class FunctionPacket(Packet):
    """Packet, that stores the function name, and its args. Used to transmit function calls over the network.

    :ivar function_name:
    :ivar args:
    :ivar kwargs:
    """
    def __init__(self, func: Union[Callable, str], *args, **kwargs) -> None:
        super().__init__(self)
        if type(func) is str:
            self.function_name: str = func
        else:
            self.function_name: str = func.__name__
        self.args: tuple = args
        self.kwargs: Dict[str, Any] = kwargs

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> 'FunctionPacket':
        num_bytes = header.specific_data_size
        all_data = general_unpack(byte_stream, num_bytes)
        function_name: str = all_data[0]
        args: tuple = all_data[1]
        kwargs: dict = all_data[2]
        return cls.__call__(function_name, *args, **kwargs)

    def pack(self) -> bytes:
        specific_byte_string = general_pack(self.function_name, self.args, self.kwargs)
        return super()._pack_all(specific_byte_string)

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, FunctionPacket):
            return self.function_name == other.function_name and self.args == other.args and self.kwargs == other.kwargs
        else:
            return False

    def __repr__(self):
        return f"{super().__repr__()} => FunctionPacket({str(self.function_name)}, " \
            f"{str(self.args)}, {str(self.kwargs)})"


class FileMetaPacket(Packet):
    """Packet that is necessary when files should be sent over the network. Because files may be very big they dont
    want to be packed in one data packet. So to send a file there is the FileMetaClass necessary.

    :ivar src_path: Path where the file is currently located at the sender.
    :ivar dst_path: Path where the file shall be copied to at the receiver.
    :ivar file_size:
    """
    def __init__(self, src_path: str, size: int, dst_path: Optional[str] = None):
        super().__init__(self)
        self.src_path = src_path
        self.dst_path = dst_path
        self.file_size = size

    @classmethod
    def from_bytes(cls, header: Header, byte_stream: ByteStream) -> 'FileMetaPacket':
        num_bytes = header.specific_data_size
        all_data = general_unpack(byte_stream, num_bytes)
        src_path: str = all_data[0]
        dst_path: Optional[str] = all_data[1]
        size: int = all_data[2]
        return cls.__call__(src_path, size, dst_path)

    def pack(self) -> bytes:
        specific_byte_string = general_pack(self.src_path, self.dst_path, self.file_size)
        return super()._pack_all(specific_byte_string)

    def __eq__(self, other):
        if super().__eq__(other) and isinstance(other, FileMetaPacket):
            return self.src_path == other.src_path and self.dst_path == other.dst_path \
                   and self.file_size == other.file_size
        else:
            return False

    def __repr__(self):
        return f"{super().__repr__()} => FileMetaPacket({self.src_path}, {self.file_size}, {str(self.dst_path)})"


packets = Ddict({
    FunctionPacket: 0x101,
    DataPacket: 0x103,
    FileMetaPacket: 0x104
})
