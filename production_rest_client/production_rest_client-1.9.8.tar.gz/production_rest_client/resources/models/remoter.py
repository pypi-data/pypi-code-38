#!/usr/bin/python
'''
===============================

 Copyright (c) 2013 - CNEXLabs.
 All rights reserved.

 These coded instructions and program statements are
 copyrighted works and confidential proprietary information of CNEXLabs.
 They may not be modified, copied, reproduced, distributed, or disclosed to
 third parties in any manner, medium, or form, in whole or in part.

 Filename:              vRemoteCtrl.py
 Description:           N/A
 Change History:
 Date                Author                Comments
 2019/5/22         Liangmin Huang        Initial create.

===============================
'''
import os
import sys
import socket
import multiprocessing
import yaml

SOCK_TRANS_SIZE = 1024

class Client(object):
    def __init__(self, ip_addr, port, output):
        self.ip_addr = ip_addr
        self.port = port
        self.output = output
        self.lock = multiprocessing.Lock()
        self.pipe = multiprocessing.Pipe()

        self.main = multiprocessing.Process(target=self.client_process, args=(self.pipe[0], ))
        self.main.deamon = True
        self.main.start()

    def __del__(self):
        if "main" in dir(self):
            self.main.terminate()
            del self.main

    def lock_print(self, mesg, wrap=True):
        self.lock.acquire()
        try:
            if self.output is None:
                if wrap:
                    sys.stdout.write("%s\n" % mesg)
                else:
                    sys.stdout.write(mesg)
                sys.stdout.flush()
            else:
                self.output.append(mesg)
        finally:
            self.lock.release()

    def raw_input(self, mesg):
        self.lock_print(mesg, wrap=False)
        return raw_input()

    def client_process(self, pipe):
        conn = socket.socket()
        conn.connect((self.ip_addr, self.port))
        self.lock_print("[+] %s:%s link on!" % (self.ip_addr, self.port))

        try:
            while True:
                # get command from user
                cmd = pipe.recv()
                if cmd:
                    # send command to server
                    conn.send(cmd)

                    # get result
                    recv = conn.recv(SOCK_TRANS_SIZE)
                    if not recv:
                        raise StandardError("receive none!")
                    self.lock_print(recv)

                    # send result to client
                    pipe.send(recv)
        except BaseException:
            pass
        finally:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            self.lock_print("[-] recv link down!")

    def send(self, cmd):
        self.pipe[1].send(cmd)

    def recv(self):
        return self.pipe[1].recv()

    def is_alive(self):
        return self.main.is_alive()

    def close(self):
        self.__del__()

class RemoteCtrl(object):
    def __init__(self, host, ini, output=None):
        self.ini = ini
        self.output = output
        self.srv_port = 5000
        self.disable = self._read_cfg()
        self.host = host
    def _read_cfg(self):
        if not os.path.isfile(self.ini):
            print("[RemoteCtrl] No config file found, remote function will be disable")
            return 1
        filep = open(self.ini)
        self.config = yaml.load(filep)
        return 0
    def reset_remote(self):
        cmd = 'reset'
        #print "[vRemoteCtrl] cmd: %s, IP: %s"%(cmd,ip)
        return self._remote_ctrl(cmd, self.host)
    def power_off(self):
        cmd = 'off'
        return self._remote_ctrl(cmd, self.host)
    def power_on(self):
        cmd = 'on'
        return self._remote_ctrl(cmd, self.host)
    def _remote_ctrl(self, cmd, ip_addr):
        if self.disable:
            print("Remote function is disabled, Please check config file")
            return {'result':1, 'msg':'Remote function is disabled, Please check config file'}
        srv_ip = self._get_srv_ip(ip_addr)
        if not srv_ip:
            return {'result':1, 'msg':'Serve IP Not Found'}

        clt = Client(srv_ip, self.srv_port, self.output)
        cmd = "usbrelay %s %s"%(ip_addr, cmd)
        if clt.is_alive():
            clt.send(cmd)
            result = clt.recv()
            print(result)
        clt.close()
        return {'result':0, 'msg':'Operation suceed'}
    def _get_srv_ip(self, ip_addr):
        for srv in self.config:
            sip = srv['ip']
            clist = srv['client']
            for client in clist:
                if ip_addr in client['ip']:
                    return sip
        return 0
