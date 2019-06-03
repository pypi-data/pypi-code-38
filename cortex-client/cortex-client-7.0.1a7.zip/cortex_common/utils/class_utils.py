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

from typing import Callable, Any
from functools import wraps


__all__ = [
    'state_modifier',
]

def state_modifier(result_factory:Callable, state_updater:Callable[[Any, Any], Any]):
    """

    :param result_factory:
    :param state_updater:
    :return:
    """
    def inner_decorator(f_to_wrap:Callable):
        @wraps(result_factory)
        def f_that_gets_called(*args, **kwargs):
            state_updater(args[0], result_factory(*args[1:], **kwargs))
            return f_to_wrap(args[0])
        return f_that_gets_called
    return inner_decorator
