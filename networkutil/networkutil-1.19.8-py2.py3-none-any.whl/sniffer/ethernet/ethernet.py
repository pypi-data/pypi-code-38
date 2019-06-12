#!/usr/bin/env python

import attr
import socket
import logging_helper
from struct import unpack
from ._constants import (ETHERNET_HEADER_LENGTH,
                         ETHERNET_VLAN_LENGTH)
from .vlan import VLANTag

logging = logging_helper.setup_logging()


@attr.s
class EthernetFrame(object):
    _frame = attr.ib()  # Raw Ethernet packet
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)
    header_length = attr.ib(init=False, default=ETHERNET_HEADER_LENGTH, type=int)
    dest_mac = attr.ib(init=False)
    src_mac = attr.ib(init=False)
    protocol = attr.ib(init=False, default=0)
    protocol_string = attr.ib(init=False)
    vlan_tag = attr.ib(init=False, default=None, type=VLANTag)
    payload = attr.ib(init=False)

    def __attrs_post_init__(self):
        # dest_mac (6), src_mac (6), eth_type/size (2)
        eth_header = unpack(u'!6s6sH', self._frame[:ETHERNET_HEADER_LENGTH])

        self.dest_mac = self._decode_eth_address(eth_header[0])
        self.src_mac = self._decode_eth_address(eth_header[1])
        self.protocol = socket.ntohs(eth_header[2])
        self.update_protocol_string()

        # Check for and handle VLAN Tags
        if hex(self.protocol) == u'0x81':
            vlan_tag = VLANTag(tag=self._frame[ETHERNET_HEADER_LENGTH:ETHERNET_VLAN_LENGTH])

            # Update header protocol
            self.protocol = socket.ntohs(vlan_tag.protocol)
            self.update_protocol_string()

            # Update header VLAN Tag
            self.vlan_tag = vlan_tag

            # Update header length variable as its size differs based on whether we have a VLAN Tag or not!
            self.header_length = ETHERNET_VLAN_LENGTH

        self.payload = self._frame[self.header_length:]

        self.log()

    @property
    def raw(self):
        return self._frame

    def update_protocol_string(self):
        self.protocol_string = u'{p:0=#4x}'.format(p=self.protocol)

    @staticmethod
    def _decode_eth_address(addr):
        # Convert a string of 6 characters of ethernet address into a dash separated hex string
        return u'{0:02x}:{1:02x}:{2:02x}:{3:02x}:{4:02x}:{5:02x}'.format(ord(addr[0]),
                                                                         ord(addr[1]),
                                                                         ord(addr[2]),
                                                                         ord(addr[3]),
                                                                         ord(addr[4]),
                                                                         ord(addr[5]))

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'Ethernet Header:')
        logging.log(level, u'    Destination MAC : {0}'.format(self.dest_mac))
        logging.log(level, u'    Source MAC      : {0}'.format(self.src_mac))
        logging.log(level, u'    Protocol        : {0}'.format(self.protocol_string))
        logging.log(level, u'    VLAN Tag        : {0}'.format(self.vlan_tag))
