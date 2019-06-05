# -*- coding: utf-8 -*-
# @Time    : 2017/5/19 9:10
# @Author  : Liu Gang
# @Site    :
# @File    : SocketTest.py
# @Software: PyCharm
import socket
import threading
import sys

import logging
import logging.config
from vatbase import LOGGER_PATH

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01, 5Jul2018, Liu Gang revise
   --sf_sendmsg增加gb2312编码
--------------------
"""
SOCKET_VER = "V1.00.01"


class SocketFunc(object):
    def __init__(self, str_host, int_port):
        logging.config.fileConfig(LOGGER_PATH)
        self.logger = logging.getLogger("socket")
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            self.logger.error(
                'Failed to create socket. Error code: ' + str(msg.args[0] + ' , Error message : ' + msg.args[1]))
            sys.exit(1)
        self.host = str_host
        self.port = int_port

    def __del__(self):
        try:
            self.s.close()
        except AttributeError:
            pass

    def sf_connect(self):
        try:
            remote_ip = socket.gethostbyname(self.host)
        except socket.gaierror:
            self.logger.error("Hostname could not be resolved!")
            return False
        else:
            # print "remoteIP:" + remote_ip
            try:
                self.s.connect((remote_ip, self.port))
            except socket.error as msg:
                self.logger.error(
                    'Failed to create socket. Error code: ' + str(msg.args[0]) + ' , Error message : ' + msg.args[1])
                return False
            else:
                return True

    def sf_sendmsg(self, str_msg='', gb_msg=None):
        try:
            if gb_msg is None:
                send_msg = str_msg
            else:
                send_msg = gb_msg.decode('utf8').encode('gb2312')
            self.s.sendto(send_msg, (self.host, self.port))
        except socket.error:
            self.logger.error("Send Error!")
            return False
        else:
            self.logger.info(str_msg)
            return True

    def sf_recvmsg(self):
        reply, addr = self.s.recvfrom(4096)
        return reply


def test():
    sf = SocketFunc("127.0.0.1", 7878)
    if sf.sf_connect():
        sf.logger.debug("Connect Success")
    sf.sf_sendmsg("starting")
    t1 = threading.Thread(target=sf.sf_recvmsg)
    t1.setDaemon(True)
    t1.start()
    sf.sf_sendmsg("start")
    t1.join()


if __name__ == "__main__":
    test()
