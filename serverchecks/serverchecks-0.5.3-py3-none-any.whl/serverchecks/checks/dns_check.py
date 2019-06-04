from typing import List

import dns.resolver
from dns.exception import DNSException

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class DnsCheck(AbstractCheck):
    name = 'DNS'

    def __init__(self, **kwargs) -> None:
        self.host = kwargs.get('host')
        self.records = kwargs.get('records', ('A', 'AAAA'))
        # XXX: implement delegation check
        self.check_delegation = kwargs.get('check_delegation', False)

        if self.host is None:
            raise ValueError(f'{self.name} required `host` parameter is missing')

    async def check(self) -> Outcome:
        ret: List = []
        try:
            for record in self.records:
                ret.append(dns.resolver.query(self.host, record).rrset)
            return Outcome(True, str(ret))
        except DNSException as e:
            return Outcome(False, f'DNS resolution for {self.host} failed: {e}')

    def __str__(self):
        return f'<{self.name} "{self.host}" ({self.records})>'


check_class = DnsCheck
