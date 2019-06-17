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
Package "dvc.branch"
"""
API_VERSION = "1.3.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_3_1 import response_validator

def create(engine, dvc_branch=None):
    """
    Create a new DVCBranch object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param dvc_branch: Payload object.
    :type dvc_branch: :py:class:`v1_3_1.web.vo.DVCBranch`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/branch"
    response = engine.post(url, dvc_branch.to_dict(dirty=True) if dvc_branch else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified DVCBranch object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_1.web.objects.DVCBranch.DVCBranch` object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_1.web.vo.DVCBranch`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/branch/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCBranch'], returns_list=False, raw_result=raw_result)

def get_all(engine, application=None, parent_bookmark=None):
    """
    Lists the DVC branches in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param application: List branches belonging to the given application.
    :type application: ``TEXT_TYPE``
    :param parent_bookmark: List branches starting from the given parent
        bookmark.
    :type parent_bookmark: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_3_1.web.vo.DVCBranch`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/branch"
    query_params = {"application": application, "parentBookmark": parent_bookmark}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCBranch'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified DVCBranch object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_1.web.objects.DVCBranch.DVCBranch` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/branch/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def switch_to_branch(engine, ref):
    """
    Makes this branch the current branch for its application.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_1.web.objects.DVCBranch.DVCBranch` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/branch/%s/switchToBranch" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

