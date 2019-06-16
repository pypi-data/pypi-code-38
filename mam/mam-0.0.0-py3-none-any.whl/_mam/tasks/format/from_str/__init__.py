"""Builtin conversions from std:out."""
# nosa: pylint[:Unused argument 'task']
# nosa: pylint[C0103]

import itertools
import json
import logging
import re
from typing import Iterator, List, Sequence, Tuple, TypeVar

from .. import formats
from ..helpers import (
    chain as _chain,
    create_internal as _create_internal,
    extract_files,
    extract_lines,
    format_line_match as _format_line_match,
    format_matches,
)
from ....core.objects import Format, Message, MessageKeys
from ....keys import TTask

__all__ = [
    'echo',

    'pycodestyle',
    'pycodestyle_pylint',
    'mypy',
    'pyflakes',
    'mccabe',
    'pylint',
    'pylint_old',
    'pylint_visual_studio',
    'pylint_parsable',
    'vulture',
    'bandit_mam_custom',
    'pylama',
    'jedi',
    'pydiatra',
    'radon',
    'radon_mi',
    'pydocstyle',
    'prospector_json',
    'detect_secrets',
    'pyroma',
]

logger = logging.getLogger(__name__)


def echo(task: TTask, data: str) -> List[Message]:
    """Echo std:out to output. Good for adding new converters."""
    print(data)  # nosa: (flake8-print)
    return []


pycodestyle = _format_line_match(formats.PYCODESTYLE)
pycodestyle_pylint = _format_line_match(formats.PYCODESTYLE_PYLINT)
mypy = _format_line_match(formats.MYPY)
pyflakes = _format_line_match(formats.PYFLAKES)
mccabe = _format_line_match(formats.MCCABE)
pylint = _format_line_match(formats.PYLINT)
pylint_old = _format_line_match(formats.PYLINT_OLD)
pylint_visual_studio = _format_line_match(formats.PYLINT_VISUAL_STUDIO)
pylint_parsable = _format_line_match(formats.PYLINT_PARSABLE)
vulture = _format_line_match(formats.VULTURE)
bandit_mam_custom = _format_line_match(formats.BANDIT_MAM_CUSTOM)
pylama = _format_line_match(formats.PYLAMA)
jedi = _format_line_match(formats.JEDI)
pydiatra = _format_line_match(formats.PYDIATRA)
radon = _chain(extract_files, format_matches(formats.RADON))
radon_mi = _chain(extract_lines, format_matches(formats.RADON_MI))

T = TypeVar('T')


def _pairwise(iterable: Sequence[T]) -> Iterator[Tuple[T, T]]:
    """Itertools recipe for pairwise iteration."""
    previous, current = itertools.tee(iterable)
    next(current, None)
    return zip(previous, current)


# file.py:1 at module level:
_pydocstyle_line = re.compile(
    r'^(?P<path>[^:]*)'
    r':(?P<line>[^ ]*)'
    r' (?P<extra>[^:]*)'
    r':.*$',
)

#         E001: example message
_pydocstyle_message = re.compile(
    r'^\s*(?P<code>[^:]*)'
    r':(?P<msg>.*)'
    r'$',
)


def pydocstyle(task: TTask, output: str) -> Iterator[Message]:
    """Convert from pydocstyle output."""
    lines = _pairwise(output.split('\n'))
    for prev, curr in lines:
        if not prev:
            continue
        prev_match = _pydocstyle_line.match(prev)
        curr_match = _pydocstyle_message.match(curr)
        if prev_match is None and curr_match is None:
            if prev:
                logger.warning(Format(
                    'No match for pydocstyle in {line}.',
                    line=prev,
                ))
            continue
        next(lines, None)
        group = prev_match.groupdict() if prev_match is not None else {}
        group.update(curr_match.groupdict() if curr_match is not None else {})
        yield _create_internal(task, group)


def prospector_json(task: TTask, output: str) -> Iterator[Message]:
    """Convert from prospector output."""
    for obj in json.loads(output)['messages']:
        location = obj['location']
        group = {
            MessageKeys.APP: obj['source'],
            MessageKeys.PATH: location['path'],
            MessageKeys.LINE: location['line'],
            MessageKeys.CHAR: location['character'],
            MessageKeys.MESSAGE: obj['message'],
            'module': location['module'],
            'function': location['function'],
        }
        if obj['code'][0].islower():
            group[MessageKeys.CODE_READABLE] = obj['code']
        else:
            group[MessageKeys.CODE] = obj['code']
        yield _create_internal(task, group)


def detect_secrets(task: TTask, output: str) -> Iterator[Message]:
    """Convert from detect-secrets output."""
    for path, secrets in json.loads(output)['results'].items():
        for secret in secrets:
            yield _create_internal(task, {
                MessageKeys.PATH: path,
                MessageKeys.LINE: secret['line_number'],
                MessageKeys.CODE_READABLE: secret['type'],
                MessageKeys.MESSAGE: (
                    'Hashed secret {}'
                    .format(secret['hashed_secret'])
                ),
            })


def pyroma(task: TTask, output: str) -> Iterator[Message]:
    """Convert from Pyroma output."""
    seperator = 0
    for line in output.splitlines():
        if line.startswith('---'):
            seperator += 1
            continue
        if seperator == 2:
            yield _create_internal(task, {
                MessageKeys.MESSAGE: line,
            })
