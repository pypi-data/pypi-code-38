import socket
import ssl
from OpenSSL import SSL, crypto

from pprint import pprint

import click

from habu.lib.certclone2 import certclone


@click.command()
@click.argument('hostname')
@click.argument('port')
@click.argument('keyfile', type=click.File('w'))
@click.argument('certfile', type=click.File('w'))
@click.option('-e', 'copy_extensions', is_flag=True, default=False, help='Copy certificate extensions (default: False)')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose')
def cmd_certclone(hostname, port, keyfile, certfile, copy_extensions, verbose):

    #context = ssl.create_default_context()
    context = SSL.Context(method=SSL.TLSv1_METHOD)
    #context = SSL.Context()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = SSL.Connection(context=context, socket=sock)
    sock.settimeout(5)
    sock.set_tlsext_host_name(hostname.encode())
    sock.connect((hostname, int(port)))
    sock.setblocking(1)
    sock.do_handshake()

    chain = sock.get_peer_cert_chain()
    print(certclone(chain, copy_extensions=copy_extensions))

    #for cert in original:
    #    #print(dir(cert))
    #    print(cert.to_cryptography())

    #with open('/tmp/cert.der', 'wb') as out:
    #    out.write(original)


    #key, cert = certclone(original, copy_extensions=copy_extensions)

    #keyfile.write(key)
    #certfile.write(cert)

if __name__ == '__main__':
    cmd_certclone()
