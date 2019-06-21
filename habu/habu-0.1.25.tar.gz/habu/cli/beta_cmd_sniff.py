import logging
from time import sleep

import click

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import ICMP, IP, conf, sr1, L3RawSocket, sniff

def packet_callback(packet):
    print(packet.summary())

@click.command()
#@click.argument('ip')
@click.option('-i', 'interface', default=None, help='Wich interface to use (default: auto)')
@click.option('-c', 'count', default=0, help='How many packets send (default: infinit)')
#@click.option('-t', 'timeout', default=2, help='Timeout in seconds (default: 2)')
#@click.option('-w', 'wait', default=1, help='How many seconds between packets (default: 1)')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose')
def cmd_sniffer(interface, count, verbose):

    if interface:
        conf.iface = interface

    sniff(prn=packet_callback, count=count)

    return True

if __name__ == '__main__':
    cmd_sniffer()
