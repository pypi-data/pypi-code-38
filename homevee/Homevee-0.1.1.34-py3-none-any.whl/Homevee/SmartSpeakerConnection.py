#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import traceback
from _thread import start_new_thread

from Homevee.Helper import Logger

SPEAKER_HOST = ''
SPEAKER_PORT = 7888

class SmartSpeakerConnection():
    def __init__(self):
        pass

    def start_loop(self):
        start_new_thread(self.smart_speaker_loop, ())

    def smart_speaker_loop(self):
        while(True):
            self.start_server_socket()
        return

    def clientthread(self, conn):
        return


    def listen_for_requests(self, s):
        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        Logger.log(('Connected with ' + addr[0] + ':' + str(addr[1])))

        # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(self.clientthread, (conn,))

    def start_server_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Logger.log('Socket created')

        # send_notification_to_users(['sascha'], "Titel", "Nachricht", Database())

        # Bind socket to local host and port
        try:
            s.bind((SPEAKER_HOST, SPEAKER_PORT))
        except socket.error as msg:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            Logger.log(('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]))

        Logger.log('Socket bind complete')

        # Start listening on socket
        s.listen(10)
        Logger.log('Socket now listening')

        while 1:
            try:
                self.listen_for_requests(s)
            except:
                if(Logger.IS_DEBUG):
                    traceback.print_exc()
                break

        s.close()