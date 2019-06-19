import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

dns_lookup = u'{base}{filename}'.format(base=base_dir, filename=u'dns_lookup.json')
dns_forwarders = u'{base}{filename}'.format(base=base_dir, filename=u'dns_forwarders.json')
