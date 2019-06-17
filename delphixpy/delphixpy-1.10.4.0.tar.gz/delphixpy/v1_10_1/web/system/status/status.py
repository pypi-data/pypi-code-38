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
Package "system.status"
"""
API_VERSION = "1.10.1"

from delphixpy.v1_10_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified SystemStatus object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.SystemStatus.SystemStatus`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_1.web.vo.SystemStatus`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/status/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SystemStatus'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SystemStatus objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_10_1.web.vo.SystemStatus`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/status"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SystemStatus'], returns_list=True, raw_result=raw_result)

def clear(engine, ref):
    """
    Hides this system status message. It will no longer be displayed.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.SystemStatus.SystemStatus`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/status/%s/clear" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

