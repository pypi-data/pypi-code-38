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
Package "storage.device"
"""
API_VERSION = "1.10.1"

from delphixpy.v1_10_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified StorageDevice object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_1.web.vo.StorageDevice`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StorageDevice'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List StorageDevice objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_10_1.web.vo.StorageDevice`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StorageDevice'], returns_list=True, raw_result=raw_result)

def prime(engine, ref):
    """
    Prime the storage device by initializing any free space on the device, so
    that subsequent accesses will have lower latency. Storage devices will be
    initialized automatically when they are first added to the storage pool,
    and when they are expanded. If an initialization was canceled earlier, this
    allows the operation to be continued.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s/prime" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def remove_verify(engine, ref):
    """
    Verify that a device can be removed.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_1.web.vo.StorageDeviceRemovalVerifyResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s/removeVerify" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StorageDeviceRemovalVerifyResult'], returns_list=False, raw_result=raw_result)

def configure(engine, ref):
    """
    Configures the device for use in the domain. Generates an error if the
    device is already configured.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s/configure" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def expand(engine, ref):
    """
    Use any additional available space after the underlying device has been
    expanded. Generates an error if the device is not configured, and does
    nothing if there is no additional available space.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s/expand" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def remove(engine, ref):
    """
    Starts the removal of a device.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.StorageDevice.StorageDevice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/%s/remove" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh_cache(engine):
    """
    Triggers a refresh of the storage device cache. This cache contains
    information about the storage devices contained on the system, allowing
    operations some operations, such as listing all of the devices, to be
    performed more quickly.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/storage/device/refreshCache"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

