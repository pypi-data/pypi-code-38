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
Package "network.route"
"""
API_VERSION = "1.8.0"

from delphixpy.v1_8_0 import response_validator

def get_all(engine):
    """
    Lists entries in the routing table.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_8_0.web.vo.NetworkRoute`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/route"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'NetworkRoute'], returns_list=True, raw_result=raw_result)

def add(engine, network_route=None):
    """
    Add a route to the routing table.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param network_route: Payload object.
    :type network_route: :py:class:`v1_8_0.web.vo.NetworkRoute`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/route/add"
    response = engine.post(url, network_route.to_dict(dirty=True) if network_route else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def lookup(engine, network_route_lookup_parameters):
    """
    Lookup a route by destination address.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param network_route_lookup_parameters: Payload object.
    :type network_route_lookup_parameters:
        :py:class:`v1_8_0.web.vo.NetworkRouteLookupParameters`
    :rtype: :py:class:`v1_8_0.web.vo.NetworkRoute`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/route/lookup"
    response = engine.post(url, network_route_lookup_parameters.to_dict(dirty=True) if network_route_lookup_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'NetworkRoute'], returns_list=False, raw_result=raw_result)

def delete(engine, network_route=None):
    """
    Delete a route from the routing table.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param network_route: Payload object.
    :type network_route: :py:class:`v1_8_0.web.vo.NetworkRoute`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/route/delete"
    response = engine.post(url, network_route.to_dict(dirty=True) if network_route else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

