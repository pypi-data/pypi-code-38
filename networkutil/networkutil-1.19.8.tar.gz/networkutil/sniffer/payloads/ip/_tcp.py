# encoding: utf-8

import attr
import logging_helper
from struct import unpack
from ._constants import TCP_HEADER_LENGTH

logging = logging_helper.setup_logging()


@attr.s
class TCPHeader(object):
    _frame = attr.ib()  # Raw TCP Header
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)
    src_port = attr.ib(init=False, type=int)
    dest_port = attr.ib(init=False, type=int)
    sequence_number = attr.ib(init=False, type=int)
    acknowledgement_number = attr.ib(init=False, type=int)
    data_offset = attr.ib(init=False, type=int)
    control_flags = attr.ib(init=False)
    window_size = attr.ib(init=False, type=int)
    checksum = attr.ib(init=False)
    urgent_pointer = attr.ib(init=False, type=bool)
    payload = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        tcph = unpack(u'!HHLLHHHH', self._frame[:TCP_HEADER_LENGTH])

        data_offset_control = u"{0:016b}".format(tcph[4])

        self.src_port = tcph[0]
        self.dest_port = tcph[1]
        self.sequence_number = tcph[2]
        self.acknowledgement_number = tcph[3]
        self.data_offset = int(data_offset_control[:4], 2) * 4  # TCP Header length
        self.control_flags = data_offset_control[7:]
        self.window_size = tcph[5]
        self.checksum = tcph[6]
        self.urgent_pointer = tcph[7]
        self.payload = self._frame[self.data_offset:]

        self.log()

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'TCP Header:')
        logging.log(level, u'    Source Port                     : {0}'.format(self.src_port))
        logging.log(level, u'    Dest Port                       : {0}'.format(self.dest_port))
        logging.log(level, u'    Sequence Number                 : {0}'.format(self.sequence_number))
        logging.log(level, u'    Acknowledgement                 : {0}'.format(self.acknowledgement_number))
        logging.log(level, u'    TCP header length (data offset) : {0}'.format(self.data_offset))
        logging.log(level, u'    Control Flags                   : {0}'.format(self.control_flags))
        logging.log(level, u'    Window Size                     : {0}'.format(self.window_size))
        logging.log(level, u'    Checksum                        : {0}'.format(self.checksum))
        logging.log(level, u'    Urgent Pointer                  : {0}'.format(self.urgent_pointer))
