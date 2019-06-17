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
Package "source.operationTemplate"
"""
API_VERSION = "1.6.1"

from delphixpy.v1_6_1 import response_validator

def create(engine, operation_template=None):
    """
    Create a new OperationTemplate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param operation_template: Payload object.
    :type operation_template: :py:class:`v1_6_1.web.vo.OperationTemplate`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/operationTemplate"
    response = engine.post(url, operation_template.to_dict(dirty=True) if operation_template else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified OperationTemplate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_6_1.web.objects.Operatio
        nTemplate.OperationTemplate` object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_1.web.vo.OperationTemplate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/operationTemplate/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OperationTemplate'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists templates available in the Delphix Engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_6_1.web.vo.OperationTemplate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/operationTemplate"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OperationTemplate'], returns_list=True, raw_result=raw_result)

def update(engine, ref, operation_template=None):
    """
    Update the specified OperationTemplate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_6_1.web.objects.Operatio
        nTemplate.OperationTemplate` object
    :type ref: ``str``
    :param operation_template: Payload object.
    :type operation_template: :py:class:`v1_6_1.web.vo.OperationTemplate`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/operationTemplate/%s" % ref
    response = engine.post(url, operation_template.to_dict(dirty=True) if operation_template else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified OperationTemplate object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_6_1.web.objects.Operatio
        nTemplate.OperationTemplate` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/operationTemplate/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

