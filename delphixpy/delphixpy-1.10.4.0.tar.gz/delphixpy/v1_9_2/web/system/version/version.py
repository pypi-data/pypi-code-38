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
Package "system.version"
"""
API_VERSION = "1.9.2"

from delphixpy.v1_9_2 import response_validator

def get(engine, ref):
    """
    Retrieve the specified SystemVersion object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.SystemVersion`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SystemVersion'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SystemVersion objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.SystemVersion`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SystemVersion'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SystemVersion object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def rollback(engine, ref):
    """
    Rollback a failed upgrade. This enables sources which have been disabled
    and updates the status of the upgrade version. This operation is only
    available for upgrade versions in the "DISABLE_FAILED" state.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/rollback" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def ignore_upgrade_check_results(engine, ref, upgrade_check_results_version_parameters):
    """
    Ignore upgrade check results corresponding to this version.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :param upgrade_check_results_version_parameters: Payload object.
    :type upgrade_check_results_version_parameters:
        :py:class:`v1_9_2.web.vo.UpgradeCheckResultsVersionParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/ignoreUpgradeCheckResults" % ref
    response = engine.post(url, upgrade_check_results_version_parameters.to_dict(dirty=True) if upgrade_check_results_version_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def reset_upgrade_check_results(engine, ref, upgrade_check_results_version_parameters):
    """
    Reset upgrade check results corresponding to this version.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :param upgrade_check_results_version_parameters: Payload object.
    :type upgrade_check_results_version_parameters:
        :py:class:`v1_9_2.web.vo.UpgradeCheckResultsVersionParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/resetUpgradeCheckResults" % ref
    response = engine.post(url, upgrade_check_results_version_parameters.to_dict(dirty=True) if upgrade_check_results_version_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def list_upgrade_check_results(engine, ref):
    """
    Lists the upgrade check results corresponding to this version.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/listUpgradeCheckResults" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def verify(engine, ref, verify_version_parameters=None):
    """
    Verify an upgrade version before applying.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :param verify_version_parameters: Payload object.
    :type verify_version_parameters:
        :py:class:`v1_9_2.web.vo.VerifyVersionParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/verify" % ref
    response = engine.post(url, verify_version_parameters.to_dict(dirty=True) if verify_version_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def resolve_upgrade_check_results(engine, ref, upgrade_check_results_version_parameters):
    """
    Resolve upgrade check results corresponding to this version.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :param upgrade_check_results_version_parameters: Payload object.
    :type upgrade_check_results_version_parameters:
        :py:class:`v1_9_2.web.vo.UpgradeCheckResultsVersionParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/resolveUpgradeCheckResults" % ref
    response = engine.post(url, upgrade_check_results_version_parameters.to_dict(dirty=True) if upgrade_check_results_version_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def apply(engine, ref, apply_version_parameters=None):
    """
    Applies the upgrade version to the current system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.SystemVersion.SystemVersion`
        object
    :type ref: ``str``
    :param apply_version_parameters: Payload object.
    :type apply_version_parameters:
        :py:class:`v1_9_2.web.vo.ApplyVersionParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/version/%s/apply" % ref
    response = engine.post(url, apply_version_parameters.to_dict(dirty=True) if apply_version_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

