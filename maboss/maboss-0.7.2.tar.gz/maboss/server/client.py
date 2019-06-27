from __future__ import print_function

import os
import sys
import time
import socket
import signal

from .atexit import register
from .comm import RUN_COMMAND, CHECK_COMMAND, DataStreamer

class MaBoSSClient:

    SERVER_NUM = 1 # for now

    def __init__(self, host = None, port = None, maboss_server = None, timeout=None):
        if not maboss_server:
            maboss_server = os.getenv("MABOSS_SERVER")
            if not maboss_server:
                maboss_server = "MaBoSS-server"

        self._maboss_server = maboss_server
        self._host = host
        self._port = port
        self._pid = None
        self._mb = bytearray()
        self._mb.append(0)
        self._pidfile = None

        if host == None:
            if port == None:
                port = '/tmp/MaBoSS_pipe_' + str(os.getpid()) + "_" + str(MaBoSSClient.SERVER_NUM)

            self._pidfile = '/tmp/MaBoSS_pidfile_' + str(os.getpid()) + "_" + str(MaBoSSClient.SERVER_NUM)
            MaBoSSClient.SERVER_NUM += 1

            try:
                pid = os.fork()
            except OSError as e:
                print("error fork:", e, file=sys.stderr)
                return

            if pid == 0:
                try:
                    args = [self._maboss_server, "--host", "localhost", "-q", "--port", port, "--pidfile", self._pidfile]
                    os.execvp(self._maboss_server, args)
                except Exception as e:
                    print("error while launching '" + self._maboss_server + "'", e, file=sys.stderr)
                    sys.exit(1)

            self._pid = pid
            register(self.close)
            server_started = False
            MAX_TRIES = 20
            TIME_INTERVAL = 0.1
            for try_cnt in range(MAX_TRIES):
                if os.path.exists(self._pidfile):
                    server_started = True
                    break
                time.sleep(TIME_INTERVAL)

            if not server_started:
                self._pidfile = None
                raise Exception \
                    ("MaBoSS server '" + self._maboss_server + "' on port " + port + " not started after " + str
                        (MAX_TRIES *TIME_INTERVAL) + " seconds")

            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect(port)
        else:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((host, port))

        # self._socket.settimeout(5)

    def run(self, simulation, hints={}):

        if "check" in hints and hints["check"]:
            command = CHECK_COMMAND
        else:
            command = RUN_COMMAND

        client_data = ClientData(str(simulation.network), simulation.str_cfg(), command)

        data = DataStreamer.buildStreamData(client_data, hints)
        data = self.send(data)

        return DataStreamer.parseStreamData(data, simulation, hints )

        # return maboss.maboss_server.result.Result(self, simulation, hints).getResultData()

    def send(self, data):
        self._socket.sendall(data.encode())
        self._term()
        SIZE = 4096
        ret_data = ""
        while True:
            databuf = self._socket.recv(SIZE)
            if not databuf or len(databuf) <= 0:
                break
            ret_data += databuf.decode()

        return ret_data

    def _term(self):
        self._socket.send(self._mb)

    def close(self):
        if self._pid != None:
            # print("kill", self._pid)
            os.kill(self._pid, signal.SIGTERM)
            if self._pidfile:
                os.remove(self._pidfile)
            self._pid = None
        self._socket.close()


class ClientData:

    def __init__(self, network = None, config = None, command = 'Run'):
        self._network = network
        self._config = config
        self._command = command

    def getNetwork(self):
        return self._network

    def getConfig(self):
        return self._config

    def getCommand(self):
        return self._command

    def setNetwork(self, network):
        self._network = network

    def setConfig(self, config):
        self._config = config

