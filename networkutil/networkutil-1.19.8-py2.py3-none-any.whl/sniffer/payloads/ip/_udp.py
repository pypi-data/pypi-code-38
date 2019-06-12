# encoding: utf-8

import attr
import logging_helper
from struct import unpack
from._constants import UDP_HEADER_LENGTH

logging = logging_helper.setup_logging()


@attr.s
class UDPHeader(object):
    _frame = attr.ib()  # Raw UDP Header
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)
    src_port = attr.ib(init=False, type=int)
    dest_port = attr.ib(init=False, type=int)
    length = attr.ib(init=False, type=int)
    checksum = attr.ib(init=False)
    payload = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        udph = unpack(u'!HHHH', self._frame[:UDP_HEADER_LENGTH])

        self.src_port = udph[0]
        self.dest_port = udph[1]
        self.length = udph[2]
        self.checksum = udph[3]
        self.payload = self._frame[UDP_HEADER_LENGTH:]

        self.log()

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'UDP Header:')
        logging.log(level, u'    Source Port : {0}'.format(self.src_port))
        logging.log(level, u'    Dest Port   : {0}'.format(self.dest_port))
        logging.log(level, u'    Length      : {0}'.format(self.length))
        logging.log(level, u'    Checksum    : {0}'.format(self.checksum))
