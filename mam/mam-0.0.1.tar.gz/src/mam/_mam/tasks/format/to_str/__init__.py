"""Builtin output formats."""
# nosa: (flake8-print)

import itertools
import os
from pprint import pprint
from typing import Iterator, Sequence

from ....core.objects import Less, Message

__all__ = [
    'default',
    'standard',
    'json',
]


def _default(data: Sequence[Message]) -> Iterator[str]:
    """Build default output."""
    for path, group in itertools.groupby(
        data,
        key=lambda item: item.path,
    ):
        if not isinstance(path, Less):
            yield os.path.relpath(path)
        else:
            yield str(None)
        for line, by_lines in itertools.groupby(
            group,
            key=lambda item: item.line,
        ):
            yield '    Line {line}'.format(line=line)
            for result in by_lines:
                yield '        {0.app}: {0.code} / {0.message}'.format(result)
                continue
                for extra in result.extras:
                    if extra:
                        yield '            {extra}'.format(extra=extra)


def default(data: Sequence[Message]) -> None:
    """Display using default output."""
    print('\n'.join(_default(data)))


def standard(data: Sequence[Message]) -> None:
    """Display using standard output."""
    for result in data:
        print(
            '{file}:{line}:{character}: {program}[{code}] {message}'
            .format(**result.to_dict()),
        )


def json(data: Sequence[Message]) -> None:
    """Display in JSON format."""
    # TODO: change to JSON format.
    pprint([m.to_dict() for m in data])
