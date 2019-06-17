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
Package "jetstream.usage.container"
"""
API_VERSION = "1.9.3"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_3 import response_validator

def list_container_usage_data(engine, data_container=None, user=None, template=None):
    """
    Lists the usage breakdown for data containers.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param data_container: If passed in, this query parameter restricts the API
        to only return the usage information for the given data container. This
        parameter is mutually exclusive with the "template" and "user"
        parameters.
    :type data_container: ``TEXT_TYPE``
    :param user: If passed in, this query parameter restricts the API to only
        return the usage information for all of the data containers owned by
        the given user. This parameter is mutually exclusive with the
        "dataContainer" and "template" parameters.
    :type user: ``TEXT_TYPE``
    :param template: If passed in, this query parameter restricts the API to
        only return the usage information for all of the data containers from
        the given data template. This parameter is mutually exclusive with the
        "dataContainer" and "user" parameters.
    :type template: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_3.web.vo.JSContainerUsageData`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/usage/container/listContainerUsageData"
    query_params = {"dataContainer": data_container, "user": user, "template": template}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSContainerUsageData'], returns_list=True, raw_result=raw_result)

