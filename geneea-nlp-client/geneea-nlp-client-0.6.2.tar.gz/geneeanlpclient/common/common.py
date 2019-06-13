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

from typing import Sequence


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

