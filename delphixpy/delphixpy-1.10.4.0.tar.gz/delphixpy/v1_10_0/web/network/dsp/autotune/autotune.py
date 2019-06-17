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
Package "network.dsp.autotune"
"""
API_VERSION = "1.10.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_0 import response_validator

def run(engine, dsp_autotuner_parameters):
    """
    Runs the DSP autotuner to find the best parameters for the specified
    target.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param dsp_autotuner_parameters: Payload object.
    :type dsp_autotuner_parameters:
        :py:class:`v1_10_0.web.vo.DSPAutotunerParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/dsp/autotune/run"
    response = engine.post(url, dsp_autotuner_parameters.to_dict(dirty=True) if dsp_autotuner_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def show_saved_best_params(engine, target_address=None):
    """
    Returns the best parameters found by previous autotuner runs for the target
    address.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param target_address: Target address for which to display the saved best
        parameters.
    :type target_address: ``TEXT_TYPE``
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/network/dsp/autotune/showSavedBestParams"
    query_params = {"targetAddress": target_address}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

