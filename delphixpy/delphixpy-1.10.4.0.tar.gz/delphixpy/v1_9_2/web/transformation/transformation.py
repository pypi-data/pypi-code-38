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
Package "transformation"
"""
API_VERSION = "1.9.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_2 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Transformation object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.Transformation.Transformation`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.Transformation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/transformation/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Transformation'], returns_list=False, raw_result=raw_result)

def get_all(engine, parent_container=None, container=None):
    """
    Returns a list of all transformations on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param parent_container: List the transformations that have been created
        against the provided container.
    :type parent_container: ``TEXT_TYPE``
    :param container: Return the transformation responsible for the given
        container reference.
    :type container: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.Transformation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/transformation"
    query_params = {"parentContainer": parent_container, "container": container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Transformation'], returns_list=True, raw_result=raw_result)

def update(engine, ref, transformation=None):
    """
    Update the specified Transformation object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.Transformation.Transformation`
        object
    :type ref: ``str``
    :param transformation: Payload object.
    :type transformation: :py:class:`v1_9_2.web.vo.Transformation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/transformation/%s" % ref
    response = engine.post(url, transformation.to_dict(dirty=True) if transformation else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def apply(engine, ref, timeflow_point_parameters):
    """
    Apply a transformation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.Transformation.Transformation`
        object
    :type ref: ``str``
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_9_2.web.vo.TimeflowPointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/transformation/%s/apply" % ref
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

