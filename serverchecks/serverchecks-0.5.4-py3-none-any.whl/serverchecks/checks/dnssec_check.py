from typing import List

import dns.resolver
from dns.exception import DNSException
from dns.message import Message
from dns.name import Name

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class DnssecCheck(AbstractCheck):
    name = 'DNSSEC'

    def __init__(self, **kwargs) -> None:
        self.host: str = kwargs.get('host')

        if self.host is None:
            raise ValueError(f'{self.name} required `host` parameter is missing')

    async def check(self) -> Outcome:

        # convert string name to dnspython Name object
        name: Name = dns.name.from_text(self.host)

        try:
            # First obtain the list of nameservers for the tested domain
            answers: List[dns.resolver.Answer] = dns.resolver.query(name, rdtype=dns.rdatatype.NS)

            if len(answers.rrset) == 0:
                return Outcome(False, f'DNSSEC test for {name} failed due to empty response: {answers}')

            for answer in answers.rrset:
                answer = answer.to_text()

            response = dns.resolver.query(answer, rdtype=dns.rdatatype.A)

        except (AttributeError, DNSException) as e:
            return Outcome(False, f'DNSSEC: Unable to obtain the list of nameservers for {name}: {e}')

        for nameserver_ip in response.rrset:

            nameserver_ip = nameserver_ip.to_text()

            try:

                # obtain DNSKEY from the nameserver
                req_dnskey = dns.message.make_query(name, rdtype=dns.rdatatype.DNSKEY, want_dnssec=True)
                response: Message = dns.query.udp(req_dnskey, nameserver_ip, timeout=5.0)
            except (AttributeError, DNSException) as e:
                return Outcome(False, f'DNSSEC: unable to obtain DNSKEY for {name}: {e}')
            else:

                if response.rcode() != 0:
                    return Outcome(False,
                                   f'DNSSEC: DNSKEY response {name} from {nameserver_ip} failed: {response.rcode()}')

                if len(response.answer) < 2:
                    return Outcome(False, f'DNSSEC test for {name} failed due to empty response: {response.answer}')

                try:
                    # now actually attempt DNSSEC validation on the received record
                    dns.dnssec.validate(response.answer[0], response.answer[1], {name: response.answer[0]})

                except (AttributeError, DNSException) as e:
                    return Outcome(False, f'DNSSEC validation for {name} at {nameserver_ip} failed: {response}: {e}')

                else:
                    return Outcome(True, f'DNSSEC fully validated for {name}')

    def __str__(self):
        return f'<{self.name} "{self.host}">'


check_class = DnssecCheck
