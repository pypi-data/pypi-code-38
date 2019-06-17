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
Package "maskingjob"
"""
API_VERSION = "1.10.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified MaskingJob object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.MaskingJob.MaskingJob` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_1.web.vo.MaskingJob`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'MaskingJob'], returns_list=False, raw_result=raw_result)

def get_all(engine, container=None):
    """
    Returns a list of all Masking Jobs on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param container: List only the Masking Jobs that are associated with the
        provided container.
    :type container: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_1.web.vo.MaskingJob`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob"
    query_params = {"container": container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'MaskingJob'], returns_list=True, raw_result=raw_result)

def update(engine, ref, masking_job=None):
    """
    Update the specified MaskingJob object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.MaskingJob.MaskingJob` object
    :type ref: ``str``
    :param masking_job: Payload object.
    :type masking_job: :py:class:`v1_10_1.web.vo.MaskingJob`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/%s" % ref
    response = engine.post(url, masking_job.to_dict(dirty=True) if masking_job else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified MaskingJob object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_1.web.objects.MaskingJob.MaskingJob` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def get_local_service_status(engine):
    """
    The service state for the local Masking Service.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/getLocalServiceStatus"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def create(engine, masking_job):
    """
    Creates a new Masking Job entry based on the specified object. For testing
    only.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    :param masking_job: Payload object.
    :type masking_job: :py:class:`v1_10_1.web.vo.MaskingJob`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/create"
    response = engine.post(url, masking_job.to_dict(dirty=True) if masking_job else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def fetch(engine):
    """
    Queries the local Delphix Masking Engine instance and creates Masking Job
    entries for all jobs found.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_1.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/maskingjob/fetch"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

