FIELDS_CORE = [
    'indicator', 'itype', 'tlp', 'provider', 'group', 'tlp', 'provider',
    'count', 'message', 'tags', 'confidence',
    'description', 'version', 'uuid', 'probability'
]

FIELDS_TIME = [
    'first_at', 'last_at', 'reported_at'
]

FIELDS_META = [
    'application', 'reference', 'reference_tlp', 'data'
]

FIELDS_GEO = [
    'cc', 'latitude', 'timezone', 'longitude', 'city', 'region'
]

FIELDS_IP = [
    'portlist', 'protocol', 'asn', 'asn_desc', 'dest', 'dest_portlist', 'mask',
    'rdata', 'rtype', 'peers'
]

FIELDS_FQDN = [
    'ns', 'mx', 'cname'
]

FIELDS = FIELDS_CORE + FIELDS_GEO + FIELDS_META + FIELDS_IP + FIELDS_TIME \
         + FIELDS_FQDN
