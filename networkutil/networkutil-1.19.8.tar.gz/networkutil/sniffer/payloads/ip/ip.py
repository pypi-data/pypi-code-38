# encoding: utf-8

import attr
import socket
import logging_helper
from struct import unpack
from ._constants import IP_HEADER_LENGTH
from ._tcp import TCPHeader
from ._udp import UDPHeader
from ._icmp import ICMPHeader

logging = logging_helper.setup_logging()


@attr.s
class IPFrame(object):

    """ Object representation of an IP Payload """

    _frame = attr.ib()  # Raw Ethernet IP payload
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)

    version = attr.ib(default=None, type=int)
    ihl = attr.ib(default=None, type=int)
    qos = attr.ib(default=None)
    length = attr.ib(default=None, type=int)
    identification = attr.ib(default=None)
    df = attr.ib(default=None, type=bool)
    mf = attr.ib(default=None, type=bool)
    fragment_offset = attr.ib(default=None)
    ttl = attr.ib(default=None, type=int)
    protocol = attr.ib(default=None)
    checksum = attr.ib(default=None)
    src_ip = attr.ib(default=None)
    dest_ip = attr.ib(default=None)
    payload = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):

        # Parse IP header
        ip_header = self._frame[:IP_HEADER_LENGTH]

        # now unpack them :)
        iph = unpack(u'!BBHHHBBH4s4s', ip_header)

        df_mf_offset = u"{0:016b}".format(iph[4])

        self.version = iph[0] >> 4
        self.ihl = (iph[0] & 0xF) * 4
        self.qos = iph[1]
        self.length = iph[2]
        self.identification = iph[3]
        self.df = df_mf_offset[1]  # Don't fragment
        self.mf = df_mf_offset[2]  # More Fragments
        self.fragment_offset = int(df_mf_offset[3:], 2)
        self.ttl = iph[5]
        self.protocol = iph[6]
        self.checksum = iph[7]
        self.src_ip = socket.inet_ntoa(iph[8])
        self.dest_ip = socket.inet_ntoa(iph[9])

        self._decode_payload()

        self.log()

    def _decode_payload(self):

        # ICMP
        if self.protocol == 1:
            self.payload = ICMPHeader(frame=self._frame[self.ihl:])

        # TCP
        elif self.protocol == 6:
            self.payload = TCPHeader(frame=self._frame[self.ihl:])

        # UDP
        elif self.protocol == 17:
            self.payload = UDPHeader(frame=self._frame[self.ihl:])

        # some other IP protocol (e.g. IGMP)
        else:
            logging.log(self.log_level, u'Protocols other than ICMP/TCP/UDP are not supported!')

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'IP Header:')
        logging.log(level, u'    Version                : {0}'.format(self.version))
        logging.log(level, u'    IP Header Length (IHL) : {0}'.format(self.ihl))
        logging.log(level, u'    QOS                    : {0}'.format(self.qos))
        logging.log(level, u'    Length                 : {0}'.format(self.length))
        logging.log(level, u'    Identification         : {0}'.format(self.identification))
        logging.log(level, u"    Don't Fragment (DF)    : {0}".format(self.df))
        logging.log(level, u'    More Fragments (MF)    : {0}'.format(self.mf))
        logging.log(level, u'    Fragment Offset        : {0}'.format(self.fragment_offset))
        logging.log(level, u'    TTL                    : {0}'.format(self.ttl))
        logging.log(level, u'    Protocol               : {0}'.format(self.protocol))
        logging.log(level, u'    Checksum               : {0}'.format(self.checksum))
        logging.log(level, u'    Source Address         : {0}'.format(self.src_ip))
        logging.log(level, u'    Destination Address    : {0}'.format(self.dest_ip))
