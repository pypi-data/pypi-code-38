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
Package "service.saml.serviceprovider"
"""
API_VERSION = "1.9.1"

from delphixpy.v1_9_1 import response_validator

def create(engine, saml_service_provider=None):
    """
    Create a new SamlServiceProvider object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param saml_service_provider: Payload object.
    :type saml_service_provider: :py:class:`v1_9_1.web.vo.SamlServiceProvider`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider"
    response = engine.post(url, saml_service_provider.to_dict(dirty=True) if saml_service_provider else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SamlServiceProvider object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.SamlServ
        iceProvider.SamlServiceProvider` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_1.web.vo.SamlServiceProvider`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SamlServiceProvider'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SamlServiceProvider objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_1.web.vo.SamlServiceProvider`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SamlServiceProvider'], returns_list=True, raw_result=raw_result)

def update(engine, ref, saml_service_provider=None):
    """
    Update the specified SamlServiceProvider object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.SamlServ
        iceProvider.SamlServiceProvider` object
    :type ref: ``str``
    :param saml_service_provider: Payload object.
    :type saml_service_provider: :py:class:`v1_9_1.web.vo.SamlServiceProvider`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/%s" % ref
    response = engine.post(url, saml_service_provider.to_dict(dirty=True) if saml_service_provider else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SamlServiceProvider object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.SamlServ
        iceProvider.SamlServiceProvider` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def saml_authn_request(engine, saml_auth_parameters=None):
    """
    Returns a SAML authentication request.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param saml_auth_parameters: Payload object.
    :type saml_auth_parameters: :py:class:`v1_9_1.web.vo.SamlAuthParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/samlAuthnRequest"
    response = engine.post(url, saml_auth_parameters.to_dict(dirty=True) if saml_auth_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def show_metadata(engine):
    """
    Returns the SAML metadata of the Delphix Engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/showMetadata"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get_destination(engine):
    """
    Returns the destination the SAML request will be POSTed to.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/saml/serviceprovider/getDestination"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

