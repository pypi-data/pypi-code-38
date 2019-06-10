#!/usr/bin/env python3

import os
import select
import socket
import ssl
import sys

from time import sleep

import click
from scapy.all import IP, IPv6


def which_source_for(ip):
    try:
        return IP(dst=ip).src
    except Exception:
        pass
    return IPv6(dst=ip).src




    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(ip, port, "Hello World 1")
        client(ip, port, "Hello World 2")
        client(ip, port, "Hello World 3")

        server.shutdown()






@click.command()
@click.argument('host')
@click.argument('port', type=click.IntRange(1, 65535))
@click.option('--family', 'family', type=click.Choice(['4', '6', '46']), default='46', help='IP Address Family')
@click.option('--ssl', 'ssl_enable', is_flag=True, default=False, help='Enable SSL')
@click.option('--crlf', 'crlf', is_flag=True, default=False, help='Use CRLF for EOL sequence')
@click.option('--protocol', type=click.Choice(['tcp', 'udp']), default='tcp', help='Layer 4 protocol to use')
@click.option('--source-ip', type=click.STRING, default=None, help='Source IP to use')
@click.option('--source-port', type=click.IntRange(0, 65535), default=0, help='Source port to use')
def cmd_nc(host, port, family, ssl_enable, crlf, source_ip, source_port, protocol):
    """Some kind of netcat/ncat replacement.

    The execution emulates the feeling of this popular tools.

    Example:

    \b
    $ habu.nc --crlf www.portantier.com 80
    Connected to 45.77.113.133 80
    HEAD / HTTP/1.0

    \b
    HTTP/1.0 301 Moved Permanently
    Date: Thu, 26 Jul 2018 21:10:51 GMT
    Server: OpenBSD httpd
    Connection: close
    Content-Type: text/html
    Content-Length: 443
    Location: https://www.portantier.com/
    """




    resolved = socket.getaddrinfo(host, port)

    families = {
        '4' :  [ socket.AF_INET ],
        '6' :  [ socket.AF_INET6 ],
        '46':  [ socket.AF_INET, socket.AF_INET6]
    }

    address = None
    for r in resolved:
        if r[0] in families[family]:
            address = r # (<AddressFamily.AF_INET6: 10>, <SocketType.SOCK_STREAM: 1>, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 80, 0, 0))

    if not address:
        print('Could not resolve {} to the ip address family selected ({})'.format(host, family), file=sys.stderr)
        sys.exit(1)

    to_send = b''
    queue_remote = b''
    queue_local = b''

    if not source_ip:
        source_ip = which_source_for(address[4][0])

    if protocol == 'tcp':
        rsocket = socket.socket(address[0], socket.SOCK_STREAM)
        lsocket = socket.socket(address[0], socket.SOCK_STREAM)
    else:
        rsocket = socket.socket(address[0], socket.SOCK_DGRAM)
        lsocket = socket.socket(address[0], socket.SOCK_DGRAM)

    rsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    rsocket.bind((source_ip, source_port))

    lsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsocket.bind(('127.0.0.1', 8080))

    if ssl_enable:
        ssl_context = ssl.SSLContext()
        rsocket = ssl_context.wrap_socket(s, server_side=False)


    lsocket.listen()

    lconnection, laddress = lsocket.accept()


    ########## CONNECT RSOCKET ###############################
    try:
        rsocket.connect((address[4][0], port))

        print('Connected to', address[4][0], port, file=sys.stderr)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)


    print(laddress, '==>', '127.0.0.1:8080', '==>', address[4][0], port)

    while True:

        iready, oready, eready = select.select([rsocket, lconnection], [], [rsocket], 1)

        for i in iready:
            if i == rsocket:
                queue_local += i.recv(4096)
            else:
                queue_remote += i.recv(4096)

        iready, oready, eready = select.select([], [rsocket, lconnection], [rsocket], 1)


        for o in oready:
            if o == rsocket:
                o.send(queue_remote)
                print(queue_remote)
                queue_remote = b''
            else:
                o.send(queue_local)
                print(queue_local)
                queue_local = b''
        sleep(1)
    s.close()


if __name__ == '__main__':
    cmd_nc()
