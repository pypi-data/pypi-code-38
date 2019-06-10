import sys
from typing import Any, Optional, Union

MINSIZE = -sys.maxsize - 1  # smallest natural int


def safe_index(seq: list, value: Any) -> Optional[int]:
    """
    ``list.index()`` except returns ``None`` rather than throwing
    a ``ValueError`` should the value not exist in the list.
    """
    try:
        return seq.index(value)
    except ValueError:
        return None


def sort_order(name: Any, preferred: list, rest: list):
    index = safe_index(preferred, name)
    if index is not None:
        return MINSIZE + index
    return rest.index(name)


def prefsorted(seq: list,
               preferred: Union[str, list, None] = None) -> list:
    if isinstance(preferred, str):
        preferred = preferred.split()
    elif preferred is None:
        preferred = []
    print('preferred:', preferred)
    return sorted(seq, key=lambda name: sort_order(name, preferred, seq))
