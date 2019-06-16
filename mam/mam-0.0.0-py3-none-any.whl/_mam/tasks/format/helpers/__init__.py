"""Conversion helpers."""
# nosa: pylint[:Unused argument 'task']

import logging
import os
import re
from typing import (
    Any, Callable, Dict, Generic, Iterator,
    List, Optional, TypeVar,
)

import parse  # nosa: (mypy)
# nosa: pylint[:Module 'parse' has no]

from typing_extensions import Protocol   # nosa: pylint[E0401]

from ....core.objects import Format, Message, MessageKeys
from ....keys import TTask, Task

__all__ = [
    'create_internal',
    'regex_line_match',
    'format_line_match',
    'chain',
    'extract_files',
    'extract_lines',
    'format_matches',
    'Converter',
]

# nosa(4): pylint[C0103]
logger = logging.getLogger(__name__)
T = TypeVar('T')
TIn = TypeVar('TIn', contravariant=True)
TOut = TypeVar('TOut', covariant=True)


class Converter(Protocol, Generic[TIn, TOut]):
    """Converter interface."""

    def __call__(self, task: TTask, output: TIn) -> TOut:
        """Convert task and output to TOut."""


def cast(value: Any, type_: Callable[[Any], T], default: Any = None,
         ) -> Optional[T]:
    """Cast value defaulting to default on TypeError."""
    try:
        return type_(value)
    except TypeError:
        return default


@parse.with_pattern(r'.:.+?|.*?')
def _parse_file(path: str) -> str:
    """Handle File types in formats."""
    return path


def create_internal(task: TTask, msg: Dict[str, Any]) -> Message:
    """Create message from task and values."""
    path = msg.pop(MessageKeys.PATH, None)
    if path is not None and not os.path.isabs(path):
        path = os.path.abspath(path)
    return Message.from_dict({
        MessageKeys.APP: msg.pop(MessageKeys.APP, None) or task[Task.NAME],
        MessageKeys.PATH: path,
        MessageKeys.LINE: cast(msg.pop(MessageKeys.LINE, None), int),
        MessageKeys.CHAR: cast(msg.pop(MessageKeys.CHAR, None), int),
        MessageKeys.CODE: msg.pop(MessageKeys.CODE, None),
        MessageKeys.CODE_READABLE: msg.pop(MessageKeys.CODE_READABLE, None),
        MessageKeys.MESSAGE: msg.pop(MessageKeys.MESSAGE, None),
        MessageKeys.EXTENDS: task.get(Task.EXTENDS, []),
        MessageKeys.EXTRAS: [msg],
    })


def regex_line_match(regex: str) -> Converter[str, Iterator[Message]]:
    """Parse file using provided regex to extract message."""
    pattern = re.compile(regex)

    def inner(task: TTask, output: str) -> Iterator[Message]:
        for line in output.split('\n'):
            match = pattern.match(line)
            if not match:
                if line:
                    logger.warning(Format(
                        'No match for {regex} in {line}.',
                        regex=regex,
                        line=line,
                    ))
                continue
            group = match.groupdict()
            yield create_internal(task, group)
    return inner


def chain(*calls: Converter[Any, Any],
          ) -> Converter[str, Iterator[Message]]:
    """Chain multiple Converters."""
    def inner(task, output):
        for call in calls:
            output = call(task, output)
        yield from output
    return inner


def format_matches(format_string: str,
                   ) -> Converter[List[str], Iterator[Message]]:
    """Convert messages from string to dict."""
    compiled_format = None

    def inner(task: TTask, matches: List[str]) -> Iterator[Message]:
        nonlocal compiled_format
        if compiled_format is None:
            compiled_format = parse.compile(
                format_string,
                {'File': _parse_file},
            )

        for line in matches:
            match = compiled_format.parse(line.lstrip())
            if not match:
                if line:
                    logger.warning(Format(
                        'No match for {format_string} in {line}.',
                        format_string=format_string,
                        line=line,
                    ))
                continue
            yield create_internal(task, match.named)
    # TODO: figure out why mypy complains
    return inner


def extract_lines(task: TTask, output: str) -> List[str]:
    """Split output into lines."""
    return output.splitlines()


def format_line_match(format_string: str,
                      ) -> Converter[str, Iterator[Message]]:
    """Handle output which follow set format."""
    return chain(extract_lines, format_matches(format_string))


def extract_files(task: TTask, output: str) -> Iterator[str]:
    """Extract data that are grouped by file."""
    path = None
    for line in output.splitlines():
        if not line.startswith('    '):
            path = line
            continue

        yield (path or '') + ': ' + line[4:]
