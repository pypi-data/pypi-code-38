from typing import (
    Sequence,
    Union,
    Any,
)


def do(
    seq: Sequence,
    indexes: Union[int, Sequence[int]]
) -> Any:
    is_single_value = isinstance(indexes, int)
    if is_single_value:
        indexes = (indexes,)
    reduced = []
    for idx in indexes:
        try:
            reduced.append(seq[idx])
        except IndexError:
            pass
    if not reduced:
        return
    if is_single_value:
        return reduced[0]
    return reduced
