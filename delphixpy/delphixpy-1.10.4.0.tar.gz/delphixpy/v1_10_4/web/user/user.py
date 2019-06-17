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
Package "user"
"""
API_VERSION = "1.10.4"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_4 import response_validator

def create(engine, user=None):
    """
    Create a new User object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param user: Payload object.
    :type user: :py:class:`v1_10_4.web.vo.User`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user"
    response = engine.post(url, user.to_dict(dirty=True) if user else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified User object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_4.web.vo.User`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'User'], returns_list=False, raw_result=raw_result)

def get_all(engine, domain_user_type=None, type=None):
    """
    Lists users in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param domain_user_type: DOMAIN user type: DOMAIN_ADMIN, STANDARD_USER, or
        SELFSERVICE_ONLY. *(permitted values: DOMAIN_ADMIN, STANDARD_USER,
        SELFSERVICE_ONLY)*
    :type domain_user_type: ``TEXT_TYPE``
    :param type: User type SYSTEM or DOMAIN. *(permitted values: SYSTEM,
        DOMAIN)*
    :type type: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_4.web.vo.User`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user"
    query_params = {"domainUserType": domain_user_type, "type": type}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'User'], returns_list=True, raw_result=raw_result)

def update(engine, ref, user=None):
    """
    Update the specified User object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    :param user: Payload object.
    :type user: :py:class:`v1_10_4.web.vo.User`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s" % ref
    response = engine.post(url, user.to_dict(dirty=True) if user else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified User object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable(engine, ref):
    """
    Enables the specified user.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s/enable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def update_credential(engine, ref, credential_update_parameters=None):
    """
    Updates the user's login credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    :param credential_update_parameters: Payload object.
    :type credential_update_parameters:
        :py:class:`v1_10_4.web.vo.CredentialUpdateParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s/updateCredential" % ref
    response = engine.post(url, credential_update_parameters.to_dict(dirty=True) if credential_update_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable(engine, ref):
    """
    Disables the specified user.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.User.User` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/%s/disable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def current(engine):
    """
    Returns the currently logged in user. This may be null if the Delphix
    Engine has not been configured yet.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_10_4.web.vo.User`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/current"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'User', None], returns_list=False, raw_result=raw_result)

def session_users(engine):
    """
    Returns the users associated to the currently logged in session. This
    returns an empty list if the session is not a logged in SSO session.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_10_4.web.vo.User`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/sessionUsers"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'User'], returns_list=True, raw_result=raw_result)

def current_auth_info(engine):
    """
    Returns summary authorization information for the currently logged in user.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_10_4.web.vo.UserAuthInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/currentAuthInfo"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'UserAuthInfo'], returns_list=False, raw_result=raw_result)

def switch_session_user(engine, switch_session_user_parameters=None):
    """
    Change the user associated with session. This operation is only applicable
    to SSO sessions.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param switch_session_user_parameters: Payload object.
    :type switch_session_user_parameters:
        :py:class:`v1_10_4.web.vo.SwitchSessionUserParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/user/switchSessionUser"
    response = engine.post(url, switch_session_user_parameters.to_dict(dirty=True) if switch_session_user_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

