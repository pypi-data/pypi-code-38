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
Package "network.interface"
"""
API_VERSION = "1.10.0"

from delphixpy.v1_10_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified NetworkInterface object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.NetworkInterface.NetworkInterf
        ace` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_0.web.vo.NetworkInterface`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/interface/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'NetworkInterface'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List NetworkInterface objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_10_0.web.vo.NetworkInterface`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/interface"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'NetworkInterface'], returns_list=True, raw_result=raw_result)

def update(engine, ref, network_interface=None):
    """
    Update the specified NetworkInterface object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.NetworkInterface.NetworkInterf
        ace` object
    :type ref: ``str``
    :param network_interface: Payload object.
    :type network_interface: :py:class:`v1_10_0.web.vo.NetworkInterface`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/interface/%s" % ref
    response = engine.post(url, network_interface.to_dict(dirty=True) if network_interface else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh(engine, ref):
    """
    Refreshes each address on the specified interface. For static addresses,
    this restarts duplicate address detection. For DHCP addresses, this
    attempts to extend the lease.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.NetworkInterface.NetworkInterf
        ace` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/interface/%s/refresh" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

