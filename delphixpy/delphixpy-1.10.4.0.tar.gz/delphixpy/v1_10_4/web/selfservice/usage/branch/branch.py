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
Package "selfservice.usage.branch"
"""
API_VERSION = "1.10.4"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_4 import response_validator

def list_branch_usage_data(engine, data_container=None):
    """
    Lists the usage breakdown for Self-Service branches belonging to the given
    container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param data_container: The usage information for the branches on this data
        container will be returned.
    :type data_container: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_4.web.vo.JSBranchUsageData`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/selfservice/usage/branch/listBranchUsageData"
    query_params = {"dataContainer": data_container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSBranchUsageData'], returns_list=True, raw_result=raw_result)

