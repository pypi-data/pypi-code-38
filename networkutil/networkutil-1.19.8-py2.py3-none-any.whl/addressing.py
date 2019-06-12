# encoding: utf-8

import socket
import netifaces

SOCKET_IP = 0
SOCKET_PORT = 1
SOCKET_ADDRESS = 4

LOCAL_ADDRESSES = [u'localhost', u'127.0.0.1']


def get_local_interface_addresses():
    address_list = list()

    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        ipv4_addresses = addresses.get(netifaces.AF_INET, [])

        for addr in ipv4_addresses:
            ip = addr.get(u'addr')
            if ip is not None:
                address_list.append(ip)

    return address_list


def get_public_interface_addresses():

    try:
        public_interfaces = [interface[SOCKET_ADDRESS][SOCKET_IP]
                             for interface in socket.getaddrinfo(socket.getfqdn(), None)]

    except socket.gaierror:
        # Sometimes socket.getfqdn() returns a reverse lookup pointer which
        # causes socket.getaddrinfo() to throw socket.gaierror.
        public_interfaces = []

    return public_interfaces


def get_local_hostname():
    return socket.gethostname()


def get_public_hostname():
    return socket.getfqdn()


def get_my_addresses():

    addresses = list()

    # Add local addresses
    addresses += LOCAL_ADDRESSES

    # Add my hostname to addresses
    addresses.append(get_local_hostname())

    # Add my public hostname to addresses
    addresses.append(get_public_hostname())

    # Add all my interface IP's to addresses
    addresses += get_local_interface_addresses()

    # Add all my public interface IP's to addresses
    addresses += get_public_interface_addresses()

    return list(set(addresses))
