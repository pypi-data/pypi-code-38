import sys
from typing import Union


def prefsorted(seq: list,
               preferred: Union[str, list, None] = None,
               reverse: bool = False) -> list:
    if isinstance(preferred, str):
        preferred = preferred.split()
    elif preferred is None:
        preferred = []


    taken = []
    rest = list(seq)[:]
    for p in preferred:
        try:
            while True:
                rest.remove(p)
                taken.append(p)
        except ValueError:
            pass

    if reverse:
        return rest + taken
    else:
        return taken + rest