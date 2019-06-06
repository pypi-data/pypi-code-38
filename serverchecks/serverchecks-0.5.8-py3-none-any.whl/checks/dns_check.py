from typing import Tuple

import dns
from dns.exception import DNSException

from serverchecks import Outcome


async def dns_check(name: str, records: Tuple[str, ...] = ('A')) -> Outcome:
    ret: list = []
    try:
        for record in records:
            ret.append(dns.resolver.query(name, record).rrset)
        return Outcome(True, str(ret))
    except DNSException as e:
        return Outcome(False, f'DNS resolution for {name} failed: {e}')