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
Package "jetstream.capacity.branch"
"""
API_VERSION = "1.4.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_4_1 import response_validator

def list_branch_capacity_data(engine, data_container=None, branch=None):
    """
    Lists the capacity breakdown for Jet Stream branches. By default, the
    capacity breakdown for all Jet Stream branches is returned.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param data_container: If passed in, this query parameter restricts the API
        to only return the capacity information for all branches in the given
        data container. This parameter is mutually exclusive with the "branch"
        parameter.
    :type data_container: ``TEXT_TYPE``
    :param branch: If passed in, this query parameter restricts the API to only
        return the capacity information for the given branch. This parameter is
        mutually exclusive with the "dataContainer" parameter.
    :type branch: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_4_1.web.vo.JSBranchCapacityData`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/capacity/branch/listBranchCapacityData"
    query_params = {"dataContainer": data_container, "branch": branch}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSBranchCapacityData'], returns_list=True, raw_result=raw_result)

