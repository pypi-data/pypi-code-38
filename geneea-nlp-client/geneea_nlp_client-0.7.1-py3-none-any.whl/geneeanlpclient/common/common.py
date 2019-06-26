# Copyright 2019 Geneea Analytics s.r.o.
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

from typing import Any, Sequence

import math


def isSequential(nums: Sequence[int]) -> bool:
    """ Checks whether the nums sequence is a subsequence of integers, i.e. n, n+1, n+2, ... """
    if len(nums) <= 1:
        return True

    prev = nums[0]
    for x in nums[1:]:
        if x != prev + 1:
            return False
        prev = x

    return True


def toBool(val: Any) -> bool:
    """ Converts the given value into boolean. (str "true" and "1" or numeric 1 are True)"""
    if val is None:
        return False
    elif isinstance(val, bool):
        return val
    else:
        return str(val).strip().lower() in {'true', '1'}


def toFloat(val: Any, default: float=0.0) -> float:
    """
    Converts the given value into float.

    :param val: value to convert
    :param default: return value when `val` cannot be converted or is None or "NaN"
    :return: input `val` converted to float value
    :since: 0.7.1
    """
    if val is None:
        return default
    else:
        try:
            fval = float(val)
            return default if math.isnan(fval) else fval
        except:
            return default
