import socket
import struct

import logging

IPV4_ADDRESS = 1
DOMAIN_NAME = 3
IPV6_ADDRESS = 4


# packed requests --> packed address(str_len + addr_type + addr + port)
def unpack_request_data(data):
    socks_version, = struct.unpack('>B', data[0])
    cmd, = struct.unpack('>B', data[1])

    addr_type, = struct.unpack('>B', data[3])
    addr_to_send = data[3]

    if addr_type == IPV4_ADDRESS:
        ip_address = data[4: 8]
        addr_to_send += ip_address

    if addr_type == DOMAIN_NAME:
        domain_len, = struct.unpack('>B', data[4])
        addr_to_send += data[4: 5 + domain_len]

    if addr_type == IPV6_ADDRESS:
        ipv6_address = data[4: 20]
        print "ipv6", ipv6_address
        addr_to_send += ipv6_address

    port, = struct.unpack('>H', data[-2:])
    addr_to_send += data[-2:]
    logging.debug("version:{}, cmd:{}, addr_type:{}, port:{}".format(socks_version, cmd, addr_type, port))

    length = struct.pack('>B', len(addr_to_send))

    addr_to_send = length + addr_to_send
    return addr_to_send


def socks5_server_reply(port):
    reply = b"\x05\x00\x00\x01"
    reply += socket.inet_aton('0.0.0.0') + struct.pack('>H', port)
    return reply


# packed address --> unpacked host, port, request
def unpack_address(data):
    data_length, = struct.unpack('>B', data[0])

    address = data[0: 1 + data_length]
    addr_type, = struct.unpack('>B', address[1])

    host = ''

    if addr_type == IPV4_ADDRESS:
        host = socket.inet_ntoa(address[2: 6])

    if addr_type == DOMAIN_NAME:
        length = ord(address[2])
        host = address[3: 3 + length]

    if addr_type == IPV6_ADDRESS:
        host = socket.inet_ntop(socket.AF_INET6, address[2: 18])

    port, = struct.unpack('>H', address[-2:])

    request = data[1 + data_length:]
    return host, port, request


def test_address_packing():
    assert unpack_address(unpack_request_data('\x05\x01\x00\x01\x97e%\x8c\x01\xbb')) == ('151.101.37.140', 443, '')
    assert unpack_address(unpack_request_data('\x05\x01\x00\x03\x0ewww.google.com\x01\xbb')) == (
        'www.google.com', 443, '')
    # not tested in real ipv6 network environment
    assert unpack_address(unpack_request_data('\x05\x01\x00\x04 \x01H`H`\x00\x00\x00\x00\x00\x00\x00\x00\x88\x88\x00P')) \
           == ('2001:4860:4860::8888', 80, '')
    assert unpack_address(
        unpack_request_data('\x05\x01\x00\x04$\x04h\x00@\x05\x08\x05\x00\x00\x00\x00\x00\x00\x10\x11\x00P')) \
           == ('2404:6800:4005:805::1011', 80, '')


if __name__ == '__main__':
    test_address_packing()
