import dns.resolver
import re


class DNSResolver:
    """This class simplifies the process of performing a recursive DNS query against a nameserver."""

    def __init__(self, nameservers=('8.8.8.8', '8.8.4.4')):
        """
        Initialize class.
        :param nameservers: list of nameservers to query
        """
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.nameservers = nameservers

    def change_nameservers(self, nameservers):
        """
        Change the nameservers to query.
        :param nameservers: list of nameservers to query
        :return: None
        """
        self.dns_resolver.nameservers = nameservers

    def lookup(self, queryobj, qtype='A'):
        """
        Perform a DNS query (by default we search for an 'A' record.)
        :param queryobj: domain name to search for
        :param qtype: type of record to search for; default is A
        :return: DNS response or False if no results
        """
        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', queryobj.strip()):
            queryobj = '.'.join(reversed(queryobj.split('.'))) + ".in-addr.arpa"
            qtype = 'PTR'
        try:
            answer = self.dns_resolver.query(queryobj, qtype)
            return answer
        except dns.exception.DNSException:
            return False
