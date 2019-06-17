#
# Copyright 2019 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Package "service.tls.caCertificate"
"""
API_VERSION = "1.10.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_2 import response_validator

def create(engine, pem_certificate):
    """
    Import a CA certificate in PEM format.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param pem_certificate: Payload object.
    :type pem_certificate: :py:class:`v1_10_2.web.vo.PemCertificate`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate"
    response = engine.post(url, pem_certificate.to_dict(dirty=True) if pem_certificate else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified CaCertificate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_2.web.objects.CaCertificate.CaCertificate`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_2.web.vo.CaCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CaCertificate'], returns_list=False, raw_result=raw_result)

def get_all(engine, delphix_ca=None):
    """
    List CaCertificate objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param delphix_ca: List the Delphix CA only. If false, display everything
        except the Delphix CA.
    :type delphix_ca: ``bool``
    :rtype: ``list`` of :py:class:`v1_10_2.web.vo.CaCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate"
    query_params = {"delphixCa": delphix_ca}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CaCertificate'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified CaCertificate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_2.web.objects.CaCertificate.CaCertificate`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def to_pem(engine, ref):
    """
    Return this certificate in PEM format.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_2.web.objects.CaCertificate.CaCertificate`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_2.web.vo.PemCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/%s/toPEM" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PemCertificate'], returns_list=False, raw_result=raw_result)

def accept(engine, ref):
    """
    Make Delphix trust this certificate. This is only needed for certificates
    added through the fetch API.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_2.web.objects.CaCertificate.CaCertificate`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/%s/accept" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def show_provided_certificate(engine, pem_certificate):
    """
    Display the provided certificate as a CaCertificate object prior to import.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param pem_certificate: Payload object.
    :type pem_certificate: :py:class:`v1_10_2.web.vo.PemCertificate`
    :rtype: :py:class:`v1_10_2.web.vo.CaCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/showProvidedCertificate"
    response = engine.post(url, pem_certificate.to_dict(dirty=True) if pem_certificate else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CaCertificate'], returns_list=False, raw_result=raw_result)

def fetch(engine, certificate_fetch_parameters=None):
    """
    Fetch an X.509 certificate from the specified host and port.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param certificate_fetch_parameters: Payload object.
    :type certificate_fetch_parameters:
        :py:class:`v1_10_2.web.vo.CertificateFetchParameters`
    :rtype: :py:class:`v1_10_2.web.vo.CaCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/caCertificate/fetch"
    response = engine.post(url, certificate_fetch_parameters.to_dict(dirty=True) if certificate_fetch_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CaCertificate'], returns_list=False, raw_result=raw_result)

