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
Package "alert.profile"
"""
API_VERSION = "1.9.3"

from delphixpy.v1_9_3 import response_validator

def create(engine, alert_profile=None):
    """
    Create a new AlertProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param alert_profile: Payload object.
    :type alert_profile: :py:class:`v1_9_3.web.vo.AlertProfile`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/alert/profile"
    response = engine.post(url, alert_profile.to_dict(dirty=True) if alert_profile else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified AlertProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_3.web.objects.AlertProfile.AlertProfile`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_3.web.vo.AlertProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/alert/profile/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AlertProfile'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List AlertProfile objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_3.web.vo.AlertProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/alert/profile"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AlertProfile'], returns_list=True, raw_result=raw_result)

def update(engine, ref, alert_profile=None):
    """
    Update the specified AlertProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_3.web.objects.AlertProfile.AlertProfile`
        object
    :type ref: ``str``
    :param alert_profile: Payload object.
    :type alert_profile: :py:class:`v1_9_3.web.vo.AlertProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/alert/profile/%s" % ref
    response = engine.post(url, alert_profile.to_dict(dirty=True) if alert_profile else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified AlertProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_3.web.objects.AlertProfile.AlertProfile`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/alert/profile/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

