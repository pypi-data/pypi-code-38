# encoding: utf-8

import sys
import socket
import dns.resolver
import logging_helper
from ipaddress import IPv4Address, IPv4Network, AddressValueError, ip_address
from .config import dns_lookup, dns_forwarders
from ._exceptions import DNSQueryFailed

logging = logging_helper.setup_logging()


def move_address_to_another_network(address,
                                    network,
                                    netmask):

    address = ip_address(unicode(address))
    target_network = IPv4Network(u'{ip}/{netmask}'.format(ip=network,
                                                          netmask=netmask),
                                 strict=False)

    network_bits = int(target_network.network_address)
    interface_bits = int(address) & int(target_network.hostmask)

    target_address = network_bits | interface_bits

    return ip_address(target_address)


class DNSQuery(object):

    def __init__(self,
                 data,
                 client_address=None,
                 interface=None):

        self.data = data
        self.client_address = client_address
        self.interface = interface if interface is not None else u'default'
        self.message = u''
        self._ip = None
        self.error = u''

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self,
           ip):
        self._ip = IPv4Address(u'{ip}'.format(ip=ip))

    def resolve(self):

        name = self._decode_query()

        if name[-1] == u'.':
            name = name[:-1]

        self.message = u'DNS ({dns}): {name}: ?.?.?.?. '.format(dns=self.interface,
                                                                name=name)

        # Handle reverse lookups
        if u'.in-addr.arpa.' in name:
            # TODO: Can we not just forward these?  No will return host not IP?
            self.error = u'Cannot handle reverse lookups yet!'
            return self._bad_reply()

        logging.debug(u'resolve name: {h}'.format(h=name))

        # Check if we have a locally configured record for requested name
        try:
            redirect_record = dns_lookup.get_active_redirect_record_for_host(name)
            logging.debug(u'redirect record: {r}'.format(r=redirect_record))

        except dns_lookup.NoActiveRecordForHost:
            # Forward request
            self.message += u'Forwarding request. '
            address = self._forward_request(name)
            self.ip = address

        else:
            # Attempt to resolve locally
            self._resolve_request_locally(redirect_record)

        self.message = self.message.replace(u'?.?.?.?', self.ip.exploded)

        return self._reply()

    def _decode_query(self):

        domain = ''
        if sys.version_info.major == 2:
            optype = (ord(self.data[2]) >> 3) & 15   # Opcode bits

            if optype == 0:                     # Standard query
                ini = 12
                lon = ord(self.data[ini])
                while lon != 0:
                    domain += self.data[ini + 1: ini + lon + 1] + '.'
                    ini += lon + 1
                    lon = ord(self.data[ini])
        else:
            optype = (self.data[2] >> 3) & 15  # Opcode bits

            if optype == 0:  # Standard query
                ini = 12
                lon = self.data[ini]
                while lon != 0:
                    domain += self.data[ini + 1: ini + lon + 1].decode('latin-1') + '.'
                    ini += lon + 1
                    lon = self.data[ini]

        return domain

    def _resolve_request_locally(self,
                                 redirect_host):

        redirection = redirect_host[dns_lookup.REDIRECT_HOST]

        if redirection.lower() == u'default':
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = u'Cannot resolve default as client interface could not be determined!'
                return self._bad_reply()

            redirection = self.interface
            self.message += (u'Redirecting to default address. ({address}) '.format(address=redirection))

        elif '/' in redirection:
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = (u'Cannot resolve {redirection} as client interface could not be determined!'
                              .format(redirection=redirection))
                return self._bad_reply()

            address, netmask = redirection.split('/')
            redirection = move_address_to_another_network(address=address,
                                                          network=self.interface,
                                                          netmask=netmask)
            self.message += (u'Redirecting to {address}. '.format(address=redirection))

        # Check whether we already have an IP (A record)
        # Note: For now we only support IPv4
        try:
            IPv4Address(u'{ip}'.format(ip=redirection))

        except AddressValueError:
            # Attempt to resolve CNAME
            redirected_address = self._forward_request(redirection)

        else:
            # We already have the A record
            redirected_address = redirection

        self.message += (u'Redirecting to {redirection} '.format(redirection=redirection))

        self.ip = redirected_address

    def _forward_request(self,
                         name):

        try:
            address = self._resolve_name_using_dns_resolver(name)

        except (dns_forwarders.NoForwardersConfigured, DNSQueryFailed):
            self.message += u'No forwarders found for request. '
            address = self._resolve_name_using_socket(name)

        return address

    def _resolve_name_using_socket(self,
                                   name):

        # TODO: Ought to add some basic checking of name here

        try:
            address = socket.gethostbyname(name)
            self.message += u"(socket). "

        except socket.gaierror as err:
            raise DNSQueryFailed(u'Resolve name ({name}) using socket failed: {err} '
                                 .format(name=name,
                                         err=err))

        else:
            return address

    def _resolve_name_using_dns_resolver(self,
                                         name):

        try:
            network = IPv4Network(u'{ip}/24'.format(ip=self.interface),
                                  strict=False)

            forwarders = dns_forwarders.get_forwarders_by_interface(network.with_prefixlen)
            logging.debug(u'Using forwarder config: {fwd} '.format(fwd=forwarders))

        except (dns_forwarders.NoForwardersConfigured,
                dns_forwarders.MultipleForwardersForInterface,
                AddressValueError,
                ValueError):
            forwarders = dns_forwarders.get_default_forwarder()
            logging.debug(u'Using default forwarder config: {fwd} '.format(fwd=forwarders))

        resolver = dns.resolver.Resolver()
        resolver.timeout = 1
        resolver.lifetime = 3
        resolver.nameservers = forwarders

        try:
            result = resolver.query(qname=name,
                                    rdtype=u"A",
                                    source=self.interface)

            address = result[0].address

            self.message += u'(dns.resolver). '

            logging.debug(u'Address for {name} via dns.resolver from nameservers - {source} '
                          u'on interface {interface}: {address}'.format(name=name,
                                                                        source=u', '.join(forwarders),
                                                                        interface=self.interface,
                                                                        address=address))

        except (IndexError, dns.exception.DNSException, dns.exception.Timeout) as err:
            self.message += u'(dns.resolver failed). '
            raise DNSQueryFailed(u'dns.resolver failed: {err}'.format(err=err))

        else:
            return address

    def _reply(self):

        packet = b''
        packet += self.data[:2] + b"\x81\x80"
        packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'     # Questions and Answers Counts
        packet += self.data[12:]                                            # Original Domain Name Question
        packet += b'\xc0\x0c'                                               # Pointer to domain name
        packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'               # Response type, ttl and resource data length -> 4 bytes
        packet += self.ip.packed                                            # 4 bytes of IP

        return packet

    def _bad_reply(self):
            # TODO: Figure out how to return rcode 2 or 3
            # DNS Response Code | Meaning
            # ------------------+-----------------------------------------
            # RCODE:2           | Server failed to complete the DNS request
            # RCODE:3           | this code signifies that the domain name
            #                   | referenced in the query does not exist.
            logging.warning(self.error)
            # For now, return localhost,
            # which should fail on the calling machine
            self.ip = u'127.0.0.1'

            return self._reply()
