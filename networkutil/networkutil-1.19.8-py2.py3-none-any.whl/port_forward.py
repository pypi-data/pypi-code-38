# encoding: utf-8

import sys
import time
import socket
import getopt
from select import select
from multiprocessing import Process
import logging  # Using standard logging

# Setup logging
format_string = u'%(asctime)s - %(levelname)-10s : %(message)s'

formatter = logging.Formatter(fmt=format_string,
                              datefmt=u' %Y-%m-%d %H:%M:%S')

logging.basicConfig(level=logging.INFO,
                    format=format_string,
                    datefmt=u' %Y-%m-%d %H:%M:%S')

SVR_LIST = None

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer gets too high or delay gets too low, you can break things!
BUFFER_SIZE = 4096
DELAY = 0.0001
CHKCONFIG = False


class CreateConnection:
    def __init__(self, host, port, protocol):

        logging.debug(u'CreateConnection Class Initialising')

        # Init Params
        self.host = host
        self.port = port

        # Create socket
        self.forward = socket.socket(socket.AF_INET, protocol)

    def start(self):
        # Connect socket to server
        try:
            self.forward.connect((self.host, self.port))
            logging.debug(u'Connected socket to {ip}:{port}'.format(ip=self.host, port=self.port))
            return self.forward

        except Exception as e:
            logging.error(u'{ip}:{port}'.format(ip=self.host, port=self.port))
            logging.error(e)
            return False


class Proxy:

    def __init__(self, host, port, f_host, f_port, udp=False):

        logging.debug(u'Proxy Class Initialising')

        # Init lists
        self.open_socket_list = []
        self.open_channels = {}

        # Set config params
        self.host = host
        self.port = port
        self.forward_host = f_host
        self.forward_port = f_port
        self.udp = udp
        self.protocol = socket.SOCK_DGRAM if udp else socket.SOCK_STREAM

        # Initialise proxy server
        logging.debug(u'Initialise proxy server')
        self.server = socket.socket(socket.AF_INET, self.protocol)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server.bind((self.host, self.port))
            logging.info(u'Server created on {ip}:{port}'.format(ip=self.host, port=self.port))

        except Exception as err:
            logging.error(u'Something went wrong, unable to bind server ({ip}) to port ({port})'.format(ip=self.host,
                                                                                                        port=self.port))
            logging.error(err)

        # For TCP server set connection queue max = 200
        if not self.udp:
            logging.debug(u'Set TCP connection queue')
            self.server.listen(200)

        # Initialise temporary socket variable
        self.tmp_sock = None

    def main_loop(self):

        logging.debug(u'PROXY MAIN_LOOP()')
        logging.info(u'Server Started; UDP = {udp}'.format(udp=str(self.udp)))

        # Add server to socket list
        self.open_socket_list.append(self.server)

        while 1:

            time.sleep(DELAY)

            # Check which sockets have received data
            inputready, _, _ = select(self.open_socket_list, [], [])

            # Act on received data
            for self.tmp_sock in inputready:

                logging.debug(u'Act on socket: {sock}'.format(sock=self.tmp_sock))

                # For this server
                if self.tmp_sock == self.server:
                    logging.debug(u'For this server')
                    self.on_accept()
                    self.forward_udp() if self.udp else None
                    break

                # For connections to this server
                logging.debug(u'For connection to this server')

                try:
                    self.data = self.tmp_sock.recv(BUFFER_SIZE)
                except Exception as err:
                    logging.error(u'Error getting data from socket!')
                    logging.error(err)

                if len(self.data) == 0:
                    logging.debug(u'No data left, closing connection')
                    self.on_close()
                    break
                else:
                    if self.udp:
                        logging.debug(u'Act on UDP data')
                        self.on_recv_udp()
                    else:
                        logging.debug(u'Act on TCP data')
                        self.on_recv_tcp()

    def on_accept(self):

        logging.debug(u'PROXY ON_ACCEPT()')
        logging.info(u'incoming connection on: {c}'.format(c=self.tmp_sock.getsockname()))

        # Create connection to the proxied server
        logging.debug(u'Create connection to proxied server')
        serversock = CreateConnection(self.forward_host, self.forward_port, self.protocol).start()

        # Accept the incoming connection
        if self.udp:
            logging.debug(u'Deal with incoming UDP connection')
            self.data, clientaddr = self.tmp_sock.recvfrom(BUFFER_SIZE)
            clientsock = CreateConnection(clientaddr[0], clientaddr[1], self.protocol).start()
            self.tmp_sock = clientsock
        else:
            logging.debug(u'Deal with incoming TCP connection')
            clientsock, clientaddr = self.server.accept()

        if serversock:
            # Create client server association
            logging.info(u'{clnt} has connected'.format(clnt=clientaddr))
            self.open_socket_list.append(clientsock)
            self.open_socket_list.append(serversock)
            self.open_channels[clientsock] = serversock
            self.open_channels[serversock] = clientsock
        else:
            # Server connection error so clean up client connection
            logging.info(u'Cannot establish connection with remote server.')
            logging.info(u'Closing connection with client side {clnt}'.format(clnt=clientaddr))
            clientsock.close()

    def on_close(self):

        logging.debug(u'PROXY ON_CLOSE()')
        logging.info(u'{peer} has disconnected'.format(peer=self.tmp_sock.getpeername()))

        # remove objects from input_list
        self.open_socket_list.remove(self.tmp_sock)
        self.open_socket_list.remove(self.open_channels[self.tmp_sock])

        out = self.open_channels[self.tmp_sock]

        # close the connection with client
        logging.debug(u'Close client connection')
        self.open_channels[out].close()  # equivalent to do self.s.close()

        # close the connection with remote server
        logging.debug(u'Close server connection')
        self.open_channels[self.tmp_sock].close()

        # delete both objects from channel dict
        del self.open_channels[out]
        del self.open_channels[self.tmp_sock]

    def on_recv_tcp(self):

        logging.debug(u'PROXY ON_RECV_TCP()')
        logging.info(u'Forwarding received TCP data')
        self.open_channels[self.tmp_sock].send(self.data)
        logging.debug(repr(self.data))

    def on_recv_udp(self):

        logging.debug(u'PROXY ON_RECV_UDP()')
        logging.info(u'Forwarding UDP response data')
        peer = self.open_channels[self.tmp_sock].getpeername()
        self.server.sendto(self.data, peer)
        logging.debug(repr(self.data))

    def forward_udp(self):

        logging.debug(u'PROXY FORWARD_UDP()')
        logging.info(u'Forwarding received UDP data')
        self.open_channels[self.tmp_sock].send(self.data)
        logging.debug(repr(self.data))


def createServer(host, port, f_host, f_port, udp):
    logging.debug(u'CREATESERVER()')

    try:
        logging.info(u'Starting Server {ip}:{port}'.format(ip=u'0.0.0.0' if host == u'' else host, port=port))
        server = Proxy(host, port, f_host, f_port, udp)
        server.main_loop()

    except KeyboardInterrupt:
        logging.info(u'Shutting Down Server')

    except Exception as err:
        logging.error(u'Fatal server error for {host}:{port}'.format(host=host, port=port))
        logging.error(err)


def initialize():
    logging.debug(u'INITIALISE()')

    svr_config = SVR_LIST
    servers = {}

    try:

        for name in svr_config:

            if name not in u'ASSERT':

                logging.debug(name)
                logging.debug(svr_config[name])

                try:
                    servers[name] = Process(target=createServer, args=(svr_config[name][u'SERVER IP'],
                                                                       svr_config[name][u'SERVER PORT'],
                                                                       svr_config[name][u'FORWARD IP'],
                                                                       svr_config[name][u'FORWARD PORT'],
                                                                       svr_config[name][u'UDP']))
                    servers[name].start()

                except KeyboardInterrupt:
                    pass

                except Exception as err:
                    logging.error(u'Server {name} failed to start!'.format(name=name))
                    logging.exception(err)

        ''' Keep processes alive until Ctrl-C is pressed '''
        logging.info(u'Ready...')
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info(u'Ctrl C - Stopping server')

        for svr in servers:

            count = 5

            while servers[svr].is_alive():

                if count < 0:
                    logging.warning(u'Timeout exceeded, terminating Server')
                    servers[svr].terminate()
                else:
                    logging.info(u'Waiting... {cnt}'.format(cnt=count))
                    count -= 1

                time.sleep(1)

        logging.info(u'Shut Down Complete')

        sys.exit(0)


def check_args(argv):
    servers = {}

    try:
        opts, args = getopt.getopt(argv, u'hn:s:p:f:r:u:')

    except getopt.GetoptError:
        logging.error(u'No Config! Run port_forward.py -h for usage')
        sys.exit(2)

    for opt, arg in opts:
        if opt == u'-h':
            logging.info(
                u'If you are running from command line: python port_forward.py -d {u\'SERVER IP\': u\'10.10.1.40\', '
                u'u\'SERVER PORT\': 80, u\'FORWARD IP\': u\'10.10.1.40\', u\'FORWARD PORT\': 8080, u\'UDP\': False}')
            logging.info(u'If you are running from PyCharm then please ensure config file is loaded correctly!')
            sys.exit()

    name = []
    server = []
    port = []
    forward_server = []
    forward_port = []
    udp = []

    for opt, arg in opts:
        if opt == u'-n':
            name.append(arg)

        if opt == u'-s':
            server.append(arg)

        if opt == u'-p':
            port.append(int(arg))

        if opt == u'-f':
            forward_server.append(arg)

        if opt == u'-r':
            forward_port.append(int(arg))

        if opt == u'-u':
            if int(arg) == 0:
                udp.append(False)
            elif int(arg) == 1:
                udp.append(True)

    for n in range(0, len(name)):
        try:
            servers[name[n]] = {u'SERVER IP': server[n],
                                u'SERVER PORT': port[n],
                                u'FORWARD IP': forward_server[n],
                                u'FORWARD PORT': forward_port[n],
                                u'UDP': udp[n]}
        except IndexError:
            logging.error(u'Server {n} us missing a parameter!'.format(n=name[n]))

    return servers


if __name__ == u'__main__':

    if SVR_LIST is None:
        SVR_LIST = check_args(sys.argv[1:])

    if SVR_LIST is not None:
        initialize()
