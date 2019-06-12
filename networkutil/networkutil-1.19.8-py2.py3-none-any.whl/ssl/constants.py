# encoding: utf-8

import attr
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import SubjectAlternativeName, DNSName
from networkutil.addressing import get_my_addresses

DEFAULT_BITS = 2048
DEFAULT_DIGEST = hashes.SHA256()
DEFAULT_VALIDITY = 3650  # 10 Years
DEFAULT_CA_NAME = u'DEFAULT_CA'
DEFAULT_CA_SUBJECT_KEYS = {
    NameOID.COMMON_NAME: u'Test Default Certificate Authority',
    NameOID.COUNTRY_NAME: u'GB',
    NameOID.STATE_OR_PROVINCE_NAME: u'England',
    NameOID.ORGANIZATION_NAME: u'Test'
}
DEFAULT_CERTIFICATE_SUBJECT_KEYS = {
    NameOID.COMMON_NAME: u'localhost',
    NameOID.COUNTRY_NAME: u'GB',
    NameOID.STATE_OR_PROVINCE_NAME: u'England',
    NameOID.ORGANIZATION_NAME: u'Test'
}

DEFAULT_DNS_NAMES = []

for address in get_my_addresses():
    try:
        DEFAULT_DNS_NAMES.append(DNSName(address))

    except TypeError:
        pass

DEFAULT_EXTENSIONS = [
    SubjectAlternativeName(DEFAULT_DNS_NAMES)
]
DEFAULT_PASSPHRASE = b'secret_password'

SSL_CONFIG = u'ssl_certificates'
SSL_DATA_DIR = u'Certificates'


@attr.s(frozen=True)
class _SSLConstant(object):
    name = attr.ib(default=u'name', init=False)
    private_key = attr.ib(default=u'key', init=False)
    public_key = attr.ib(default=u'pub', init=False)
    csr = attr.ib(default=u'csr', init=False)
    pem = attr.ib(default=u'crt', init=False)
    der = attr.ib(default=u'cer', init=False)


SSLConstant = _SSLConstant()
