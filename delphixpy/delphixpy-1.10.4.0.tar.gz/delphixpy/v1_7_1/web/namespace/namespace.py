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
Package "namespace"
"""
API_VERSION = "1.7.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_7_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Namespace object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    :rtype: :py:class:`v1_7_1.web.vo.Namespace`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Namespace'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List Namespace objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_7_1.web.vo.Namespace`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Namespace'], returns_list=True, raw_result=raw_result)

def update(engine, ref, namespace=None):
    """
    Update the specified Namespace object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    :param namespace: Payload object.
    :type namespace: :py:class:`v1_7_1.web.vo.Namespace`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s" % ref
    response = engine.post(url, namespace.to_dict(dirty=True) if namespace else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified Namespace object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def discard(engine, ref):
    """
    Discards any partial receive state for the given namespace.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s/discard" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def failover(engine, ref):
    """
    Initiates failover for the given namespace.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s/failover" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def translate(engine, ref, object=None):
    """
    Returns the local object corresponding to the remote reference.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.Namespace.Namespace` object
    :type ref: ``str``
    :param object: None
    :type object: ``TEXT_TYPE``
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/%s/translate" % ref
    query_params = {"object": object}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def lookup(engine, tag=None):
    """
    Lookup a namespace by tag.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param tag: The value of the namespace tag to search for.
    :type tag: ``TEXT_TYPE``
    :rtype: :py:class:`v1_7_1.web.vo.Namespace`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/namespace/lookup"
    query_params = {"tag": tag}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Namespace'], returns_list=False, raw_result=raw_result)

