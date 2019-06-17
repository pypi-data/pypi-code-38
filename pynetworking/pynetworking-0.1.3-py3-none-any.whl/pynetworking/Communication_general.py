"""
:module: pynetworking.Communication_general
:synopsis: Important functions, classes for communication. Main module of pynetworking.
:author: Julian Sobott

public classes
----------------
Communicator, Connector, SocketAddress, Functions, to_server_id

.. autoclass:: Communicator
    :members:
    :undoc-members:
    :private-members:

.. autoclass:: Connector
    :members:
    :undoc-members:

.. autoclass:: SingleConnector
    :members:
    :undoc-members:

.. autoclass:: MultiConnector
    :members:
    :undoc-members:

.. autoclass:: MultiConnector
    :members:
    :undoc-members:

.. autoclass:: Functions
    :noindex:
    :members:
    :undoc-members:


public functions
----------------

.. autofunction:: to_server_id
.. autofunction:: to_client_id
.. autofunction:: set_encrypted_communication

private classes
-----------------

.. autoclass:: PacketBuilder
    :members:
    :undoc-members:

.. autoclass:: MetaFunctionCommunicator
    :members: __call__, __getattribute__, __getattr__

.. autoclass:: MetaSingletonConnector
    :members:
    :undoc-members:

.. autoclass:: FunctionExecutionThread

"""
import threading
import socket
import time
import traceback
import sys
from typing import Tuple, List, Dict, Optional, Callable, Any, Type, Union

from pynetworking.Cryptography import Cryptographer
from pynetworking.Logging import logger
from pynetworking.Packets import Packet, DataPacket, FunctionPacket, FileMetaPacket, Header
from pynetworking.ID_management import IDManager, remove_manager
from pynetworking.Data import ByteStream, File

SocketAddress = Tuple[str, int]

"""Server and client ids are different to separate them, when server and client both run on the same machine."""
CLIENT_ID_END = 30
SERVER_ID_END = 0  # Max 30 servers

ENCRYPTED_COMMUNICATION = True


def set_encrypted_communication(value: bool):
    """Allows to deactivate encrypted communication."""
    global ENCRYPTED_COMMUNICATION
    ENCRYPTED_COMMUNICATION = value


def to_client_id(id_: int) -> int:
    return int(id_ + CLIENT_ID_END)


def to_server_id(id_: int) -> int:
    return int(id_ + SERVER_ID_END)


class Communicator(threading.Thread):
    """Super class for all communicators. It handles a tcp-socket connection. Can send and receive packets and
    handles them. Responsible for connecting to another tcp-socket.
    """
    CHUNK_SIZE = 4096

    def __init__(self, address: SocketAddress, id_, socket_connection: socket.socket = None, from_accept=False,
                 on_close: Optional[Callable[['Communicator'], Any]] = None, local_functions=Type['Functions']) -> None:
        super().__init__(name=f"{'Client' if from_accept else 'Server'}_Communicator_thread_{id_}")
        self._recv_timeout = 1
        if socket_connection is None:
            socket_connection = socket.socket()
        self._socket_connection = socket_connection
        self._socket_connection.settimeout(self._recv_timeout)

        self._address = address
        self._id = id_
        self._is_connected = from_accept
        self._keep_connection = not from_accept
        self._packets: List[Packet] = []
        self._exit = threading.Event()
        self._time_till_next_check = 0.3
        self._on_close = on_close
        self._functions: Type['Functions'] = local_functions
        self._auto_execute_functions = from_accept
        self._closed = False
        self.wait_for_response_timeout = float("inf")
        self.cryptographer = Cryptographer()

    def run(self) -> None:
        """Connects to a tcp-socket. When it is connected, it listens to packets, that are sent from the other
        socket."""
        if not self._is_connected:
            self._connect()
        self._wait_for_new_input()

    def send_packet(self, packet: Packet) -> bool:
        """Set the proper ids and converts/packs the packet into bytes. Sends the bytes string."""
        IDManager(self._id).set_ids_of_packet(packet)
        send_data = packet.pack()
        successfully_sent = self._send_bytes(send_data)
        if not successfully_sent:
            logger.error("Could not send packet: %s", str(packet))
        return successfully_sent

    def wait_for_response(self):
        """Waits till a data-packet is received and returns it. If a function packet is received instead it is
        executed first."""
        waited = 0.
        while not self._exit.is_set():
            next_global_id = IDManager(self._id).get_next_outer_id()
            try:
                next_packet = self._packets.pop(0)
                actual_outer_id = next_packet.header.id_container.global_id
                if actual_outer_id > next_global_id:
                    logger.error(f"Packet lost! Expected outer_id: {next_global_id}. Got instead: {actual_outer_id}")
                    # TODO: handle
                elif actual_outer_id < next_global_id:
                    logger.error(f"Unhandled Packet! Expected outer_id: {next_global_id}. "
                                 f"Got instead: {actual_outer_id}")
                    # TODO: handle (if possible)
                else:
                    if isinstance(next_packet, Packet):
                        self._handle_packet(next_packet)
                    if isinstance(next_packet, FunctionPacket):
                        """execute and keep waiting for data"""
                    elif isinstance(next_packet, DataPacket):
                        return next_packet
                    elif isinstance(next_packet, FileMetaPacket):
                        """File is already transmitted."""
                        return DataPacket(**{"return": File.from_meta_packet(next_packet)})
                    else:
                        logger.error(f"Received not implemented Packet class: {type(next_packet)}")

            except IndexError:
                pass  # List is empty -> wait
            self._exit.wait(self._time_till_next_check)
            waited += self._time_till_next_check
            if waited > self.wait_for_response_timeout >= 0:
                logger.warning("wait_for_response waited too long")
                raise TimeoutError("wait_for_response waited too long")

    def _connect(self, seconds_till_next_try: float = 2, timeout: float = -1) -> bool:
        waited = 0
        while not self._exit.is_set() and not self._is_connected:
            try:
                self._socket_connection = socket.create_connection(self._address)
                self._socket_connection.settimeout(self._recv_timeout)
                self._is_connected = True
                logger.info(f"Successfully connected to: {str(self._address)}")
                return True
            except ConnectionRefusedError:
                logger.warning("Could not connect to server with address: (%s)", str(self._address))
            except OSError as e:
                logger.error("Is already connected to server")
                logger.debug(e)
                self._is_connected = True
            except socket.gaierror:
                raise ValueError(
                    f"Address error. {self._address} is not a valid address. Address must be of type {SocketAddress}")

            self._exit.wait(seconds_till_next_try)
            waited += seconds_till_next_try
            if waited > timeout >= 0:
                logger.warning("Connection timeout")
                return False
        return False

    def _wait_for_new_input(self):
        """Loop that is constantly receiving or waiting for new packets from the tcp-connection."""
        plain_byte_stream = ByteStream(b'')
        encrypted_byte_stream = ByteStream(b'')
        while not self._exit.is_set():
            if not self._exit.is_set() and not self._is_connected:
                if self._keep_connection:
                    self._connect()
                else:
                    self.stop(is_same_thread=True)
            packet = self._recv_packet(plain_byte_stream, encrypted_byte_stream)
            if packet is not None:
                if isinstance(packet, FileMetaPacket):
                    self._recv_file(packet, plain_byte_stream, encrypted_byte_stream)
                    self._packets.append(packet)
                elif self._auto_execute_functions and isinstance(packet, FunctionPacket):
                    func_thread = FunctionExecutionThread(self._id, packet, self._handle_packet)
                    func_thread.start()
                else:
                    self._packets.append(packet)

    def _recv_data(self, plain_byte_stream: ByteStream, encrypted_byte_stream: ByteStream) -> \
            Optional[bytes]:
        """Returns every chunk, that can be decrypted"""
        data = plain_byte_stream.next_all_bytes()
        plain_byte_stream.remove_consumed_bytes()
        if len(data) > 0:
            return data
        encrypted_data = encrypted_byte_stream.next_all_bytes()
        encrypted_byte_stream.remove_consumed_bytes()
        try:
            while not self._exit.is_set():
                chunk_data = self._socket_connection.recv(self.CHUNK_SIZE)
                if chunk_data == b"":
                    logger.info("Connection reset, (%s)", str(self._address))
                    self._is_connected = False
                    return None
                else:
                    if not self.cryptographer.is_encrypted_communication:
                        return chunk_data
                    if b"%%" in chunk_data:
                        corresponding_data = chunk_data.split(b"%%")[0]
                        encrypted_data += corresponding_data
                        encrypted_byte_stream += chunk_data[len(corresponding_data) + 2:]
                        data += self.cryptographer.decrypt(encrypted_data)
                        return data
                    else:
                        encrypted_data += chunk_data

        except ConnectionResetError:
            if not self._exit.is_set():
                logger.warning(f"Connection reset at ID({self._id}), {self._address}")
            self._is_connected = False

        except ConnectionAbortedError:
            if not self._exit.is_set():
                logger.warning(f"Connection aborted at ID({self._id}), {self._address}")
            self._is_connected = False

        except OSError as e:
            if not isinstance(e, socket.timeout):
                if not self._exit.is_set():
                    logger.warning("TCP connection closed while listening")
                self._is_connected = False

    def _recv_packet(self, plain_byte_stream: ByteStream, encrypted_byte_stream: ByteStream,) -> Optional[Packet]:
        """Receives bytes till a packet can be build. This packet is returned"""
        packet_builder = PacketBuilder(plain_byte_stream)
        while not self._exit.is_set():
            chunk_data = self._recv_data(plain_byte_stream, encrypted_byte_stream)
            if chunk_data == b"" or chunk_data is None:
                return None
            else:
                possible_packet = packet_builder.add_chunk(chunk_data)
                logger.debug(possible_packet)
                if possible_packet is not None:
                    return possible_packet

    def _recv_file(self, file_meta_packet: FileMetaPacket, plain_byte_stream: ByteStream,
                   encrypted_byte_stream: ByteStream,) -> None:
        """Receives bytes, till the file is fully received. The file is saved at the destination, given in the
        file_meta_packet."""
        file_path = file_meta_packet.dst_path
        existing_bytes = plain_byte_stream.next_all_bytes()
        with open(file_path, "wb+") as file:
            file.write(existing_bytes)
        remaining_bytes = file_meta_packet.file_size - len(existing_bytes)
        appended_data = b""
        with open(file_path, "ab") as file:
            while remaining_bytes > 0:
                data = self._recv_data(plain_byte_stream, encrypted_byte_stream)
                if data is None:
                    logger.error("Connection aborted, while receiving file!")
                    return
                write_data = data[:remaining_bytes]
                appended_data = data[remaining_bytes:]
                file.write(write_data)
                remaining_bytes -= len(write_data)
            plain_byte_stream += appended_data

    def _send_bytes(self, byte_string: bytes) -> bool:
        if not self._is_connected:
            self._connect(timeout=2)
        try:
            encrypted_message = self.cryptographer.encrypt(byte_string)
            if self.cryptographer.is_encrypted_communication:
                send_message = encrypted_message + b"%%"
            else:
                send_message = encrypted_message
            sent = self._socket_connection.sendall(send_message)
            # returns None on success
            return sent is None
        except OSError:
            logger.error(f"Could not send bytes {byte_string}")
            return False

    def _handle_packet(self, packet):
        """Adjusts all ids in the IDManager. Handles function-packets."""
        IDManager(self._id).update_ids_by_packet(packet)
        if isinstance(packet, FunctionPacket):
            self._received_function_packet(packet)

    def _received_function_packet(self, packet: FunctionPacket) -> None:
        """Executes the function, with all args. Packs the return value or the exception in a data-packet and sends
        it back. If a pynetworking.File is returned, a FileMetaPacket + the file itself is sent."""
        func = packet.function_name
        args = packet.args
        kwargs = packet.kwargs
        try:
            ret_value = self._functions.__getattr__(func)(*args, **kwargs)
            if isinstance(ret_value, File):
                return self._send_file(ret_value)
        except:
            ret_value = ExceptionObject(*sys.exc_info())

        ret_kwargs = {"return": ret_value}
        data_packet = DataPacket(**ret_kwargs)
        self.send_packet(data_packet)

    def _send_file(self, file: File):
        """Creates a FileMetaPacket, that is sent and followed by the file_content."""
        file_meta_packet = FileMetaPacket(file.src_path, file.size, file.dst_path)
        self.send_packet(file_meta_packet)
        with open(file.src_path, "rb") as f:
            file_data = f.read(self.CHUNK_SIZE)
            while len(file_data) > 0:
                self._send_bytes(file_data)
                file_data = f.read(self.CHUNK_SIZE)

    def stop(self, is_same_thread=False) -> None:
        """Stops all listening and the thread is joined. Send processes are not stopped and it the thread first
        stops when all data is sent."""
        if self._closed:
            logger.debug("Prevented closing already closed communicator")
        else:
            logger.info(f"Stopping communicator: {self._id}")
            self._exit.set()
            self._socket_connection.close()
            self._is_connected = False
            if not is_same_thread:
                self.join()
            remove_manager(self._id)
            if self._on_close is not None:
                try:
                    self._on_close(self)
                except TypeError:
                    pass  # no function provided
            self._closed = True

    def is_connected(self) -> bool:
        return self._is_connected

    def get_id(self) -> int:
        return self._id


class PacketBuilder:
    """Builds a packet from bytes chunk data. Bytes must be added till a packet can be built. This packet is returned"""

    def __init__(self, byte_stream: ByteStream) -> None:
        self.byte_stream = byte_stream
        self.current_header: Optional[Header] = None

    def add_chunk(self, byte_string: bytes) -> Optional[Packet]:
        """Byte string is from receiving bytes from the tcp-connection. This function rebuilds the packet from it,
        if there was enough data added."""
        self.byte_stream += byte_string
        if self.current_header is None and self.byte_stream.length >= Header.LENGTH_BYTES:
            self.current_header = Header.from_bytes(self.byte_stream)
        if self.current_header and self.byte_stream.remaining_length >= self.current_header.specific_data_size:
            packet = Packet.from_bytes(self.current_header, self.byte_stream)
            self.byte_stream.remove_consumed_bytes()
            self.current_header = None
            return packet
        return None


class MetaFunctionCommunicator(type):
    """
    Magic class.

    This class makes it possible, that functions, that are located at the other side, and should be
    transmitted of the network can be called, like they were local functions. The dunder functions of python play an
    important role in this class. Python can intercept the process of getting an attribute with `__getattribute__`.
    This function every time something is called with `x.foo` or `x.bar()`. Normally this just returns the attribute,
    but in this case we treat every attribute (except special attributes) as a function call. This function call is
    then packed into a function-packet with all its args and kwargs and is sent over the tcp-connection to the other
    side. The data-packet, that is returned, is unpacked and returned to the caller. If an exception was risen at the
    other side it also raises locally.

    This class is the metaclass for following Function classes."""

    def __call__(cls, *args, **kwargs):
        """A subclass can be called (not necessary). It is possible to call it with the `timeout` argument
        (e.g. `remote_functions(timeout=2.5).function(...)`). This way it is waited till the data-packet arrives or
        the timeout raises."""
        try:
            timeout = kwargs["timeout"]
            connector: Connector = cls.__getattr__("_connector")
            if connector and connector.communicator:
                connector.communicator.wait_for_response_timeout = timeout
        except KeyError:
            pass
        return cls

    def __getattribute__(self, item: str):
        """Intercepts the calling process of functions. To allow calling special variables there is this if block at
        the beginning.

        NOTE: that if you want to access any other attribute, you need to call it with the dunder functions, that are
        defined in the if block."""
        if item == "__getattr__":
            return type.__getattribute__(self, item)
        if item == "__setattr__":
            return type.__setattr__
        if item == "__call__":
            return type.__call__
        if item.startswith("__", 0, 2):
            return type.__getattribute__(self, item)

        def container(*args, **kwargs) -> Any:
            """Container works like a decorator container. The 'decoration' is, that it sends a function-packet and
            receives and unpacks a data-packet."""
            function_name = item
            # send function packet
            connector: Connector = self.__getattr__("_connector")
            function_packet = FunctionPacket(function_name, *args, **kwargs)
            if connector is None or connector.communicator is None:
                raise ConnectionError(
                    "Communicator is not connected!"
                    "Connect first to a server with `ServerCommunicator.connect(server_address)´")
            sent_packet = connector.communicator.send_packet(function_packet)
            if not sent_packet:
                raise ConnectionError("Could not send function to server. Check connection to server.")

            try:
                data_packet = connector.communicator.wait_for_response()
            except TimeoutError as e:
                raise e
            # unpack data packet
            return_values = data_packet.data["return"]
            if isinstance(return_values, ExceptionObject):
                # An exception was thrown at the other side!
                raise return_values.exec_type(return_values.get_formatted())
            return return_values

        return container

    def __getattr__(self, attr_name: str) -> Any:
        """Allows accessing attributes without interception. Usage: <class_object>.__getattr__("<attribute_name>")"""
        attribute = type.__getattribute__(self, attr_name)
        return attribute


class MetaSingletonConnector(type):
    """Allows singleton like connectors. Each connector is identified, by its id."""
    _instances: Dict[int, 'Connector'] = {}

    def __call__(cls, *args, **kwargs) -> 'Connector':
        id_: int = args[0]
        if id_ not in cls._instances:
            cls._instances[id_] = super(MetaSingletonConnector, cls).__call__(*args, **kwargs)
        return cls._instances[id_]

    @classmethod
    def remove(mcs, id_: int) -> 'Connector':
        return mcs._instances.pop(id_)

    @classmethod
    def remove_all(mcs) -> Dict[int, 'Connector']:
        ret = dict(mcs._instances)
        mcs._instances = {}
        return ret


class Connector:
    """Super class for :class:`MultiConnector` and :class:`SingleConnector`. The subclasses are responsible for the
    connection and communication.

    :ivar remote_functions: Class with all functions, that are available at the remote side.
    :ivar local_functions: Class with all functions, that are locally available.
    :ivar communicator: instance of :class:`Communicator`.
    :ivar _id:
    """
    remote_functions: Optional[Type['Functions']] = None
    local_functions: Optional[Type['Functions']] = None

    communicator: Optional[Communicator] = None
    _id = to_client_id(0)
    _exchanged_keys = False

    @staticmethod
    def connect(connector: Union['Connector', Type['SingleConnector']], addr: SocketAddress, blocking=True,
                timeout=float("inf"), exchange_keys_function=None) -> bool:
        """Connects the passed `connector` to the server. This is done, by creating a new :class:`Communicator`,
        that connects to the server. Also creates a relation between this connector and the remote_functions. The
        connection process can be executed in a separate thread."""
        if connector.communicator is None:
            connector.communicator = Communicator(addr, id_=connector._id, local_functions=connector.local_functions)
            try:
                connector.remote_functions.__setattr__(connector.remote_functions, "_connector", connector)
                # self argument, must be provided
            except TypeError:
                raise AttributeError("Communicator functions are not set.")
            connector.communicator.start()

            def try_connect():
                waited = 0.
                wait_time = 0.01
                while not connector.communicator.is_connected() and waited < timeout:
                    time.sleep(wait_time)
                    waited += wait_time
                if waited >= timeout:
                    logger.warning(f"Stopped trying to connect to server after {int(waited)} seconds due to timeout")
                    connector.communicator.stop()
                    # raise TimeoutError(f"Stopped trying to connect to server after {int(waited)} seconds")
                elif ENCRYPTED_COMMUNICATION is True:
                    exchange_keys_function(connector)

            if blocking:
                try_connect()
            else:
                threading.Thread(target=try_connect, name=f"Connector_{connector._id}").start()
        assert isinstance(connector.communicator, Communicator)
        return connector.communicator.is_connected()

    @staticmethod
    def close_connection(connector: Union['Connector', Type['SingleConnector']], blocking=True,
                         timeout=float("inf")) -> None:
        """Closes the connection to the server. If blocking is True, it will wait till the communicator stopped the
        connection."""
        if connector.communicator is not None:
            connector.communicator.stop()
            if blocking:
                waited = 0.
                wait_time = 0.01
                while connector.communicator.is_connected() and waited < timeout:
                    time.sleep(wait_time)
                    waited += wait_time
            connector.communicator: Optional[Communicator] = None

    @staticmethod
    def is_connected(connector: Union['Connector', Type['SingleConnector']]) -> bool:
        if connector.communicator is None:
            return False
        return connector.communicator.is_connected()

    @staticmethod
    def get_id(connector: Union['Connector', Type['SingleConnector']]):
        return connector._id


class MultiConnector(Connector, metaclass=MetaSingletonConnector):
    """Connector that allows creating multiple instances. Every instance is handled like a Singleton."""

    def __init__(self, id_: int) -> None:
        self._id = to_client_id(id_)
        self.communicator: Optional[Communicator] = None
        self._exchanged_keys = False

    def connect(self: Connector, addr: SocketAddress, blocking=True, timeout=float("inf"), exchange_keys_function=None) \
            -> bool:
        return super().connect(self, addr, blocking, timeout, exchange_keys_function)

    def close_connection(self: Connector, blocking=True, timeout=float("inf")) -> None:
        return super().close_connection(self, blocking, timeout)

    @staticmethod
    def close_all_connections() -> None:
        all_instances = MetaSingletonConnector.remove_all()
        for id_, connector in all_instances.items():
            connector.close_connection(connector)

    def is_connected(self) -> bool:
        return super().is_connected(self)

    def get_id(self):
        return super().get_id(self)

    @property
    def exchanged_keys(self):
        return self._exchanged_keys


class SingleConnector(Connector):
    """Only static accessible. Therefore only a single connector (per address) per machine possible. For most
    applications this class is sufficient and the :class:`MultiConnector` isn't needed."""

    @classmethod
    def connect(cls, addr: SocketAddress, blocking=True, timeout=float("inf"), exchange_keys_function=None) -> bool:
        return super().connect(cls, addr, blocking, timeout, exchange_keys_function)

    @classmethod
    def close_connection(cls, blocking=True, timeout=float("inf")) -> None:
        return super().close_connection(cls, blocking, timeout)

    @classmethod
    def is_connected(cls) -> bool:
        return super().is_connected(cls)

    @classmethod
    def get_id(cls):
        return super().get_id(cls)


class Functions(metaclass=MetaFunctionCommunicator):
    """Static class that contains all available local and remote functions. All functions must be stored in the
        :attr:`__dict__` attribute.

            """
    _connector: Optional[Communicator] = None

    def __new__(cls, *args, **kwargs):
        pass


class FunctionExecutionThread(threading.Thread):
    """Executes a received function in a separate thread."""
    def __init__(self, id_: int, function_packet: FunctionPacket, handle_packet: Callable) -> None:
        super().__init__(name=f"FunctionExecutionThread_{id_}")
        self._id = id_
        self._function_packet = function_packet
        self._handle_packet = handle_packet

    def run(self):
        self._handle_packet(self._function_packet)

    @property
    def id(self):
        return self._id


class ExceptionObject:

    def __init__(self, exc_type, exc_value, exc_traceback):
        self._lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        self.tb = traceback.extract_tb(exc_traceback)
        self.exec_type = exc_type

    def print_exception(self):
        for line in self._lines:
            print(line, end="", file=sys.stderr)

    def get_formatted(self):
        return "An Error occurred on the other side!\n"+"".join(self._lines)
