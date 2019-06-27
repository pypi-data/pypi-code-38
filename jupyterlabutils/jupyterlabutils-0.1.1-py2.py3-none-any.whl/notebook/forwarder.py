import logging
import maproxy.proxyserver
import maproxy.iomanager
import tornado.netutil


class Forwarder(maproxy.proxyserver.ProxyServer):
    """This creates a TCP proxy server running on a randomly-assigned
    dynamic local port.  Pass it the target host and port to construct it.
    """
    _ioloop = None
    _thread = None
    _logger = None
    _bind_addresses = []

    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)
        sockets = tornado.netutil.bind_sockets(0, '')
        ioloop = None
        if "ioloop" in kwargs:
            ioloop = kwargs["ioloop"]
            ioloop.make_current()
            del kwargs["ioloop"]
        super().__init__(*args, **kwargs)
        self.add_sockets(sockets)
        self.bind_addresses = [x.getsockname()[:2] for x in sockets]
        self._ioloop = tornado.ioloop.IOLoop.current()

    def get_ports(self):
        """Returns a list of the ports the Forwarder is listening to."""
        return list(set(x[1] for x in self.bind_addresses))

    def get_port(self):
        """Returns the first port the Forwarder is listening to, or None."""
        rval = self.get_ports()
        if rval and len(rval) > 0:
            return rval[0]
        return None
