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
Package "registration"
"""
API_VERSION = "1.8.0"

from delphixpy.v1_8_0 import response_validator

def get(engine):
    """
    Retrieve the specified RegistrationInfo object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_8_0.web.vo.RegistrationInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/registration"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'RegistrationInfo'], returns_list=False, raw_result=raw_result)

def query_status(engine, registration_parameters):
    """
    Attempts to contact the registration portal to get the registration status
    of the Delphix Engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param registration_parameters: Payload object.
    :type registration_parameters:
        :py:class:`v1_8_0.web.vo.RegistrationParameters`
    :rtype: :py:class:`v1_8_0.web.vo.RegistrationParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/registration/queryStatus"
    response = engine.post(url, registration_parameters.to_dict(dirty=True) if registration_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'RegistrationParameters'], returns_list=False, raw_result=raw_result)

def register(engine, registration_parameters):
    """
    Attempts to register the Delphix Engine by contacting the registration
    portal.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param registration_parameters: Payload object.
    :type registration_parameters:
        :py:class:`v1_8_0.web.vo.RegistrationParameters`
    :rtype: :py:class:`v1_8_0.web.vo.RegistrationParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/registration/register"
    response = engine.post(url, registration_parameters.to_dict(dirty=True) if registration_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'RegistrationParameters'], returns_list=False, raw_result=raw_result)

