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

import uuid
from typing import List, Optional, Any, Tuple

import pandas as pd

__all__ = [
    'unique_id',
    'head',
    'tuples_with_nans_to_tuples_with_nones',
    'split_list_of_tuples',
]

def unique_id() -> str:
    """
    Returns a unique id.
    """
    return str(uuid.uuid4())


def head(l:Optional[List[Any]]) -> Optional[Any]:
    """
    Gets the head of a list if its not empty.
    If its empty, None is returned ...
    :param l:
    :return:
    """
    if l is None:
        return None
    list_with_first_elem = l[0:1]
    return list_with_first_elem[0] if list_with_first_elem else None


def nan_to_none(value:Any) -> Optional[Any]:
    """
    Turns NaNs to Nones ...
    :return: 
    """
    return None if isinstance(value, float) and pd.isna(value) else value


def tuples_with_nans_to_tuples_with_nones(iter:List[Tuple[Any, ...]]) -> List[Tuple[Optional[Any], ...]]:
    """
    Replaces NaNs within a tuple into Nones.

    # ... I only want to check for NaNs on primitives... and replace them with None ... not Lists ...
        # Unfortunately python has no way of saying "isPrimitive"
        # Luckily, NaNs are floats ...!

    :param iter:
    :return:
    """
    return [
        tuple([
            nan_to_none(x) for x in tup
        ])
        for tup in iter
    ]


def split_list_of_tuples(l:List[Tuple[Any, ...]]) -> Optional[Tuple[List[Any], ...]]:
    """
    NOTE: No python way of specifying that the return type ... the number of List[Any] in it depends on the size of the tuple passed in ...
    :param l:
    :return:
    """
    if not l:
        return None
    lengths_of_each_tuple = list(map(lambda x: len(list(x)), l))
    # We know there is at least one item ...
    all_tuples_same_length =  all(map(
        lambda x: x == lengths_of_each_tuple[0],
        lengths_of_each_tuple
    ))
    assert all_tuples_same_length, "All tuples must be of the same length: {}".format(lengths_of_each_tuple[0])
    return tuple(*[[tupe[i] for tupe in l] for i in range(0, lengths_of_each_tuple[0])])
