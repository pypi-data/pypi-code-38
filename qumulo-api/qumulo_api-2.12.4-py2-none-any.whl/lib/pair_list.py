# Copyright (c) 2019 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

'''
Utilities for manipulating a "pair list" data structure, which is of the
following form:

  [{'key': b, 'value': 8},
   {'key': c, 'value': 12},
   {'key': a, 'value': 1}]

Such structures are used by a lot of Qumulo APIs, and this module gives
some easy lookup methods.
'''

def find_by_key(kv_map, key):
    '''
    Given a list of dictionaries like {"key": ...; "value": ...},
    extract the value corresponding to a given key.
    '''
    # there should be exactly one:
    (result,) = [i['value'] for i in kv_map if i['key'] == key]
    return result

def find_by_key_default(kv_map, key, default=None):
    return next(
        (i.get('value', default) for i in kv_map if i['key'] == key),
        default)
