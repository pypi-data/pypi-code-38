"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__all__ = [
    'AttrsAsDict',
]

class _AttrsAsDictMeta(type):
    """
    Meta class to help transform any python class that extends this type into a dict where the keys are the attributes
    of the class and the values are the respected attribute values.

    This class is useful in place of enums, where we want an IDE to auto fill in attributes, but we want to treat the
    class like a dict as well.
    """
    def __iter__(self):
        return zip(self.keys(), self.values())

    def __getitem__(self, arg):
        return dict(list(self)).get(arg)

    def keys(cls):
        return list(filter(lambda x: x[0] != "_", cls.__dict__.keys()))

    def values(cls):
        return [ getattr(cls, k) for k in cls.keys()]

    def items(cls):
        return dict(list(cls)).items()


class AttrsAsDict(metaclass=_AttrsAsDictMeta):
    """
    Any class that extends this will have its attributes be transformable into a dict.
    """
    pass