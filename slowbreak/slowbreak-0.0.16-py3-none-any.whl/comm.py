"""\
Utilities to connect to ssl servers validating them with their certificate hash.
"""

import ssl
import socket
import hashlib
import functools
import logging

logger = logging.getLogger(__name__)

class InvalidFingerprint(Exception): pass

def ssl_client_socket_builder(*args, **kwargs):
    """\
Receives the same parameters as the ssl_connect method. 
 
:returns: a parameterless function that attempts to open a new connection each time is invoked 
"""
    return functools.partial(ssl_connect, *args, **kwargs)

client_socket_builder = ssl_client_socket_builder 

def ssl_connect(host, port, fingerprints, timeout=None):
    """\
Connect to a SSL server and validate that the server fingerprint is proper.
 
:param host: Host to connect to.
:param port: Port to connect to.
:param timeout: Timeout (in seconds) of the socket. Default, blocks forever.
:param fingerprints: List of acceptable server fingerprints. Each one is expressed as a hex-string.
:returns: connected socked.
:raises InvalidFingerprint: if the server fingerprint is not whitelisted.
"""
    
    try:
        fingerprints = [f.replace(":","").lower() for f in fingerprints]
        rv = ssl.wrap_socket(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
        rv.settimeout(timeout)
        rv.connect((host, port))
        rv.do_handshake(True)
        
        fingerprint = hashlib.sha256(rv.getpeercert(True)).hexdigest()
        
        if not fingerprint in fingerprints:
            rv.close()
            raise InvalidFingerprint(fingerprint)
        
        return rv
    
    except IOError:
        logger.exception("Error doing SSL conection to %s:%s" % (host, port))
        return None
    
def plain_tcp_client_socket_builder(*args, **kwargs):
    """\
Receives the same parameters as the plain_tcp_connect method. 
 
:returns: a parameterless function that attempts to open a new connection each time is invoked 
"""
    return functools.partial(plain_tcp_connect, *args, **kwargs)

class PlainTcpSocketProxy(object):
    "Wraps a plain tcp socket to be used in slowbreak"
    def __init__(self, socket):
        self.socket = socket
        
    def __getattr__(self, name):
        "Fetches attributes from the underlying socket"
        return getattr(self.socket, name)
    
    def read(self, len=1024):  # @ReservedAssignment
        "Invokes recv on the underlying socket"
        while True:
            rv = self.socket.recv(len)
            if not (rv is None):
                return rv
    
def plain_tcp_connect(host, port, timeout=None):
    """\
Connect via a plain tcp socket (no encryption). 

:param host: Host to connect to.
:param port: Port to connect to.
:param timeout: Timeout (in seconds) of the socket. Default, blocks forever.
:returns: connected socket, decorated to have the proper methods to be used by slowbreak.
"""

    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        return PlainTcpSocketProxy(socket=s)
    except IOError:
        logger.exception("Error doing plain TCP connection to %s:%s" % (host, port))
        return None
    
def close(s):
    """\
Properly close an SSL socket
 
:param s: socket to be closed
"""
    try:
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    except:
        # ignore errors.
        pass


class MockSocket(object):
    """Simulates a socket to be read and written"""
    def __init__(self, *args):
        self.parts_to_read = args
        self.written_parts = []
        
    def read(self):
        if not self.parts_to_read:
            return b""
        
        rv = self.parts_to_read[0]
        self.parts_to_read = self.parts_to_read[1:]
        
        if rv is None:
            raise ssl.SSLError("Simulating a socket that timed out")
        
        return rv
    
    def sendall(self, buf):
        self.written_parts.append(buf)
        
    def shutdown(self, ignored):
        pass
    
    def close(self):
        pass
    
    def settimeout(self, ignored):
        pass
    
