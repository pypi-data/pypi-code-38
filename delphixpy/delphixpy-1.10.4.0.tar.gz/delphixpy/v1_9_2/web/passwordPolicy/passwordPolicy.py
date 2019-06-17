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
Package "passwordPolicy"
"""
API_VERSION = "1.9.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_2 import response_validator

def create(engine, password_policy=None):
    """
    Create a new PasswordPolicy object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param password_policy: Payload object.
    :type password_policy: :py:class:`v1_9_2.web.vo.PasswordPolicy`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy"
    response = engine.post(url, password_policy.to_dict(dirty=True) if password_policy else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified PasswordPolicy object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.PasswordPolicy.PasswordPolicy`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.PasswordPolicy`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PasswordPolicy'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists password policies in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.PasswordPolicy`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PasswordPolicy'], returns_list=True, raw_result=raw_result)

def update(engine, ref, password_policy=None):
    """
    Update the specified PasswordPolicy object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.PasswordPolicy.PasswordPolicy`
        object
    :type ref: ``str``
    :param password_policy: Payload object.
    :type password_policy: :py:class:`v1_9_2.web.vo.PasswordPolicy`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/%s" % ref
    response = engine.post(url, password_policy.to_dict(dirty=True) if password_policy else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified PasswordPolicy object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.PasswordPolicy.PasswordPolicy`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def current_requirements(engine):
    """
    Returns the pasword policy of the currently logged in user. This is empty
    if the Delphix Engine has not been configured yet.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/currentRequirements"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def current_password_policy(engine, user_type=None):
    """
    Returns the currently active password policy for users of the selected user
    type.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param user_type: Type of user. *(permitted values: SYSTEM, DOMAIN)*
    :type user_type: ``TEXT_TYPE``
    :rtype: :py:class:`v1_9_2.web.vo.PasswordPolicy`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/currentPasswordPolicy"
    query_params = {"userType": user_type}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PasswordPolicy'], returns_list=False, raw_result=raw_result)

def change_current_password_policy(engine, change_current_password_policy_parameters):
    """
    Changes the currently active password policy for all users of the selected
    user type.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param change_current_password_policy_parameters: Payload object.
    :type change_current_password_policy_parameters:
        :py:class:`v1_9_2.web.vo.ChangeCurrentPasswordPolicyParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/passwordPolicy/changeCurrentPasswordPolicy"
    response = engine.post(url, change_current_password_policy_parameters.to_dict(dirty=True) if change_current_password_policy_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

