"""Collection of mutations when merging inherited configs."""
# nosa: pylint[:Unused argument 'info']

import itertools
import logging
from typing import (
    Any, Iterable, List, Optional, Sequence, Union,
)

from .tasks import handle_tasks as tasks
from .typings import TNone
from ...core.configs import MutationInfo, NULL

__all__ = [
    'mutations',
    'update',
    'extend',
    'child',
    'tasks',
    'defer',
    'zip_update',
]

# nosa(1): pylint[C0103]
logger = logging.getLogger(__name__)


def mutations(orig: Any, parent: Any, *, info: MutationInfo) -> dict:
    """Merge mutations."""
    if info.path[-1] == '$':
        if isinstance(orig, dict) or isinstance(parent, dict):
            raise ValueError("`$` can't be a dictionary.")
        return child(orig, parent, info=info)

    for dict_ in (orig, parent):
        for key in (dict_ or {}).keys():
            if key != '$' and isinstance(dict_[key], str):
                dict_[key] = {'$': dict_[key]}

    return defer(orig, parent, info=info)


def update(orig: Union[TNone, dict],
           parent: Union[TNone, dict],
           **_,
           ) -> Optional[dict]:
    """
    Merge two dictionaries.

    Child keys overwrite parent keys.
    This doesn't merge them, like `defer` does.
    """
    if orig is None or orig is NULL and parent is None:
        return None
    new = NULL.default_none(parent, {}).copy()
    new.update(NULL.default_none(orig, {}))
    return new


def extend(orig: Union[TNone, list],
           parent: Union[TNone, list],
           **_,
           ) -> list:
    """Merge two lists, by extending the first with the second."""
    return (
        NULL.default_none(parent, [])
        + NULL.default_none(orig, [])
    )


def child(orig: Any, parent: Any, *, info: MutationInfo) -> Any:
    """Take child, unless it's NULL."""
    if orig is NULL:
        return parent
    return orig


# TODO: make work with all generic typing types.
# TODO: handle in different ways - lists updated inplace or extended.
def defer(orig: Union[TNone, dict],
          parent: Union[TNone, dict],
          *,
          info: MutationInfo,
          ) -> dict:
    """
    Merge two dictionaries.

    defers conflicting values to another merger.
    """
    output = {}
    orig_: dict = NULL.default_none(orig, {})
    parent_: dict = NULL.default_none(parent, {})
    for key in list(set(orig_.keys()) | set(parent_.keys())):
        output[key] = info.merge(
            orig_.get(key, NULL),
            parent_.get(key, NULL),
            key,
        )
    return output


def zip_update(orig: Iterable[Union[TNone, Sequence]],
               parent: Iterable[Union[TNone, Sequence]],
               *,
               info: MutationInfo,
               ) -> List[Optional[Any]]:
    """Merge two list of lists."""
    return [
        (
            (p or [])
            + (o or [])
        ) or None
        for o, p in itertools.zip_longest(
            orig or [],
            parent or [],
            fillvalue=[],
        )
    ]
