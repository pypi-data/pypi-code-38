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
Package "replication.serializationpoint"
"""
API_VERSION = "1.5.3"

from delphixpy.v1_5_3 import response_validator

def get(engine, ref):
    """
    Retrieve the specified SerializationPoint object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_5_3.web.objects.Serializ
        ationPoint.SerializationPoint` object
    :type ref: ``str``
    :rtype: :py:class:`v1_5_3.web.vo.SerializationPoint`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/replication/serializationpoint/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SerializationPoint'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SerializationPoint objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_3.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_5_3.web.vo.SerializationPoint`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/replication/serializationpoint"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SerializationPoint'], returns_list=True, raw_result=raw_result)

