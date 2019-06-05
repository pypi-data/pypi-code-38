import time
import socket
import sys
import select

class TCPConn:
    def __init__(self, ConnTarget):
        #IP and port
        #9760 is the default address of modules -
        #In Qis do a '$list details' and it will show you ports
        TCP_PORT = 9760
        self.ConnTarget = ConnTarget
        #Creates connection socket
        self.Connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Sets buffer size
        self.BufferSize = 4096
        #Opens the ocnnection
        self.Connection.connect((self.ConnTarget, TCP_PORT))

    def close(self):
        self.Connection.close()
        return True

    def sendCommand(self, Command, readUntilCursor = True):

        #Prepares the message to be sent
        MESSAGE_ready = (chr(len(Command + "\r\n")) + chr(0) + Command + "\r\n").encode()

        #Sends the message
        self.Connection.send(MESSAGE_ready)

        #Receives raw the answer
        data_raw = self.Connection.recv(self.BufferSize)

        #Decodes data and ignores the first character
        data = data_raw.decode("ISO-8859-1")[1:-3]


        return data

