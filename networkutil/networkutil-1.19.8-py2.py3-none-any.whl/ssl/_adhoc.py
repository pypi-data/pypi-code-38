# encoding: utf-8

import os
from cryptography.x509.oid import NameOID
from networkutil.ssl import generate_ca, generate_config_ca, generate_certificates, generate_config_certificates

ROOT_DIR = u'/Users/oda02/Desktop/'

# Create a test CA
cacert, cakey, capaths = generate_ca(filepath=os.path.join(ROOT_DIR, u'cert_test'),
                                     filename=u'CA',
                                     subject_keys={
                                         NameOID.COMMON_NAME: u'Test Certificate Authority',
                                         NameOID.COUNTRY_NAME: u'GB',
                                         NameOID.STATE_OR_PROVINCE_NAME: u'England',
                                         NameOID.ORGANIZATION_NAME: u'Test'
                                     })

# Create a test server certificate using our CA
srv1cert, srv1key, srv1paths = generate_certificates(ca_cert=cacert,
                                                     ca_key=cakey,
                                                     filepath=os.path.join(ROOT_DIR, u'cert_test'),
                                                     filename=u'Server1')

# Create a test server certificate (will generate default CA)
srv2cert, srv2key, srv2paths = generate_certificates(filepath=os.path.join(ROOT_DIR, u'cert_test'),
                                                     filename=u'Server2')

# Create a test server certificate (will use generated default CA)
srv3cert, srv3key, srv3paths = generate_certificates(filepath=os.path.join(ROOT_DIR, u'cert_test'),
                                                     filename=u'Server3')

# Create a test config CA
ca2cert, ca2key, ca2paths = generate_config_ca(name=u'Config_CA',
                                               subject_keys={
                                                   NameOID.COMMON_NAME: u'Test Config Certificate Authority',
                                                   NameOID.COUNTRY_NAME: u'GB',
                                                   NameOID.STATE_OR_PROVINCE_NAME: u'England',
                                                   NameOID.ORGANIZATION_NAME: u'Test'
                                               })
print(ca2paths)

# Create a test config server certificate using our config CA
srv4cert, srv4key, srv4paths = generate_config_certificates(ca_cert=ca2cert,
                                                            ca_key=ca2key,
                                                            name=u'Server4')
print(srv4paths)
