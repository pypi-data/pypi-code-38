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
Package "timeflow.bookmark"
"""
API_VERSION = "1.4.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_4_1 import response_validator

def create(engine, timeflow_bookmark_create_parameters):
    """
    Create a new TimeflowBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param timeflow_bookmark_create_parameters: Payload object.
    :type timeflow_bookmark_create_parameters:
        :py:class:`v1_4_1.web.vo.TimeflowBookmarkCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/bookmark"
    response = engine.post(url, timeflow_bookmark_create_parameters.to_dict(dirty=True) if timeflow_bookmark_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified TimeflowBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_1.web.objects.TimeflowBookmark.TimeflowBookma
        rk` object
    :type ref: ``str``
    :rtype: :py:class:`v1_4_1.web.vo.TimeflowBookmark`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/bookmark/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TimeflowBookmark'], returns_list=False, raw_result=raw_result)

def get_all(engine, database=None):
    """
    Returns a list of all timeflow bookmarks.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param database: Filter results based on specified database.
    :type database: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_4_1.web.vo.TimeflowBookmark`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/bookmark"
    query_params = {"database": database}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TimeflowBookmark'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified TimeflowBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_1.web.objects.TimeflowBookmark.TimeflowBookma
        rk` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/bookmark/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

