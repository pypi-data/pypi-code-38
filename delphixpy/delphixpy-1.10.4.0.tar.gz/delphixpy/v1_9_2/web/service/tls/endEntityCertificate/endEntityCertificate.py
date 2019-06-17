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
Package "service.tls.endEntityCertificate"
"""
API_VERSION = "1.9.2"

from delphixpy.v1_9_2 import response_validator

def get(engine, ref):
    """
    Retrieve the specified EndEntityCertificate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_2.web.objects.EndEntit
        yCertificate.EndEntityCertificate` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.EndEntityCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'EndEntityCertificate'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List EndEntityCertificate objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.EndEntityCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'EndEntityCertificate'], returns_list=True, raw_result=raw_result)

def to_pem(engine, ref):
    """
    Return this certificate in PEM format.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_2.web.objects.EndEntit
        yCertificate.EndEntityCertificate` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.PemCertificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate/%s/toPEM" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PemCertificate'], returns_list=False, raw_result=raw_result)

def request_key_pair_and_cert_chain_upload(engine, certificate_upload_parameters):
    """
    Request upload for a key pair and associated certificate chain within a
    keystore private key entry.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param certificate_upload_parameters: Payload object.
    :type certificate_upload_parameters:
        :py:class:`v1_9_2.web.vo.CertificateUploadParameters`
    :rtype: :py:class:`v1_9_2.web.vo.FileUploadResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate/requestKeyPairAndCertChainUpload"
    response = engine.post(url, certificate_upload_parameters.to_dict(dirty=True) if certificate_upload_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FileUploadResult'], returns_list=False, raw_result=raw_result)

def show_provided_certificate_chain(engine, end_entity_certificate_replace_parameters):
    """
    Display the provided certificate chain as Certificate objects prior to
    replace.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param end_entity_certificate_replace_parameters: Payload object.
    :type end_entity_certificate_replace_parameters:
        :py:class:`v1_9_2.web.vo.EndEntityCertificateReplaceParameters`
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.Certificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate/showProvidedCertificateChain"
    response = engine.post(url, end_entity_certificate_replace_parameters.to_dict(dirty=True) if end_entity_certificate_replace_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Certificate'], returns_list=True, raw_result=raw_result)

def replace(engine, end_entity_certificate_replace_parameters):
    """
    Replace the end-entity certificate and key pair for a service. This will
    delete the current end-entity certificate and key pair for that service.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param end_entity_certificate_replace_parameters: Payload object.
    :type end_entity_certificate_replace_parameters:
        :py:class:`v1_9_2.web.vo.EndEntityCertificateReplaceParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/endEntityCertificate/replace"
    response = engine.post(url, end_entity_certificate_replace_parameters.to_dict(dirty=True) if end_entity_certificate_replace_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

