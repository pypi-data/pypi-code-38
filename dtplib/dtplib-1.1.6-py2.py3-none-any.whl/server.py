import socket
import select
import threading
import pickle
import errno
import os
import copy
from contextlib import contextmanager
from .util import LENSIZE, LENTYPE, TYPEOBJ, TYPEFILE, _decToAscii, _asciiToDec, _buildMessage, _unpackMessage, _newKey, _asymmetricEncrypt

class Server:
    '''Server socket object.'''
    def __init__(self, onRecv=None, onConnect=None, onDisconnect=None, blocking=False, eventBlocking=False, recvDir=None, daemon=True, jsonEncode=False):
        ''''onRecv' will be called when a packet is received.
            onRecv takes the following parameters: client socket, data, datatype (0: object, 1: file).
        'onConnect' will be called when a client connects.
            onConnect takes the following parameters: client socket.
        'onDisconnect' will be called when a client disconnects.
            onDisconnect takes the following parameters: client socket.
        If 'blocking' is True, the start method will block until stopping.
        If 'eventBlocking' is True, onRecv, onConnect, and onDisconnect will block when called.
        'recvDir' is the directory in which files will be put in when received.
        If 'daemon' is True, all threads spawned will be daemon threads.
        If 'jsonEncode' is True, packets will be encoded using json instad of pickle.'''
        self._onRecv = onRecv
        self._onConnect = onConnect
        self._onDisconnect = onDisconnect
        self._blocking = blocking
        self._eventBlocking = eventBlocking
        if recvDir is not None:
            self.recvDir = recvDir
        else:
            self.recvDir = os.getcwd()
        self._daemon = daemon
        self._jsonEncode = jsonEncode
        self._serving = False
        self._host = None
        self._port = None
        self._keys = {}
        self._serveThread = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socks = [self.sock]
    
    def start(self, host=None, port=None):
        '''Start the server.'''
        if self._serving:
            raise RuntimeError("already serving")
        if host is None:
            host = socket.gethostname() # socket.gethostbyname(socket.gethostname())
        if port is None:
            port = 0
        self.sock.bind((host, port))
        self.sock.listen()
        self._serving = True
        self._host = host
        self._port = port
        if not self._blocking:
            self._serveThread = threading.Thread(target=self._serve)
            if self._daemon:
                self._serveThread.daemon = True
            self._serveThread.start()
        else:
            self._serve()
    
    def stop(self):
        '''Stop the server.'''
        self._serving = False
        for sock in self.socks:
            sock.close()
        self.socks = [self.sock]
        self._host = None
        self._port = None
        self._keys = {}

    def serving(self):
        '''Whether or not the server is serving.'''
        return self._serving

    def getAddr(self):
        '''Get the address of the server.'''
        return self.sock.getsockname()

    def getClientAddr(self, conn):
        '''Get the address of a client.'''
        return conn.getpeername()

    def getClients(self):
        '''Get the list of clients.'''
        clients = copy.copy(self.socks)
        clients.remove(self.sock)
        return clients

    def removeClient(self, conn):
        '''Remove a client.'''
        conn.close()
        self.socks.remove(conn)
        self._keys.pop(conn)

    def send(self, data, conn=None):
        '''Send data to a client. If conn is None, data is sent to all clients.'''
        if not self._serving:
            raise RuntimeError("not currently serving")
        if conn is not None:
            message = _buildMessage(data, messageType=TYPEOBJ, key=self._keys[conn], jsonEncode=self._jsonEncode)
            conn.send(message)
        else:
            for conn in self.socks:
                if conn != self.sock:
                    message = _buildMessage(data, messageType=TYPEOBJ, key=self._keys[conn], jsonEncode=self._jsonEncode)
                    conn.send(message)

    def sendFile(self, path, conn=None):
        '''Send a file or directory to a client. If conn is None, data is sent to all clients.'''
        if not self._serving:
            raise RuntimeError("not currently serving")
        if conn is not None:
            message = _buildMessage(path, messageType=TYPEFILE, key=self._keys[conn], jsonEncode=self._jsonEncode)
            conn.send(message)
        else:
            for conn in self.socks:
                if conn != self.sock:
                    message = _buildMessage(path, messageType=TYPEFILE, key=self._keys[conn], jsonEncode=self._jsonEncode)
                    conn.send(message)

    def _doKeyExchange(self, conn):
        size = conn.recv(LENSIZE)
        messageSize = _asciiToDec(size)
        message = conn.recv(messageSize)
        pubkey = pickle.loads(message)
        key = _newKey()
        encryptedKey = _asymmetricEncrypt(pubkey, key)
        size = _decToAscii(len(encryptedKey))
        size = b"\x00" * (LENSIZE - len(size)) + size
        conn.send(size + encryptedKey)
        self._keys[conn] = key

    def _serve(self):
        while self._serving:
            try:
                readSocks, _, exceptionSocks = select.select(self.socks, [], self.socks)
            except ValueError: # happens when a client is removed
                continue
            for notifiedSock in readSocks:
                if notifiedSock == self.sock:
                    try:
                        conn, _ = self.sock.accept()
                    except OSError as e:
                        if e.errno == errno.ENOTSOCK and not self._serving:
                            return
                        else:
                            raise e
                    self._doKeyExchange(conn)
                    self.socks.append(conn)
                    self._callOnConnect(conn)
                else:
                    try:
                        size = notifiedSock.recv(LENSIZE)
                        if len(size) == 0:
                            try:
                                self.removeClient(notifiedSock)
                            except ValueError:
                                pass
                            self._callOnDisconnect(notifiedSock)
                            continue
                        messageSize = _asciiToDec(size)
                        messageType = int(notifiedSock.recv(LENTYPE).decode("utf-8"))
                        message = notifiedSock.recv(messageSize)
                    except OSError as e:
                        if e.errno == errno.ECONNRESET or e.errno == errno.ENOTSOCK:
                            if not self._serving:
                                return
                            try:
                                self.removeClient(notifiedSock)
                            except ValueError:
                                pass
                            self._callOnDisconnect(notifiedSock)
                            continue
                        else:
                            raise e
                    else:
                        data = _unpackMessage(message, messageType=messageType, key=self._keys[notifiedSock], recvDir=self.recvDir, jsonEncode=self._jsonEncode)
                        self._callOnRecv(notifiedSock, data, messageType)
            for notifiedSock in exceptionSocks:
                try:
                    self.removeClient(notifiedSock)
                except ValueError:
                    pass
                self._callOnDisconnect(notifiedSock)

    def _callOnRecv(self, conn, data, messageType):
        if self._onRecv is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onRecv, args=(conn, data, messageType))
                if self._daemon:
                    t.daemon = True
                t.start()
            else:
                self._onRecv(conn, data, messageType)

    def _callOnConnect(self, conn):
        if self._onConnect is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onConnect, args=(conn,))
                if self._daemon:
                    t.daemon = True
                t.start()
            else:
                self._onConnect(conn)
    
    def _callOnDisconnect(self, conn):
        if self._onDisconnect is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onDisconnect, args=(conn,))
                if self._daemon:
                    t.daemon = True
                t.start()
            else:
                self._onDisconnect(conn)

@contextmanager
def server(host, port, *args, **kwargs):
    '''Use Server object in a with statement.'''
    s = Server(*args, **kwargs)
    s.start(host, port)
    yield s
    s.stop()
