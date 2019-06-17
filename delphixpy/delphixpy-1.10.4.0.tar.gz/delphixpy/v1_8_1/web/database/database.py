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
Package "database"
"""
API_VERSION = "1.8.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_8_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.Container`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Container'], returns_list=False, raw_result=raw_result)

def get_all(engine, group=None, no_js_container_data_source=None, no_js_data_source=None, restoration=None, provision_container=None, valid_for_secure_replication=None):
    """
    Returns a list of databases on the system or within a group.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param group: Restrict databases to those within the specified group. This
        option is mutually exclusive with the "provisionContainer" option.
    :type group: ``TEXT_TYPE``
    :param no_js_container_data_source: Restrict databases to those which are
        not part of a Jet Stream data container. This option is mutually
        exclusive with the "noJSDataSource" option.
    :type no_js_container_data_source: ``bool``
    :param no_js_data_source: Restrict databases to those which are not part of
        a Jet Stream data layout (data template or data container). This option
        is mutually exclusive with the "noJSContainerDataSource" option.
    :type no_js_data_source: ``bool``
    :param restoration: Restrict listing to include only restoration datasets.
    :type restoration: ``bool``
    :param provision_container: Restrict databases to those provisioned from
        the specified container. This option is mutually exclusive with the
        "group" option.
    :type provision_container: ``TEXT_TYPE``
    :param valid_for_secure_replication: Restrict listing to include only
        datasets that can be securely replicated.
    :type valid_for_secure_replication: ``bool``
    :rtype: ``list`` of :py:class:`v1_8_1.web.vo.Container`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database"
    query_params = {"group": group, "noJSContainerDataSource": no_js_container_data_source, "noJSDataSource": no_js_data_source, "restoration": restoration, "provisionContainer": provision_container, "validForSecureReplication": valid_for_secure_replication}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Container'], returns_list=True, raw_result=raw_result)

def update(engine, ref, container=None):
    """
    Update the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param container: Payload object.
    :type container: :py:class:`v1_8_1.web.vo.Container`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s" % ref
    response = engine.post(url, container.to_dict(dirty=True) if container else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref, delete_parameters=None):
    """
    Delete the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param delete_parameters: Payload object.
    :type delete_parameters: :py:class:`v1_8_1.web.vo.DeleteParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/delete" % ref
    response = engine.post(url, delete_parameters.to_dict(dirty=True) if delete_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def undo(engine, ref):
    """
    Reverts the effects of the latest refresh or rollback operation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/undo" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def xpp_status_reset(engine, ref):
    """
    Resets the cross-platform provisioning status of a container where
    applicable.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/xppStatusReset" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def connection_info(engine, ref):
    """
    Returns the connection information for the source associated with this
    container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.SourceConnectionInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/connectionInfo" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SourceConnectionInfo'], returns_list=False, raw_result=raw_result)

def attach_source(engine, ref, attach_source_parameters):
    """
    Attaches a database source to a previously detached container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param attach_source_parameters: Payload object.
    :type attach_source_parameters:
        :py:class:`v1_8_1.web.vo.AttachSourceParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/attachSource" % ref
    response = engine.post(url, attach_source_parameters.to_dict(dirty=True) if attach_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def apply_live_source_resync(engine, ref):
    """
    Apply the resync to the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/applyLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete_xpp_upload(engine, ref):
    """
    Delete the cross-platform provisioning upload associated with this
    container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/deleteXppUpload" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def add_live_source(engine, ref, add_live_source_parameters):
    """
    Add a LiveSource for this dSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param add_live_source_parameters: Payload object.
    :type add_live_source_parameters:
        :py:class:`v1_8_1.web.vo.AddLiveSourceParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/addLiveSource" % ref
    response = engine.post(url, add_live_source_parameters.to_dict(dirty=True) if add_live_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def add_live_source_defaults(engine, ref):
    """
    Returns a partially constructed add LiveSource parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.AddLiveSourceParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/addLiveSource/defaults" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AddLiveSourceParameters'], returns_list=False, raw_result=raw_result)

def create_transformation(engine, ref, create_transformation_parameters):
    """
    Defines a new transformation against this container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param create_transformation_parameters: Payload object.
    :type create_transformation_parameters:
        :py:class:`v1_8_1.web.vo.CreateTransformationParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/createTransformation" % ref
    response = engine.post(url, create_transformation_parameters.to_dict(dirty=True) if create_transformation_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def sync(engine, ref, sync_parameters=None):
    """
    Performs SnapSync on a database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param sync_parameters: Payload object.
    :type sync_parameters: :py:class:`v1_8_1.web.vo.SyncParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/sync" % ref
    response = engine.post(url, sync_parameters.to_dict(dirty=True) if sync_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh(engine, ref, refresh_parameters):
    """
    Refreshes a container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param refresh_parameters: Payload object.
    :type refresh_parameters: :py:class:`v1_8_1.web.vo.RefreshParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/refresh" % ref
    response = engine.post(url, refresh_parameters.to_dict(dirty=True) if refresh_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def request_xpp_download(engine, ref):
    """
    Request download of cross-platform provisioning user script that was
    uploaded previously.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.FileDownloadResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/requestXppDownload" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FileDownloadResult'], returns_list=False, raw_result=raw_result)

def test_performance_mode_data_loss(engine, ref):
    """
    Test the effect of data loss as might be seen as a result of a Delphix
    Engine failure with performanceMode enabled.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/testPerformanceModeDataLoss" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def request_xpp_upload(engine, ref):
    """
    Request upload for cross-platform provisioning. See UploadParameters for
    more information on how to upload files.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.FileUploadResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/requestXppUpload" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FileUploadResult'], returns_list=False, raw_result=raw_result)

def start_live_source_resync(engine, ref):
    """
    Resync the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/startLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def xpp_status(engine, ref):
    """
    Get the cross-platform provisioning status of this container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_1.web.vo.XppStatus`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/xppStatus" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'XppStatus'], returns_list=False, raw_result=raw_result)

def switch_timeflow(engine, ref, switch_timeflow_parameters):
    """
    Switch to the latest point on the specified TimeFlow.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param switch_timeflow_parameters: Payload object.
    :type switch_timeflow_parameters:
        :py:class:`v1_8_1.web.vo.SwitchTimeflowParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/switchTimeflow" % ref
    response = engine.post(url, switch_timeflow_parameters.to_dict(dirty=True) if switch_timeflow_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def rollback(engine, ref, rollback_parameters):
    """
    Rolls back a container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param rollback_parameters: Payload object.
    :type rollback_parameters: :py:class:`v1_8_1.web.vo.RollbackParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/rollback" % ref
    response = engine.post(url, rollback_parameters.to_dict(dirty=True) if rollback_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def detach_source(engine, ref, detach_source_parameters):
    """
    Detaches a linked source from a database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param detach_source_parameters: Payload object.
    :type detach_source_parameters:
        :py:class:`v1_8_1.web.vo.DetachSourceParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/detachSource" % ref
    response = engine.post(url, detach_source_parameters.to_dict(dirty=True) if detach_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def remove_live_source(engine, ref):
    """
    Remove the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/removeLiveSource" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def discard_live_source_resync(engine, ref):
    """
    Discard the data from previous resync for LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/discardLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def purge_logs(engine, ref, purge_logs_parameters):
    """
    Delete logs to reclaim storage space.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_1.web.objects.Container.Container` object
    :type ref: ``str``
    :param purge_logs_parameters: Payload object.
    :type purge_logs_parameters: :py:class:`v1_8_1.web.vo.PurgeLogsParameters`
    :rtype: :py:class:`v1_8_1.web.vo.PurgeLogsResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/%s/purgeLogs" % ref
    response = engine.post(url, purge_logs_parameters.to_dict(dirty=True) if purge_logs_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'PurgeLogsResult'], returns_list=False, raw_result=raw_result)

def file_mapping(engine, file_mapping_parameters):
    """
    Generate file mappings for a particular TimeFlow point and a set of rules.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param file_mapping_parameters: Payload object.
    :type file_mapping_parameters:
        :py:class:`v1_8_1.web.vo.FileMappingParameters`
    :rtype: :py:class:`v1_8_1.web.vo.FileMappingResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/fileMapping"
    response = engine.post(url, file_mapping_parameters.to_dict(dirty=True) if file_mapping_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FileMappingResult'], returns_list=False, raw_result=raw_result)

def create_restoration_dataset(engine, restoration_dataset_parameters):
    """
    Creates a new restoration dataset from the specified source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param restoration_dataset_parameters: Payload object.
    :type restoration_dataset_parameters:
        :py:class:`v1_8_1.web.vo.RestorationDatasetParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/createRestorationDataset"
    response = engine.post(url, restoration_dataset_parameters.to_dict(dirty=True) if restoration_dataset_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def create_restoration_dataset_defaults(engine, timeflow_point_parameters):
    """
    Returns partially constructed parameters for creating a restoration
    dataset.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_8_1.web.vo.TimeflowPointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/createRestorationDataset/defaults"
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def create_empty(engine, empty_dataset_creation_parameters):
    """
    Creates a new empty virtual dataset.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param empty_dataset_creation_parameters: Payload object.
    :type empty_dataset_creation_parameters:
        :py:class:`v1_8_1.web.vo.EmptyDatasetCreationParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/createEmpty"
    response = engine.post(url, empty_dataset_creation_parameters.to_dict(dirty=True) if empty_dataset_creation_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def oracle_supported_character_sets(engine):
    """
    Retrieves all possible character sets for an Oracle database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_8_1.web.vo.OracleCharacterSet`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/oracleSupportedCharacterSets"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleCharacterSet'], returns_list=True, raw_result=raw_result)

def link(engine, link_parameters):
    """
    Links the database specified by link parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param link_parameters: Payload object.
    :type link_parameters: :py:class:`v1_8_1.web.vo.LinkParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/link"
    response = engine.post(url, link_parameters.to_dict(dirty=True) if link_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def link_defaults(engine, config=None):
    """
    Returns a partially constructed linking parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param config: The config being linked.
    :type config: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/link/defaults"
    query_params = {"config": config}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def validate_xpp(engine, timeflow_point_parameters):
    """
    Validate the container for cross-platform provisioning.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_8_1.web.vo.TimeflowPointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/validateXpp"
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def export(engine, export_parameters):
    """
    Provision a physical database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param export_parameters: Payload object.
    :type export_parameters: :py:class:`v1_8_1.web.vo.ExportParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/export"
    response = engine.post(url, export_parameters.to_dict(dirty=True) if export_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def xpp(engine, oracle_provision_parameters):
    """
    Provisions the container specified by the provision parameters to a
    different host platform.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param oracle_provision_parameters: Payload object.
    :type oracle_provision_parameters:
        :py:class:`v1_8_1.web.vo.OracleProvisionParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/xpp"
    response = engine.post(url, oracle_provision_parameters.to_dict(dirty=True) if oracle_provision_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def xpp_defaults(engine, timeflow_point_parameters):
    """
    Returns a partially constructed provision parameters object from the
    container's latest snapshot.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_8_1.web.vo.TimeflowPointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/xpp/defaults"
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def provision(engine, provision_parameters):
    """
    Provisions the container specified by the provision parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param provision_parameters: Payload object.
    :type provision_parameters: :py:class:`v1_8_1.web.vo.ProvisionParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/provision"
    response = engine.post(url, provision_parameters.to_dict(dirty=True) if provision_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def provision_defaults(engine, timeflow_point_parameters):
    """
    Returns a partially constructed provision parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_8_1.web.vo.TimeflowPointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/provision/defaults"
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

