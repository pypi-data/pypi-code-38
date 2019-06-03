import socket
import select
import threading
import pickle
import compressdir
from cryptography.fernet import Fernet
import rsa
import errno
import os
import binascii
import copy
from contextlib import contextmanager

LENSIZE = 5
LENTYPE = 1

TYPEOBJ = 0
TYPEFILE = 1

MAXSIZE = 256 ** LENSIZE - 1

def _decToAscii(dec):
    hexstr = hex(dec)[2:]
    if len(hexstr) % 2 == 1:
        hexstr = "0" + hexstr
    ascii = binascii.unhexlify(hexstr.encode())
    return ascii

def _asciiToDec(ascii):
    hexstr = binascii.hexlify(ascii)
    dec = int(hexstr, base=16)
    return dec

def _buildMessage(data, messageType=TYPEOBJ, key=None):
    if messageType == TYPEOBJ:
        data = pickle.dumps(data)
    elif messageType == TYPEFILE:
        data = compressdir.compressed(data)
    if key is not None:
        data = _encrypt(key, data)
    if len(data) > MAXSIZE:
        raise RuntimeError("maximum data packet size exceeded")
    size = _decToAscii(len(data))
    size = b"\x00" * (LENSIZE - len(size)) + size
    type = str(messageType).encode("utf-8")
    return size + type + data

def _unpackMessage(data, messageType=TYPEOBJ, key=None, recvDir=None):
    if recvDir is None:
        recvDir = os.getcwd()
    if key is not None:
        data = _decrypt(key, data)
    if messageType == TYPEOBJ:
        data = pickle.loads(data)
        return data
    elif messageType == TYPEFILE:
        os.makedirs(recvDir, exist_ok=True)
        path = compressdir.decompressed(data, newpath=recvDir)
        return path

def _newKeys(size=512):
    pubkey, privkey = rsa.newkeys(size)
    return pubkey, privkey

def _asymmetricEncrypt(pubkey, plaintext):
    ciphertext = rsa.encrypt(plaintext, pubkey)
    return ciphertext

def _asymmetricDecrypt(privkey, ciphertext):
    plaintext = rsa.decrypt(ciphertext, privkey)
    return plaintext

def _newKey():
    key = Fernet.generate_key()
    return key

def _encrypt(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    return token

def _decrypt(key, token):
    f = Fernet(key)
    data = f.decrypt(token)
    return data

class Client:
    '''Client socket object.'''
    def __init__(self, onRecv=None, onDisconnected=None, blocking=False, eventBlocking=False, recvDir=None):
        ''''onRecv' will be called when a packet is received.
            onRecv takes the following parameters: data, datatype (0: object, 1: file).
        'onDisconnected' will be called when the server disconnects suddenly.
            onDisconnected takes no parameters.
        If 'blocking' is True, the connect method will block until disconnecting.
        If 'eventBlocking' is True, onRecv and onDisconnected will block when called.
        'recvDir' is the directory in which files will be put in when received.'''
        self._onRecv = onRecv
        self._onDisconnected = onDisconnected
        self._blocking = blocking
        self._eventBlocking = eventBlocking
        if recvDir is not None:
            self.recvDir = recvDir
        else:
            self.recvDir = os.getcwd()
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
        message = _buildMessage(data, key=self._key)
        self.sock.send(message)

    def sendFile(self, path):
        '''Send a file or directory to the server.'''
        if not self._connected:
            raise RuntimeError("not connected to a server")
        message = _buildMessage(path, messageType=TYPEFILE, key=self._key)
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
                data = _unpackMessage(message, messageType=messageType, key=self._key, recvDir=self.recvDir)
                self._callOnRecv(data, messageType)

    def _callOnRecv(self, data, messageType):
        if self._onRecv is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onRecv, args=(data, messageType))
                t.daemon = True
                t.start()
            else:
                self._onRecv(data, messageType)

    def _callOnDisconnected(self):
        if self._onDisconnected is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onDisconnected)
                t.daemon = True
                t.start()
            else:
                self._onDisconnected()

class Server:
    '''Server socket object.'''
    def __init__(self, onRecv=None, onConnect=None, onDisconnect=None, blocking=False, eventBlocking=False, recvDir=None):
        ''''onRecv' will be called when a packet is received.
            onRecv takes the following parameters: client socket, data, datatype (0: object, 1: file).
        'onConnect' will be called when a client connects.
            onConnect takes the following parameters: client socket.
        'onDisconnect' will be called when a client disconnects.
            onDisconnect takes the following parameters: client socket.
        If 'blocking' is True, the start method will block until stopping.
        If 'eventBlocking' is True, onRecv, onConnect, and onDisconnect will block when called.
        'recvDir' is the directory in which files will be put in when received.'''
        self._onRecv = onRecv
        self._onConnect = onConnect
        self._onDisconnect = onDisconnect
        self._blocking = blocking
        self._eventBlocking = eventBlocking
        if recvDir is not None:
            self.recvDir = recvDir
        else:
            self.recvDir = os.getcwd()
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
            message = _buildMessage(data, key=self._keys[conn])
            conn.send(message)
        else:
            for conn in self.socks:
                if conn != self.sock:
                    message = _buildMessage(data, key=self._keys[conn])
                    conn.send(message)

    def sendFile(self, path, conn=None):
        '''Send a file or directory to a client. If conn is None, data is sent to all clients.'''
        if not self._serving:
            raise RuntimeError("not currently serving")
        if conn is not None:
            message = _buildMessage(path, messageType=TYPEFILE, key=self._keys[conn])
            conn.send(message)
        else:
            for conn in self.socks:
                if conn != self.sock:
                    message = _buildMessage(path, messageType=TYPEFILE, key=self._keys[conn])
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
                        data = _unpackMessage(message, messageType=messageType, key=self._keys[notifiedSock], recvDir=self.recvDir)
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
                t.daemon = True
                t.start()
            else:
                self._onRecv(conn, data, messageType)

    def _callOnConnect(self, conn):
        if self._onConnect is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onConnect, args=(conn,))
                t.daemon = True
                t.start()
            else:
                self._onConnect(conn)
    
    def _callOnDisconnect(self, conn):
        if self._onDisconnect is not None:
            if not self._eventBlocking:
                t = threading.Thread(target=self._onDisconnect, args=(conn,))
                t.daemon = True
                t.start()
            else:
                self._onDisconnect(conn)

@contextmanager
def client(host, port, *args, **kwargs):
    '''Use Client object in a with statement.'''
    c = Client(*args, **kwargs)
    c.connect(host, port)
    yield c
    c.disconnect()

@contextmanager
def server(host, port, *args, **kwargs):
    '''Use Server object in a with statement.'''
    s = Server(*args, **kwargs)
    s.start(host, port)
    yield s
    s.stop()
