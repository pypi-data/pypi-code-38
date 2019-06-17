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
Package "sourceconfig.oracle.pdb"
"""
API_VERSION = "1.6.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_6_2 import response_validator

def get_all(engine, cdb_config=None):
    """
    Returns a list of Oracle PDB configs within a container database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param cdb_config: Restrict PDB configs to those belonging to the specified
        CDB source config.
    :type cdb_config: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_6_2.web.vo.OraclePDBConfig`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig/oracle/pdb"
    query_params = {"cdbConfig": cdb_config}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OraclePDBConfig'], returns_list=True, raw_result=raw_result)

