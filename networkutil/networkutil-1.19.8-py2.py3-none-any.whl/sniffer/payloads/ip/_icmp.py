# encoding: utf-8

import attr
import logging_helper
from struct import unpack
from ._constants import ICMP_HEADER_LENGTH

logging = logging_helper.setup_logging()


@attr.s
class ICMPHeader(object):
    _frame = attr.ib()  # Raw ICMP Header
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)
    type = attr.ib(init=False, type=int)
    code = attr.ib(init=False, type=int)
    checksum = attr.ib(init=False, type=int)
    payload = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        icmph = unpack(u'!BBH', self._frame[:ICMP_HEADER_LENGTH])

        self.type = icmph[0]
        self.code = icmph[1]
        self.checksum = icmph[2]
        self.payload = self._frame[ICMP_HEADER_LENGTH:]

        self.log()

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'ICMP Header:')
        logging.log(level, u'    Type            : {0}'.format(self.type))
        logging.log(level, u'    Code            : {0}'.format(self.code))
        logging.log(level, u'    Checksum        : {0}'.format(self.checksum))
