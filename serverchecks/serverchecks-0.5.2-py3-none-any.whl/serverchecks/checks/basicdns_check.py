import socket
from typing import List

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class BasicDnsAbstractCheck(AbstractCheck):
    """
    Check that passed FQDN (fully-qualified domain name) resolves to an Internet address using a resolver local
    to the running script. Allows detection of DNS-related issues such as non-existent hostnames, expired domains etc.

    Parameters:

    * `host` (mandatory) - string, the hostname to check
      Example: `host: www.webcookies.org`
    * `expect` (optional) - list of strings, specific IP addresses that the hostname should resolve to
      Example: `expect: ['94.130.162.156', '2a01:4f8:13b:29a3::2']
    """
    name = 'BasicDNS'

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.expect = kwargs.get('expect', [])

    async def check(self) -> Outcome:
        try:
            gai_result: List = socket.getaddrinfo(self.host, None, proto=socket.IPPROTO_TCP)
            gai_ips: List[str] = [x[4][0] for x in gai_result]
        except socket.gaierror as e:
            return Outcome(False, f'DNS resolution for {self.host} failed: {e}')
        else:
            # check for expected IPs; this will be no-op if `expect` is an empty array
            for expected_ip in self.expect:
                if expected_ip not in gai_ips:
                    return Outcome(False,
                                   f'DNS resolution for {self.host} failed because {expected_ip} not found among the returned IPs: {gai_ips}')

            return Outcome(True, f'{self.host} {gai_ips}')

    def __str__(self):
        return f'<{self.name} "{self.host}">'


check_class = BasicDnsAbstractCheck
