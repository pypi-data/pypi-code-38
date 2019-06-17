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
Package "dvc.preferences"
"""
API_VERSION = "1.3.1"

from delphixpy.v1_3_1 import response_validator

def get(engine):
    """
    Retrieve the specified DVCUserPreferences object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_3_1.web.vo.DVCUserPreferences`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/preferences"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCUserPreferences'], returns_list=False, raw_result=raw_result)

def set(engine, dvc_user_preferences=None):
    """
    Update the specified DVCUserPreferences object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param dvc_user_preferences: Payload object.
    :type dvc_user_preferences: :py:class:`v1_3_1.web.vo.DVCUserPreferences`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/preferences"
    response = engine.post(url, dvc_user_preferences.to_dict(dirty=True) if dvc_user_preferences else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def reset(engine):
    """
    Reset the DVC user's preferences to the default values.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/preferences/reset"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def get_default(engine):
    """
    Returns the default DVC user preferences.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_3_1.web.vo.DVCUserPreferences`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/preferences/getDefault"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCUserPreferences'], returns_list=False, raw_result=raw_result)

def update_default(engine, dvc_user_preferences):
    """
    Updates the default DVC user preferences.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param dvc_user_preferences: Payload object.
    :type dvc_user_preferences: :py:class:`v1_3_1.web.vo.DVCUserPreferences`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/preferences/updateDefault"
    response = engine.post(url, dvc_user_preferences.to_dict(dirty=True) if dvc_user_preferences else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

