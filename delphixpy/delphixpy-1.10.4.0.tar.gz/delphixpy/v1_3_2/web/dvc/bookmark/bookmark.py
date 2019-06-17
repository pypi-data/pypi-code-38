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
Package "dvc.bookmark"
"""
API_VERSION = "1.3.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_3_2 import response_validator

def create(engine, dvc_bookmark_create_parameters):
    """
    Create a new DVCBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param dvc_bookmark_create_parameters: Payload object.
    :type dvc_bookmark_create_parameters:
        :py:class:`v1_3_2.web.vo.DVCBookmarkCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark"
    response = engine.post(url, dvc_bookmark_create_parameters.to_dict(dirty=True) if dvc_bookmark_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified DVCBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_2.web.vo.DVCBookmark`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCBookmark'], returns_list=False, raw_result=raw_result)

def get_all(engine, container=None, template=None):
    """
    Lists the DVC application's bookmarks in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param container: List all bookmarks accessible to the specified
        application container. This option is mutually exclusive with all other
        options.
    :type container: ``TEXT_TYPE``
    :param template: List all bookmarks created in the specified application
        template. This option is mutually exclusive with all other options.
    :type template: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_3_2.web.vo.DVCBookmark`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark"
    query_params = {"container": container, "template": template}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCBookmark'], returns_list=True, raw_result=raw_result)

def update(engine, ref, dvc_bookmark=None):
    """
    Update the specified DVCBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    :param dvc_bookmark: Payload object.
    :type dvc_bookmark: :py:class:`v1_3_2.web.vo.DVCBookmark`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s" % ref
    response = engine.post(url, dvc_bookmark.to_dict(dirty=True) if dvc_bookmark else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified DVCBookmark object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def get_create_bookmark_operation(engine, ref):
    """
    Returns the CREATE_BOOKMARK operation associated with the bookmark.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_2.web.vo.DVCOperation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s/getCreateBookmarkOperation" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCOperation'], returns_list=False, raw_result=raw_result)

def share(engine, ref):
    """
    Shares the bookmark.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s/share" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def unshare(engine, ref):
    """
    Unshares the bookmark.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_2.web.objects.DVCBookmark.DVCBookmark` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/bookmark/%s/unshare" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

