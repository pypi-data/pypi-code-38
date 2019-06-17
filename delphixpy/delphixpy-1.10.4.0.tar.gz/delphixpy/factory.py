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

"""
Instantiate an object of the type given by the 'type_name' string.
The 'data' value will be passed as the single constructor argument
when creating the new object, and must correspond to the JSON data
of an object that extends the TypedObject webservice type (i.e has
a 'type' field).
"""

import importlib


_VALUE_OBJECTS = 'delphixpy.web.vo'


def unwrap_partial_result(obj):
    if hasattr(obj, 'type') and obj.type == 'PartialResult':
        return obj.items
    else:
        return obj


def create_object(data, object_type=None):
    class_name = data.get('type', object_type)
    cls = _import_class(class_name)
    obj = cls.from_dict(data)
    return unwrap_partial_result(obj)


def validate_type(obj, class_name):
    cls = _import_class(class_name)
    assert isinstance(obj, cls), \
        "Type validation failed: Object %s is not of type %s" % (obj, cls)


def _import_class(class_name):
    module = importlib.import_module(_VALUE_OBJECTS)
    return getattr(module, class_name)