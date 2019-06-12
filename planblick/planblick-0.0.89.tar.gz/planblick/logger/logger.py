import socket
from datetime import datetime
import json

class Logger:
    def __init__(self, host, port, consoleLog=False):
        self.host = host
        self.port = port
        self.consoleLog = consoleLog

    def getLogger(self):
        return self.log

    def log(self, message, kind="INFO"):
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        msg = {"source": socket.gethostname(), "time": now, "kind": kind, "message": message}
        if self.consoleLog == True:
            print(json.dumps(msg))
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((self.host, self.port))
            try:
                sock.sendall(bytes(json.dumps(msg), 'utf-8'))
            finally:
                sock.close()
