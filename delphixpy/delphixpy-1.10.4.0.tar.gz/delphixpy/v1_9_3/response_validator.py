# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from delphixpy.v1_9_3 import exceptions
from delphixpy.v1_9_3 import factory
from delphixpy.v1_9_3.job_context import wait
from delphixpy.v1_9_3.web.vo import OKResult, ErrorResult, ListResult


def validate(response, engine=None):
    """
    Takes as input a Result object and returns its payload
    if the status is "OK". Otherwise a RequestError is raised.

    :param response: JSON response from the engine as a dict
    :param engine: DelphixEngine object
    """
    if response.get('status') == 'OK':
        if isinstance(response.get('result'), list):
            res = ListResult.from_dict(response)
        else:
            res = OKResult.from_dict(response)
    elif response.get('status') == 'ERROR':
        res = ErrorResult.from_dict(response)
        raise exceptions.RequestError(res.error)

    if res.job:
        if engine.is_async:
            engine.job_contexts[-1][1].append(res.job)
        else:
            wait(engine, res.job)
        engine.last_job = res.job

    return res.result


def parse_result(result, undef_enabled, return_types, returns_list, raw_result):
    """
    Parses API call results of different data structures into the correct object
    types.
    """
    if isinstance(result, list):
        return [factory.create_object(o) for o in result]
    elif isinstance(result, dict):
        return factory.create_object(result)
    else:
        return result