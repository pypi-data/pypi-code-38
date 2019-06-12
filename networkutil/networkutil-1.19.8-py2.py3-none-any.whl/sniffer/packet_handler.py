# encoding: utf-8

import attr
import datetime
import logging_helper
from pcapy import BPFProgram
from .ethernet import EthernetFrame
from .payloads import IPFrame

logging = logging_helper.setup_logging()


@attr.s
class ProcessedPayload(object):
    timestamp = attr.ib(type=datetime.datetime)
    header = attr.ib()
    bpf = attr.ib(type=BPFProgram)
    raw_frame = attr.ib(type=str)
    eth_frame = attr.ib(default=None, type=EthernetFrame)
    ip_frame = attr.ib(default=None, type=IPFrame)


@attr.s
class PacketHandler(object):
    header = attr.ib()
    frame = attr.ib()
    bpf = attr.ib()
    _processed_type = attr.ib(init=False, default=ProcessedPayload, type=ProcessedPayload)
    _processed = attr.ib(init=False, type=ProcessedPayload)

    def decode(self):
        try:
            # Create processed frame response with packet timestamp
            self._processed = self._processed_type(timestamp=datetime.datetime.now(),
                                                   header=self.header,
                                                   bpf=self.bpf,
                                                   raw_frame=self.frame)

            # parse ethernet frame
            self._processed.eth_frame = EthernetFrame(frame=self.frame)

            # Perform any pre-filter parsing
            self._pre_filter_decode()

            # Filter packets
            if self.bpf.filter(self._processed.eth_frame.raw):
                logging.debug(u'===============*===============')
                logging.debug(u'{dt}: captured {len} bytes, truncated to {cap} bytes'.format(dt=self._processed.timestamp,
                                                                                             len=self.header.getlen(),
                                                                                             cap=self.header.getcaplen()))

                try:
                    self._decode_frame()

                except Exception as err:
                    logging.error(u'Error decoding frame: {err}'.format(err=err))
                    logging.exception(err)
                    self._processed = None

                logging.debug(u'===============^===============')

        except Exception as err:
            logging.error(u'Error in packet decode: {err}'.format(err=err))
            logging.exception(err)
            self._processed = None

        # We need to return processed data for use by external processes
        return self._processed

    def _pre_filter_decode(self):

        """ Override to perform any special decoding before filter is applied """

        pass

    def _decode_frame(self):

        """ Override this to process an ethernet frame

            Note: the code below is an example that logs the processed IP headers & payload
        """

        self._processed.eth_frame.log(level=logging_helper.INFO)

        # Parse IP packets, protocol=0x8
        if hex(self._processed.eth_frame.protocol) == u'0x8':
            self._processed.ip_frame = IPFrame(self._processed.eth_frame.payload)
            self._processed.ip_frame.log(level=logging_helper.INFO)

            if self._processed.ip_frame.payload is not None:
                self._processed.ip_frame.payload.log(level=logging_helper.INFO)

        else:
            logging.info(u'Not an IP payload')

        logging.info(self._processed)
