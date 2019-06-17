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
Package "service.certificate"
"""
API_VERSION = "1.5.0"

from delphixpy.v1_5_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified X509Certificate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_0.web.objects.X509Certificate.X509Certificate
        ` object
    :type ref: ``str``
    :rtype: :py:class:`v1_5_0.web.vo.X509Certificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/certificate/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'X509Certificate'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List X509Certificate objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_5_0.web.vo.X509Certificate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/certificate"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'X509Certificate'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified X509Certificate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_0.web.objects.X509Certificate.X509Certificate
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/certificate/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def accept(engine, ref):
    """
    Make Delphix trust this certificate.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_0.web.objects.X509Certificate.X509Certificate
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/certificate/%s/accept" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def fetch(engine, certificate_fetch_parameters=None):
    """
    Fetch an X.509 certificate from the specified host and port.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :param certificate_fetch_parameters: Payload object.
    :type certificate_fetch_parameters:
        :py:class:`v1_5_0.web.vo.CertificateFetchParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/certificate/fetch"
    response = engine.post(url, certificate_fetch_parameters.to_dict(dirty=True) if certificate_fetch_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

