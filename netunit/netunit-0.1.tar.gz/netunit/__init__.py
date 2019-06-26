import socket
import netifaces
from unittest2 import TestCase
from ipaddress import ip_address, ip_network, ip_interface


def tcp_probe(interface: ip_interface, destination_ip: ip_address, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    try:
        sock.bind((str(interface.ip), 0))
    except OSError as e:
        raise Exception("Could not bind source ip {} ({})".format(interface, e))

    sock.settimeout(1)

    try:
        if sock.connect_ex((str(destination_ip), port)) == 0:
            return True
        else:
            return False
    finally:
        sock.close()


def local_ips() -> [ip_interface]:
    addresses = map(lambda x: netifaces.ifaddresses(x), netifaces.interfaces())
    ips = [value[0]["addr"] for sublist in addresses for key, value in sublist.items() if key == 2]
    return list(map(lambda x: ip_interface(x), ips))


def get_interface(network: ip_network) -> ip_interface:
    for interface in local_ips():
        if interface in network:
            return interface

    return None


class NetworkTestCase(TestCase):

    @property
    def network(self) -> ip_network:
        raise NotImplementedError("you need to define network property in your test class")

    @classmethod
    def setUpClass(cls):
        cls.interface_ip = get_interface(cls.network)

    def assertReachable(self, ip: ip_address, port: int):
        if not self.interface_ip:
            self.skipTest("no interface in this net")

        available = tcp_probe(self.interface_ip, ip, port)
        self.assertTrue(available, "{}:{} should be available but is not!".format(ip, port))

    def assertNotReachable(self, ip: ip_address, port: int):
        if not self.interface_ip:
            self.skipTest("no interface in this net")

        available = tcp_probe(self.interface_ip, ip, port)
        self.assertFalse(available, "{}:{} should not be available but it is!".format(ip, port))
