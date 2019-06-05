import sys
import socket
import logging
import ssl

from slowbreak.app import stack, ByMessageTypeApp, on
from slowbreak.session import AcceptorSessionApp
from slowbreak.constants import MsgType
from slowbreak.message import Message

logger = logging.getLogger(__name__)

def listen():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 34567))
    s.listen(5)
    return s

class AcceptorLogicApp(ByMessageTypeApp):
    
    @on(MsgType.Logon)
    def on_logon(self, message):
        logger.info("Received logon")
        self.send(Message(
            (35,MsgType.Logon),
            (98, message.get_field(98)), # Encrypt is reflected
            (108, message.get_field(108)) # HeartBeat is reflected 
        ))
        
        return message 

def start_server_session(plain_socket):
    logger.info("Starting server session")
    ssl_socket = ssl.wrap_socket(plain_socket,
        server_side=True,
        certfile="cert.pem",
        keyfile="key.pem",
        ssl_version=ssl.PROTOCOL_SSLv23
    )
    return stack( 
        ( AcceptorSessionApp, 
            dict(socket = ssl_socket, we=b"server1")
        ), 
        ( AcceptorLogicApp, dict() )
    ) 
def main(argv):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
    )
    server_socket = listen()
    logger.info("Listening for connections")
    try:
        while True:
            sock, _addr = server_socket.accept()
            start_server_session(sock)
    finally:
        server_socket.close()
    

if __name__ == '__main__':
    sys.exit( main(sys.argv) )