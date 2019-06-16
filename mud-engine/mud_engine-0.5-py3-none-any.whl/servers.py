import select
import logging
import socket
from .base import MUDObject
from .base import MUDInterface


class ServerInterface(MUDInterface):

    name = 'server'

class MUDServer(MUDObject):

    def __init__(self):
        self.interface = MUDInterface.get_interface('server')()

class MUDTCPSocket(MUDServer):

    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(False)
        self.clients = []

    def bind_and_listen(self, host, port):
        self.socket.bind((host, port))
        self.socket.listen()

    def handle_incoming_connections(self):

        from .events import ConnectionEvent

        rlist, wlist, xlist = select.select([self.socket], [], [], 0)

        # We don't have anything waiting to be read on the socket
        if not rlist:
            return []

        client_socket, addr = self.socket.accept()

        client_socket.setblocking(False)

        client = MUDTelnetClient(client_socket, addr)

        self.clients.append(client)

        logging.info("Incoming connection, created client {}".format(client))

        self.interface.event.emit_event(ConnectionEvent(client))

    def handle_incoming_messages(self):

        from .events import MessageEvent

        for client in self.clients:

            message = client.get_incoming_message()

            # No message from the client
            if message is None:
                continue

            logging.debug("Got message {} from {}".format(message, client))

            #self.interface.engine.emit_event(MessageEvent(client, message))

            client.player.handle_command(message)

class MUDClient(MUDObject):

    def handle_disconnect(self):
        pass

    def parse_message(self, message):
        pass

    def get_incoming_message(self):
        pass

    def send_message(self, message):
        pass


class MUDTelnetClient(MUDClient):

    def __str__(self):
        return "{}({}, <{}>)".format(self.__class__.__name__, self.socket, self.address)

    def __init__(self, socket, address, buffer=None, lastcheck=0):
        from .player import HumanPlayer
        self.socket = socket
        self.address = address
        self.buffer = buffer or ''
        self.lastcheck = lastcheck
        self.player = HumanPlayer(self)

    def __del__(self):
        logging.debug("Deleting {}".format(self))
        del self.socket

    def handle_disconnect(self):
        pass

    def parse_message(self, message):
        return MUDTelnetClient.TelnetMessage(self, message)

    def get_incoming_message(self):

        rlist, wlist, xlist = select.select([self.socket], [], [], 0)

        if self.socket not in rlist:
            return None

        try:
            message = self.parse_message(self.socket.recv(4096).decode("latin1"))

            if message is None:
                return None

            message = message.message.strip()

            return message

        except socket.error:
            self.handle_disconnect()

    def send_message(self, message):

        try:
            self.socket.sendall(bytearray(message, "latin1"))
        except socket.error:
            self.handle_disconnect()

    class TelnetMessage(MUDObject):

        # Different states we can be in while reading data from client
        # See _process_sent_data function
        _READ_STATE_NORMAL = 1
        _READ_STATE_COMMAND = 2
        _READ_STATE_SUBNEG = 3

        # Command codes used by Telnet protocol
        # See _process_sent_data function
        _TN_INTERPRET_AS_COMMAND = 255
        _TN_ARE_YOU_THERE = 246
        _TN_WILL = 251
        _TN_WONT = 252
        _TN_DO = 253
        _TN_DONT = 254
        _TN_SUBNEGOTIATION_START = 250
        _TN_SUBNEGOTIATION_END = 240

        def __bool__(self):
            return True if self.message else False

        def __init__(self, client, data):
            super().__init__()
            self.client = client
            self.data = data
            self.message = self._clean_message()

        def _clean_message(self):

            # start with no message and in the normal state
            message = ''
            state = self._READ_STATE_NORMAL

            # go through the data a character at a time
            for c in self.data:

                # handle the character differently depending on the state we're in:

                # normal state
                if state == self._READ_STATE_NORMAL:

                    # if we received the special 'interpret as command' code,
                    # switch to 'command' state so that we handle the next
                    # character as a command code and not as regular text data
                    if ord(c) == self._TN_INTERPRET_AS_COMMAND:
                        state = self._READ_STATE_COMMAND

                    # if we get a newline character, this is the end of the
                    # message. Set 'message' to the contents of the buffer and
                    # clear the buffer
                    elif c == "\n":
                        message = self.client.buffer
                        self.client.buffer = ""

                    # some telnet clients send the characters as soon as the user
                    # types them. So if we get a backspace character, this is where
                    # the user has deleted a character and we should delete the
                    # last character from the buffer.
                    elif c == "\x08":
                        self.client.buffer = self.client.buffer[:-1]

                    # otherwise it's just a regular character - add it to the
                    # buffer where we're building up the received message
                    else:
                        self.client.buffer += c

                # command state
                elif state == self._READ_STATE_COMMAND:

                    # the special 'start of subnegotiation' command code indicates
                    # that the following characters are a list of options until
                    # we're told otherwise. We switch into 'subnegotiation' state
                    # to handle this
                    if ord(c) == self._TN_SUBNEGOTIATION_START:
                        state = self._READ_STATE_SUBNEG

                    # if the command code is one of the 'will', 'wont', 'do' or
                    # 'dont' commands, the following character will be an option
                    # code so we must remain in the 'command' state
                    elif ord(c) in (self._TN_WILL, self._TN_WONT, self._TN_DO,
                                    self._TN_DONT):
                        state = self._READ_STATE_COMMAND

                    # for all other command codes, there is no accompanying data so
                    # we can return to 'normal' state.
                    else:
                        state = self._READ_STATE_NORMAL

                # subnegotiation state
                elif state == self._READ_STATE_SUBNEG:

                    # if we reach an 'end of subnegotiation' command, this ends the
                    # list of options and we can return to 'normal' state.
                    # Otherwise we must remain in this state
                    if ord(c) == self._TN_SUBNEGOTIATION_END:
                        state = self._READ_STATE_NORMAL

            # return the contents of 'message' which is either a string or None
            return message
