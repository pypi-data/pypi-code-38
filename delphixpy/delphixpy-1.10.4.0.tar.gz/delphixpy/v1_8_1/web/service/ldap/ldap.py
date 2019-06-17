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
Package "service.ldap"
"""
API_VERSION = "1.8.1"

from delphixpy.v1_8_1.web.service.ldap import server
from delphixpy.v1_8_1 import response_validator

def get(engine):
    """
    Retrieve the specified LdapInfo object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_8_1.web.vo.LdapInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/ldap"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'LdapInfo'], returns_list=False, raw_result=raw_result)

