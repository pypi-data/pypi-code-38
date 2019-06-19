#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Constants used for building and more'''

import os
import pkg_resources

from . import bootstrap

from .log import get_logger
logger = get_logger(__name__)


BASE_CONDARC = bootstrap._BASE_CONDARC
'''Default setup for conda builds'''


CONDA_BUILD_CONFIG = pkg_resources.resource_filename(__name__,
    os.path.join('data', 'conda_build_config.yaml'))
'''Configuration variants we like building'''


CONDA_RECIPE_APPEND = pkg_resources.resource_filename(__name__,
    os.path.join('data', 'recipe_append.yaml'))
'''Extra information to be appended to every recipe upon building'''


SERVER = bootstrap._SERVER
'''This is the default server use use to store data and build artifacts'''


WEBDAV_PATHS = {
    True: {  #stable?
      False: {  #visible?
        'root': '/private-upload',
        'conda': '/conda',
        'docs': '/docs',
        },
      True: {  #visible?
        'root': '/public-upload',
        'conda': '/conda',
        'docs': '/docs',
        },
      },
    False: {  #stable?
      False: {  #visible?
        'root': '/private-upload',
        'conda': '/conda/label/beta',
        'docs': '/docs',
        },
      True: {  #visible?
        'root': '/public-upload',
        'conda': '/conda/label/beta',
        'docs': '/docs',
        },
      },
    }
'''Default locations of our webdav upload paths'''


IDIAP_ROOT_CA = b'''
Idiap Root CA 2016 - for internal use
=====================================
-----BEGIN CERTIFICATE-----
MIIG7zCCBNegAwIBAgIJAP2rGWTQbd8bMA0GCSqGSIb3DQEBCwUAMIGYMQswCQYD
VQQGEwJDSDELMAkGA1UECBMCVlMxETAPBgNVBAcTCE1hcnRpZ255MSEwHwYDVQQK
ExhJZGlhcCBSZXNlYXJjaCBJbnN0aXR1dGUxDDAKBgNVBAsTA1BLSTEbMBkGA1UE
AxMSSWRpYXAgUm9vdCBDQSAyMDE2MRswGQYJKoZIhvcNAQkBFgxwa2lAaWRpYXAu
Y2gwHhcNMTYwMTI3MTU1MzAxWhcNNDYwMTMwMTU1MzAxWjCBmDELMAkGA1UEBhMC
Q0gxCzAJBgNVBAgTAlZTMREwDwYDVQQHEwhNYXJ0aWdueTEhMB8GA1UEChMYSWRp
YXAgUmVzZWFyY2ggSW5zdGl0dXRlMQwwCgYDVQQLEwNQS0kxGzAZBgNVBAMTEklk
aWFwIFJvb3QgQ0EgMjAxNjEbMBkGCSqGSIb3DQEJARYMcGtpQGlkaWFwLmNoMIIC
IjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAydOC2EzaT+6bPcUFin8BawnS
OxfFzDh18536O+PDAuyycOY1cIefpC3PvLk7XM83hIlUY1Q02/yt4h0iXkAUs/RI
VE6PyIh7pTxabyjIqIZ7xlVkK9cfGhlUm+ofd/Limo6WBbaH64jf/Jm6KdRtu2n4
q1brII31nCIwBvf8uVBuo5Y4NMS8bWcaBxj93S+C16sV4E2gz28FYCuSpAnU5DeP
0PwNsuBkVFgHUwc2VxfUyCmQEs+qlWb+6W7ULWvtD3K28414tygVxOSXkl9ZVJGX
KBwevSs2TTlH25Q3TAY4mXweJ2RweFwlnbzpA0YYrQUDy5MTVslD5Sl0c5vO6HZH
DgT4jyWbL87akczTaz028zmUQvC7RoGPKXqhHlaO3uDu1fBC7aoA/L1akqfYGnoO
x4xU7gouGi9Hck23DKLsW1HP2PzaZ/ME++IZPr2I049aKBadz3vCbAh2bHgosdyp
a69e6SMiq9guloQXCqFTSk+P6CwU9wWil3SdGojRafyocKyoBL67hKIFkJQOdjhq
edi3WfoSU+1kDwEyXU2fCsTjgg0q1BsJFctSUFs7QoVMAoyXXauDCf1YuojlXuXM
FrQmYLBzSFA7OFFynWbnn1mHMzsHEiAzAr0+7ecIreBwN1gJqx1+7hxkSQzDm2oH
jTPGGwJfbJnej4RduBkCAwEAAaOCATgwggE0MB0GA1UdDgQWBBR6H/NwUn5K3lVV
IVgpNR41/bxdtTCBzQYDVR0jBIHFMIHCgBR6H/NwUn5K3lVVIVgpNR41/bxdtaGB
nqSBmzCBmDELMAkGA1UEBhMCQ0gxCzAJBgNVBAgTAlZTMREwDwYDVQQHEwhNYXJ0
aWdueTEhMB8GA1UEChMYSWRpYXAgUmVzZWFyY2ggSW5zdGl0dXRlMQwwCgYDVQQL
EwNQS0kxGzAZBgNVBAMTEklkaWFwIFJvb3QgQ0EgMjAxNjEbMBkGCSqGSIb3DQEJ
ARYMcGtpQGlkaWFwLmNoggkA/asZZNBt3xswDwYDVR0TAQH/BAUwAwEB/zAJBgNV
HRIEAjAAMBcGA1UdEQQQMA6BDHBraUBpZGlhcC5jaDAOBgNVHQ8BAf8EBAMCAQYw
DQYJKoZIhvcNAQELBQADggIBAJmXqtgmHj1XXUptloVVsCwCYBU8ykf1dZz2Kxrx
oe0dnDO24CA6w3D3TCt8rncT2lFNRTbc/4HO32xl1IDNiWh5P/ZPNpptwd6XjGR1
EgDjpIBKNotf+6WWvcKrs23mj9UwNPHDwNA251LAMVXaoMN2iOflzj2BbIcasY3P
IcYeshd3CChy8QqltE1M8mjwb7brkIzwcPI5QEhW9NmfYUfbijILZrE2kgo6oOFH
mRZIDoexrd19hHLWFLxoe0IPj6R1GFajBHi8Ttt3tPQOPjwjGQvNfVPRhWh3/kAF
UrWZposffDDIc+8TNlrhkx+YKucYH56Tyuh6Y1Po7FCkvp2/G/JxKWeAEqKpI2+g
8Hsl0XjSOJ9bOhs+R0wMzeBzntDk8k+6ar3KYGJD24gQ+QDy4klE/rsdC/Gp6dEi
tSIPvH4VIvN0lLICWKj3IFhBv6IOJ12Xq5IMquDq5BZ6O2+yqoROIYQyhwHq+xhn
rqqR6TsFMl/F5R0j14oGzg+VdB8VsIrg7rTJx+oDD9r+Pa2hua4DRmQsw+CJgnHz
NqU3Xei/78W+eLh9HZvVqXpi4s/fF6z+lXKDHpqVRh5kNAKJbYQUfcV2H7FEtCux
NIDS6J1GnHJKCmYPuwFSrQ5VXM/1p7w+A9MkJktsxw2kxsRUvJn7Ka+bp7M6wERU
JHsX
-----END CERTIFICATE-----
'''


CACERT_URL = 'https://curl.haxx.se/ca/cacert.pem'
'''Location of the most up-to-date CA certificate bundle'''


CACERT = pkg_resources.resource_filename(__name__,
    os.path.join('data', 'cacert.pem'))
'''We keep a copy of the CA certificates we trust here

   To update this file use: ``curl --remote-name --time-cond cacert.pem https://curl.haxx.se/ca/cacert.pem``

   More information here: https://curl.haxx.se/docs/caextract.html
'''


MATPLOTLIB_RCDIR = pkg_resources.resource_filename(__name__, 'data')
'''Base directory where the file matplotlibrc lives

It is required for certain builds that use matplotlib functionality.
'''
