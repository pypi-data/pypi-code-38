# encoding: utf-8

import os
import sys
import socket
import logging_helper
from classutils.thread_pool import ThreadPool
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from networkutil.addressing import get_my_addresses
from .dns_query import DNSQuery

logging = logging_helper.setup_logging()


class DNSServer(ThreadPool):

    DEFAULT_INTERFACE = u'0.0.0.0'
    DEFAULT_PORT = 53

    def __init__(self,
                 interface=DEFAULT_INTERFACE,
                 port=DEFAULT_PORT,
                 *args,
                 **kwargs):

        super(DNSServer, self).__init__(*args,
                                        **kwargs)

        self.interface = interface
        self.port = port

        self.server_socket = None

        self._stop = True  # Set termination flag
        self._main_async_response = None

    def start(self):

        logging.info(u'Starting DNS Server on {int}:{port}...'.format(int=self.interface,
                                                                      port=self.port))

        if (sys.platform == u'darwin'
                and os.geteuid() != 0
                and self.port <= 1024):
            raise Exception(u'You are running macOS please restart with sudo!')

        # Run initialisation steps here
        self._stop = False

        try:
            self._create_socket()

        except Exception as err:
            logging.exception(err)
            logging.error(u'DNS Server failed to start, failed binding socket to destination '
                          u'({destination}:{port})'.format(destination=self.interface,
                                                           port=self.port))
            if 'win' in sys.platform:
                logging.error(u'The Internet Connection Sharing (ICS) service may have hijacked the port.')

            self._stop = True

        if not self._stop:
            logging.info(u'DNS Server Started on {int}:{port}!'.format(int=self.interface,
                                                                       port=self.port))

            # Create pool and Run Main loop
            self.create()
            self._main_async_response = self.submit_task(self._main_loop)

    def stop(self):

        logging.info(u'Stopping DNS Server, waiting for processes to complete...')

        # Signal loop termination
        self._stop = True

        # Retrieve & raise any exceptions from thread!
        if self._main_async_response is not None:
            self._main_async_response.get(timeout=60)

        self._main_async_response = None

        self.destroy()

        self.server_socket = None

        logging.info(u'DNS Server Stopped')

    def _main_loop(self):

        logging.info(u'DNS ({dns}): Waiting for lookup requests'.format(dns=self.interface))

        while not self._stop:
            try:
                data, address = self.server_socket.recvfrom(1024)

                # Pass item to worker thread
                self.submit_task(func=self._query,
                                 kwargs={u'request': data,
                                         u'address': address})

            except (socket.timeout, socket.error):
                continue

            except Exception as err:
                logging.error(u'Something went wrong in DNS Server main thread: {err}'.format(err=err))

    def _create_socket(self):
        self.server_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM)

        self.server_socket.settimeout(1)

        self.server_socket.bind((self.interface,
                                 self.port))

        logging.debug(u'DNS Server socket bound')

    def _query(self,
               request,
               address):
        try:
            logging.debug(address)
            logging.debug(repr(request))

            # Try to narrow down interface from client address
            # We are assuming a /24 network as this is the most common for LAN's

            # Start with the server interface
            interface = self.interface

            # Get the client network to test our interfaces against
            client_net = IPv4Network(u'{ip}/24'.format(ip=address[0]),
                                     strict=False)

            # Search for an interface address on the same network as the client
            for addr in get_my_addresses():
                try:
                    if IPv4Address(u'{ip}'.format(ip=addr)) in client_net:
                        interface = addr
                        break  # We found a matching address so no point looping through remaining addresses!

                except AddressValueError:
                    pass

            # Create query
            query = DNSQuery(data=request,
                             client_address=address,
                             interface=interface)

            # Make query & Respond to the client
            self.server_socket.sendto(query.resolve(), address)

            logging.info(query.message)

        except Exception as err:
            logging.exception(err)

    @property
    def active(self):
        return not self._stop
