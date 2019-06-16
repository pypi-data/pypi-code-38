"""Mutate data."""

import collections
import dataclasses
import itertools
import operator
from typing import (
    Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union,
)

from mypy_extensions import TypedDict  # nosa: pylint[E0401]

from .nosa import remove_nosa
from ...core.objects import LESS, Less, Message

__all__ = [
    'remove_nosa',
    'sort_location',
    'clean_extensions',
    'merge_duplicates',
    'remove_mam',
]

# nosa(29): pylint[C0103]
_get_location = operator.attrgetter(
    'path',
    'line',
    'char',
)
_get_line = operator.attrgetter(
    'path',
    'line',
)
_get_location_with_program = operator.attrgetter(
    'path',
    'line',
    'char',
    'app',
)
_get_programless_info = operator.attrgetter(
    'path',
    'line',
    'char',
    'code',
    'message',
)
_get_error_info = operator.attrgetter(
    'code',
    'message',
)
_get_program_message = operator.attrgetter(
    'app',
    'message',
)


def sort_location(data: Sequence[Message]) -> Sequence[Message]:
    """Sort data by location."""
    # return sorted(data, key=_get_location_with_program)
    return sorted(data, key=_get_line)


TValue = Union[Less, Any]


def clean_extensions(data: Sequence[Message]) -> Iterator[Message]:
    """Condense extensions into one message."""
    for _, group_ in itertools.groupby(data, key=_get_location):
        group = list(group_)
        messages: Dict[Tuple[TValue, ...], Tuple[Set[str], List[str]]] = {}
        for result in group:
            programs, extends = messages.setdefault(
                _get_error_info(result),
                (set(), []),
            )
            programs.add(result.app)
            extends.extend(result.extends)

        output: Dict[Tuple[TValue, ...], Tuple[bool, Optional[str]]] = {}
        for key, (programs, extends) in messages.items():
            if len(programs) == 1:
                output[key] = (True, programs.pop())
                continue
            count = collections.Counter(extends)
            for prog, _ in count.most_common():
                if prog in programs:
                    output[key] = (True, prog)
                    break
            else:
                if count:
                    (ext, _), = count.most_common(1)
                    output[key] = (False, ext)
                else:
                    output[key] = (False, None)

        for result in group:
            key = _get_error_info(result)
            is_program, name = output[key]
            obj = None
            if is_program:
                if result.app == name:
                    obj = result
            elif name is None:
                obj = result
            elif name in result.extends:
                obj = result
                obj.app = '*' + name
            if obj is not None:
                messages.pop(key, None)
                yield obj


def merge_duplicates(data: Sequence[Message]) -> Iterator[Message]:
    """Merge duplicate messages."""
    for _, group_ in itertools.groupby(data, _get_line):
        group = list(sorted(list(group_), key=_get_program_message))
        for _, duplicates_ in itertools.groupby(group, _get_program_message):
            duplicates = iter(duplicates_)
            output = next(duplicates)  # nosa: pylint[R1708]
            for dup in duplicates:
                for field in dataclasses.fields(dup):
                    value = getattr(dup, field.name, LESS)
                    if value is LESS:
                        continue
                    if getattr(output, field.name, LESS) is LESS:
                        setattr(output, field.name, value)
                output.extras.extend(dup.extras)
            yield output


class TApp(TypedDict):
    """App types."""

    code: Sequence[str]
    message: Sequence[str]
    code_readable: Sequence[str]


TUNWANTED = Dict[str, Optional[TApp]]
UNWANTED = {
    'pylint': {
        'code': {'R0903', 'R1705', 'W0212', 'W0511'},
        'message': {
            'Too few public methods',
            "Value 'Generic' is unsubscriptable",
        },
    },
    'mccabe': None,
    'pycodestyle': {
        'code': {'E124'},
    },
    'pep257': {
        'code': {'D203', 'D212'},
    },
}


def _unwanted_code_readable(message: Message, unwanted):
    if 'code_readable' in unwanted:
        if message.code_readable in unwanted['code_readable']:
            return True
    return False


def _unwanted_code(message: Message, unwanted):
    if 'code' in unwanted:
        full_code = LESS.default(message.code, '')
        for code in unwanted['code']:
            if full_code.startswith(code):
                return True
    return False


def _unwanted_message(message: Message, unwanted):
    if 'message' in unwanted:
        full_message = LESS.default(message.message, '')
        for message_ in unwanted['message']:
            if message_ in full_message:
                return True
    return False


def remove_mam(data: Sequence[Message]) -> Iterator[Message]:
    """Remove unwanted warnings from MAM output."""
    for message in data:
        unwanted = UNWANTED.get(message.app, {})
        if (unwanted is None
            or _unwanted_code_readable(message, unwanted)
            or _unwanted_code(message, unwanted)
            or _unwanted_message(message, unwanted)
        ):
            continue
        yield message
