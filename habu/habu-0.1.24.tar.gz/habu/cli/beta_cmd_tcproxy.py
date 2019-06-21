import logging
from time import sleep

import socket

import click

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import ICMP, IP, conf, sr1, L3RawSocket, sniff

def packet_callback(packet):
    print(packet.summary())

@click.command()
#@click.argument('ip')
#@click.option('-i', 'interface', default=None, help='Wich interface to use (default: auto)')
@click.option('-a', 'address', default='127.0.0.1', help='Wich address to bind (default: 127.0.0.1)')
@click.option('-p', 'port', default=8080, help='Wich port to use (default: 8080)')
#@click.option('-t', 'timeout', default=2, help='Timeout in seconds (default: 2)')
#@click.option('-w', 'wait', default=1, help='How many seconds between packets (default: 1)')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose')
def cmd_tcproxy(address, port, verbose):

    #if interface:
    #    conf.iface = interface

    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    sock.bind((address, port))
    sock.listen(3)
    self.lsock.append(sock)
    print('[*] Listening on {0} {1}'.format(address, port))
    while True:
        readable, writable, exceptional = select.select(self.lsock, [], [])
        for s in readable:
            if s == sock:
                rserver =self.remote_conn()
                if rserver:
                    client, addr = sock.accept()
                    print('Accepted connection {0} {1}'.format(addr[0], addr[1]))
                    self.store_sock(client, addr, rserver)
                    break
                else:
                    print('the connection with the remote server can\'t be \
                    established')
                    print('Connection with {} is closed'.format(addr[0]))
                    client.close()
            data = self.received_from(s, 3)
            self.msg_queue[s].send(data)
            if len(data) == 0:
                self.close_sock(s)
                break
            else:
                print('Received {} bytes from client '.format(len(data)))
                self.hexdump(data)

    return True

if __name__ == '__main__':
    cmd_tcproxy()
