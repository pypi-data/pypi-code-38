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
Package "service.tls.csr"
"""
API_VERSION = "1.10.2"

from delphixpy.v1_10_2 import response_validator

def create(engine, certificate_signing_request_create_parameters):
    """
    Create a new CertificateSigningRequest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param certificate_signing_request_create_parameters: Payload object.
    :type certificate_signing_request_create_parameters:
        :py:class:`v1_10_2.web.vo.CertificateSigningRequestCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/csr"
    response = engine.post(url, certificate_signing_request_create_parameters.to_dict(dirty=True) if certificate_signing_request_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified CertificateSigningRequest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_10_2.web.objects.Certifi
        cateSigningRequest.CertificateSigningRequest` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_2.web.vo.CertificateSigningRequest`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/csr/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CertificateSigningRequest'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List CertificateSigningRequest objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_10_2.web.vo.CertificateSigningRequest`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/csr"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CertificateSigningRequest'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified CertificateSigningRequest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_10_2.web.objects.Certifi
        cateSigningRequest.CertificateSigningRequest` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/csr/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def validate_dname(engine, x500_distinguished_name):
    """
    Validate distinguished name.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param x500_distinguished_name: Payload object.
    :type x500_distinguished_name:
        :py:class:`v1_10_2.web.vo.X500DistinguishedName`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/csr/validateDname"
    response = engine.post(url, x500_distinguished_name.to_dict(dirty=True) if x500_distinguished_name else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

