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
Package "group"
"""
API_VERSION = "1.6.2"

from delphixpy.v1_6_2 import response_validator

def create(engine, group=None):
    """
    Create a new Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param group: Payload object.
    :type group: :py:class:`v1_6_2.web.vo.Group`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/group"
    response = engine.post(url, group.to_dict(dirty=True) if group else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Group.Group` object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_2.web.vo.Group`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/group/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Group'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List Group objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_6_2.web.vo.Group`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/group"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Group'], returns_list=True, raw_result=raw_result)

def update(engine, ref, group=None):
    """
    Update the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Group.Group` object
    :type ref: ``str``
    :param group: Payload object.
    :type group: :py:class:`v1_6_2.web.vo.Group`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/group/%s" % ref
    response = engine.post(url, group.to_dict(dirty=True) if group else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Group.Group` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/group/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

