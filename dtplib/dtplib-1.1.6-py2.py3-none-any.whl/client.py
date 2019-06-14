import socket
import threading
import pickle
import errno
import os
from contextlib import contextmanager
from .util import LENSIZE, LENTYPE, TYPEOBJ, TYPEFILE, _decToAscii, _asciiToDec, _buildMessage, _unpackMessage, _newKeys, _asymmetricDecrypt

class Client:
    '''Client socket object.'''
    def __init__(self, onRecv=None, onDisconnected=None, blocking=False, eventBlocking=False, recvDir=None, daemon=True, jsonEncode=False):
        ''''onRecv' will be called when a packet is received.
            onRecv takes the following parameters: data, datatype (0: object, 1: file).
        'onDisconnected' will be called when the server disconnects suddenly.
            onDisconnected takes no parameters.
        If 'blocking' is True, the connect method will block until disconnecting.
        If 'eventBlocking' is True, onRecv and onDisconnected will block when called.
        'recvDir' is the directory in which files will be put in when received.
        If 'daemon' is True, all threads spawned will be daemon threads.
        If 'jsonEncode' is True, packets will be encoded using json instad of pickle.'''
        self._onRecv = onRecv
        self._onDisconnected = onDisconnected
        self._blocking = blocking
        self._eventBlocking = eventBlocking
        if recvDir is not None:
            self.recvDir = recvDir
        else:
            self.recvDir = os.getcwd()
        self._daemon = daemon
        self._jsonEncode = jsonEncode
        self._connected = False
        self._host = None
        self._port = None
        self._key = None
        self._serveThread = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, host, port):
        '''Connect to a server.'''
        if self._connected:
            raise RuntimeError("already connected to a server")
        self.sock.connect((host, port))
        self._connected = True
        self._host = host
        self._port = port
        self._doKeyExchange()
        if not self._blocking:
            self._serveThread = threading.Thread(target=self._handle)
            if self._daemon:
                self._serveThread.daemon = True
            self._serveThread.start()
        else:
            self._handle()

    def disconnect(self):
        '''Disconnect from the server.'''
        self._connected = False
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = None
        self._port = None
        self._key = None
    
    def connected(self):
        '''Whether or not the client is connected to a server.'''
        return self._connected

    def getAddr(self):
        '''Get the address of the client.'''
        return self.sock.getsockname()
    
    def getServerAddr(self):
        '''Get the address of the server.'''
        return self.sock.getpeername()

    def send(self, data):
        '''Send data to the server.'''
        if not self._connected:
            raise RuntimeError("not connected to a server")
        message = _buildMessage(data, messageType=TYPEOBJ, key=self._key, jsonEncode=self._jsonEncode)
        self.sock.send(message)

    def sendFile(self, path):
        '''Send a file or directory to the server.'''
        if not self._connected:
            raise RuntimeError("not connected to a server")
        message = _buildMessage(path, messageType=TYPEFILE, key=self._key, jsonEncode=self._jsonEncode)
        self.sock.send(message)

    def _doKeyExchange(self):
        pubkey, privkey = _newKeys()
        pickled = pickle.dumps(pubkey)
        size = _decToAscii(len(pickled))
        size = b"\x00" * (LENSIZE - len(size)) + size
        self.sock.send(size + pickled)
        size = self.sock.recv(LENSIZE)
        messageSize = _asciiToDec(size)
        message = self.sock.recv(messageSize)
        key = _asymmetricDecrypt(privkey, message)
        self._key = key

    def _handle(self):
        while self._connected:
            try:
                size = self.sock.recv(LENSIZE)
                if len(size) == 0:
                    if not self._connected:
                        return
                    else:
                        self.disconnect()
                        self._callOnDisconnected()
                        return
                messageSize = _asciiToDec(size)
                messageType = int(self.sock.recv(LENTYPE).decode("utf-8"))
                message = self.sock.recv(messageSize)
            except ConnectionResetError:
                self.disconnect()
                self._callOnDisconnected()
                return
            except OSError as e:
                if e.errno == errno.ENOTSOCK:
                    self.disconnect()
                    self._callOnDisconnected()
                    return
                elif e.errno == errno.ECONNABORTED and not self._connected:
                    return
                else:
                    raise e
            except IOError as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    continue
                else:
                    raise e
            else:
                data = _unpackMessage(message, messageType=messageType, key=self._key, recvDir=self.recvDir, jsonEncode=self._jsonEncode)
                self._callOnRecv(data, messageType)

    def _callOnRecv(self, data, messageType):
        if self._onRecv is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onRecv, args=(data, messageType))
                if self._daemon:
                    t.daemon = True
                t.start()
            else:
                self._onRecv(data, messageType)

    def _callOnDisconnected(self):
        if self._onDisconnected is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onDisconnected)
                if self._daemon:
                    t.daemon = True
                t.start()
            else:
                self._onDisconnected()

@contextmanager
def client(host, port, *args, **kwargs):
    '''Use Client object in a with statement.'''
    c = Client(*args, **kwargs)
    c.connect(host, port)
    yield c
    c.disconnect()
