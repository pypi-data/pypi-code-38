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
Package "service.tls.cacert"
"""
API_VERSION = "1.9.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_0 import response_validator

def create(engine, certificate_import_parameters):
    """
    Import a CA certificate in PEM format.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param certificate_import_parameters: Payload object.
    :type certificate_import_parameters:
        :py:class:`v1_9_0.web.vo.CertificateImportParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/cacert"
    response = engine.post(url, certificate_import_parameters.to_dict(dirty=True) if certificate_import_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified TlsCaCert object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.TlsCaCert.TlsCaCert` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_0.web.vo.TlsCaCert`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/cacert/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TlsCaCert'], returns_list=False, raw_result=raw_result)

def get_all(engine, alias=None):
    """
    List TlsCaCert objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param alias: List the CA with the given alias.
    :type alias: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_0.web.vo.TlsCaCert`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/cacert"
    query_params = {"alias": alias}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TlsCaCert'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified TlsCaCert object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.TlsCaCert.TlsCaCert` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/tls/cacert/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

