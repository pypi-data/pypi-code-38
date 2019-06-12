# encoding: utf-8

import attr
import logging_helper
from struct import unpack

logging = logging_helper.setup_logging()


@attr.s
class VLANTag(object):
    _tag = attr.ib()  # Raw VLAN Tag
    log_level = attr.ib(default=logging_helper.DEBUG, type=int)
    priority = attr.ib(init=False, default=0, type=int)
    cfi = attr.ib(init=False, default=0, type=int)
    id = attr.ib(init=False, default=1, type=int)
    protocol = attr.ib(init=False, default=0)
    protocol_string = attr.ib(init=False)

    def __attrs_post_init__(self):
        # Decode VLAN Tag
        # 000. .... .... .... = Priority: 0
        # ...0 .... .... .... = CFI: 0
        # .... 0000 0010 0000 = ID: 32
        eth_vlan_tag = unpack(u'!HH', self._tag)
        binary_vlan_tag = u"{0:016b}".format(eth_vlan_tag[0])

        self.priority = int(binary_vlan_tag[:3], 2)
        self.cfi = int(binary_vlan_tag[4], 2)
        self.id = int(binary_vlan_tag[4:], 2)
        self.protocol = eth_vlan_tag[1]
        self.update_protocol_string()

        self.log()

    def update_protocol_string(self):
        self.protocol_string = u'{p:0=#4x}'.format(p=self.protocol)

    def log(self,
            level=None):

        if level is None:
            level = self.log_level

        logging.log(level, u'VLAN Tag:')
        logging.log(level, u'    VLAN Priority   : {0}'.format(self.priority))
        logging.log(level, u'    VLAN CFI        : {0}'.format(self.cfi))
        logging.log(level, u'    VLAN ID         : {0}'.format(self.id))
        logging.log(level, u'    VLAN Protocol   : {0}'.format(self.protocol_string))
