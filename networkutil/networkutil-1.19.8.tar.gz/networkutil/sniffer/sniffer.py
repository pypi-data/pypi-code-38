# encoding: utf-8

import attr
import pcapy
import logging_helper
from queue import Queue
from classutils.thread_pool import ThreadPoolMixIn
from ._constants import (FILTER,
                         SNAPLEN,
                         PROMISCUOUS,
                         READ_TIMEOUT,
                         FILTER_OPTIMISE,
                         FILTER_NETMASK)
from .packet_handler import PacketHandler

logging = logging_helper.setup_logging()


@attr.s
class Sniffer(ThreadPoolMixIn):
    _dev = attr.ib(type=str)
    _filter = attr.ib(default=FILTER, type=str)
    _snaplen = attr.ib(default=SNAPLEN, type=int)
    _promiscuous = attr.ib(default=PROMISCUOUS, type=bool)
    _to_ms = attr.ib(default=READ_TIMEOUT, type=int)
    _handler = attr.ib(default=PacketHandler, type=PacketHandler)
    _optimise = attr.ib(default=FILTER_OPTIMISE, type=int)
    _netmask = attr.ib(default=FILTER_NETMASK, type=int)
    _started = attr.ib(init=False, default=False, type=bool)
    queue = attr.ib(default=None, type=Queue)
    _async_response = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        super(Sniffer, self).__init__()

        if self.queue is None:
            self.queue = Queue()

        self.open_pool()

        # Open interface for capturing.
        self._pcap = pcapy.open_live(self._dev,
                                     self._snaplen,
                                     self._promiscuous,
                                     self._to_ms)

        # We only support ethernet for now
        if self._pcap.datalink() != pcapy.DLT_EN10MB:
            raise Exception(u'Only Ethernet connections are currently supported.')

        # Create the BPF filter. See tcpdump(3).
        self._bpf = pcapy.compile(pcapy.DLT_EN10MB,
                                  self._snaplen,
                                  self._filter,
                                  self._optimise,
                                  self._netmask)

    def __del__(self):
        self.close_pool()

    def _sniff(self):
        try:
            logging.info(u"Listening on {dev}: net={net}, "
                         u"mask={mask}, linktype={link}".format(dev=self._dev,
                                                                net=self._pcap.getnet(),
                                                                mask=self._pcap.getmask(),
                                                                link=self._pcap.datalink()))

            # Sniff ad infinitum.
            # self._handler shall be invoked by self._pcap for every packet.
            while self._started:
                try:
                    self._pcap.dispatch(0, self._handle)

                except Exception as err:
                    logging.error(u'Error dispatching handler: {err}'.format(err=err))
                    logging.exception(err)

        except Exception as err:
            logging.exception(u'Exception in sniffer thread: {e}'.format(e=err))

    def _handle(self,
                header,
                frame):

        try:
            decoded_frame = self._handler(header=header,
                                          frame=frame,
                                          bpf=self._bpf).decode()

            if decoded_frame is not None:
                self.queue.put(decoded_frame)
                # TODO: Need to put some limits on the queue to stop its memory growing when there is no queue consumer!
                # TODO: This should probably be non-blocking, so if full drop the oldest item in queue so we can insert!

        except Exception as err:
            logging.error(u'Error handling Packet: {err}'.format(err=err))
            logging.exception(err)

    def start(self):
        self._started = True
        self._async_response = self._pool.submit_task(self._sniff)

    def stop(self):
        self._started = False

        # Retrieve & raise any exceptions from thread!
        if self._async_response is not None:
            self._async_response.get(timeout=60)

        self._async_response = None
