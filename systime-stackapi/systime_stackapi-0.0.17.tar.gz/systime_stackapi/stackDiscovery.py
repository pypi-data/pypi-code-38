import time
import dns.resolver


class StackDiscovery(object):
    def __init__(self, **kwargs):
        self.domain_to_discover = kwargs.get('domain', 'systime.dk')
        self._stacks = None
        self.ttlExpiry = 0

    @property
    def stacks(self):
        if self.ttlExpiry < time.time():
            stacks, ttl = self.discover_stacks()
            self.ttlExpiry = time.time() + ttl
            self._stacks = stacks
        return self._stacks

    def stack_list(self):
        return self.stacks.keys()

    def get_stack_endpoint(self, hostname):
        if self.stacks is not None and hostname in self.stacks:
            return self.stacks[hostname]

        raise Exception('Unable to locate stack.')

    def discover_stacks(self):
        dns_prefix = '%s.%s' % ('_stackservice_._tcp', self.domain_to_discover)
        answers = dns.resolver.query(dns_prefix, 'SRV')
        stacks = {}
        for rdata in answers:
            if rdata.port == 443:
                hostname = rdata.target.to_text().rstrip('.')
                stacks[hostname] = 'https://%s' % hostname
        return stacks, answers.ttl
