

class LookupMixin(object):
    def csirtg(self):
        try:
            from csirtgsdk.search import Search
        except ImportError:
            print('')
            print('The csirtg function requires the csirtgsdk')
            print('$ pip install csirtgsdk')
            print('$ export CSIRTG_TOKEN=1234...')
            print('')
            raise SystemExit

        return Search().search(self.indicator, limit=5)

    def cif(self):
        try:
            from cifsdk.client.http import HTTP as Client
        except ImportError:
            print('')
            print('The cif function requires the cifsdk>=4.0')
            print('$ pip install https://github.com/csirtgadgets/'
                  'verbose-robot-sdk-py/archive/master.zip')
            print('$ export CIF_TOKEN=1234...')
            print('')
            raise SystemExit

        return Client().search({'q': self.indicator, 'limit': 25})

    def farsight(self):
        if self.itype != 'ipv4':
            raise TypeError('%s is not supported' % self.itype)

        try:
            from csirtg_dnsdb.client import Client
        except ImportError:
            print('')
            print('The csirtg function requires the csirtg_dnsdb client')
            print('https://github.com/csirtgadgets/dnsdb-py')
            print('$ pip install csirtg_dnsdb')
            print('$ export FARSIGHT_TOKEN=1234...')
            print('')
            raise SystemExit

        return Client().search(self.indicator)

    def spamhaus(self):
        from csirtg_indicator.utils.spamhaus import ip, fqdn
        if self.is_ip():
            return ip.process(self, resolve_geo=self.resolve_geo)

        elif self.is_fqdn():
            return fqdn.process(self, resolve_geo=self.resolve_geo)

        else:
            return None
