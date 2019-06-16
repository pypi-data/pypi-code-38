"""Handle nosa comments."""

from __future__ import annotations

import itertools
import logging
import operator
import re
import tokenize
from typing import Any, Iterator, List, Optional, Tuple

from ...core.objects import Format, LESS, Less, Message

# nosa(2): pylint[C0103]
_get_path = operator.attrgetter('path')
logger = logging.getLogger(__name__)


class Position:
    """Position states."""

    PREV = object()
    NEXT = object()
    NEXT_ORIG = object()


class Scope:
    """Scope states."""

    COMMENT = object()
    DEFINITION = object()
    EMPTY_LINE = object()


SCOPE_TO_POSITION = {
    Scope.COMMENT: Position.NEXT,
    Scope.DEFINITION: Position.NEXT,
    Scope.EMPTY_LINE: Position.NEXT_ORIG,
}
TokenPosition = Tuple[int, tokenize.TokenInfo]
Scoped = Tuple[object, List[tokenize.TokenInfo]]


def _convert_scope(queue: List[Scoped],
                   comment_global: bool = True,
                   ) -> Iterator[Scoped]:
    """Convert from Scope to Position."""
    for i, (type_, values) in enumerate(queue):
        if (comment_global
            and type_ is Scope.COMMENT
            and any(Scope.DEFINITION == t for t, _ in queue[i:])
        ):
            yield Position.NEXT_ORIG, values
        else:
            yield SCOPE_TO_POSITION[type_], values


def handle_queue(queue: List[Scoped],
                 scope: int,
                 prev: int,
                 prev_orig: int,
                 ) -> Iterator[TokenPosition]:
    """Handle queue."""
    place = {
        Position.PREV: prev,
        Position.NEXT: scope,
        Position.NEXT_ORIG: prev_orig,
    }
    for position, values in _convert_scope(queue):
        pos = place[position]
        for value in values:
            yield (pos, value)


def _with_scope(tokens: Iterator[tokenize.TokenInfo],
                ) -> Iterator[TokenPosition]:
    """Add scope to tokens."""
    queue: List[Scoped] = []
    prev = 1
    prev_orig = 1
    for line, values in itertools.groupby(tokens, lambda i: i.line):
        striped_line = line.lstrip(' ')
        if striped_line.startswith('#'):
            queue.append((Scope.COMMENT, list(values)))
        elif not line.strip():
            queue.append((Scope.EMPTY_LINE, list(values)))
        elif (striped_line.startswith('def')
              or striped_line.startswith('class')
        ):
            queue.append((Scope.DEFINITION, list(values)))
            prev_orig = len(line) - len(striped_line) + 1
        else:
            scope = len(line) - len(striped_line) + 1
            yield from handle_queue(queue, scope, prev, prev_orig)
            for value in values:
                yield (scope, value)
            queue = []
            prev = prev_orig = scope

    if queue:
        yield from handle_queue(queue, 1, prev, prev_orig)


TOKEN_EMPTY = {
    tokenize.NEWLINE,
    tokenize.NL,
    tokenize.DEDENT,
    tokenize.INDENT,
}


TScope = Tuple[int, List]


# nosa: flake8-annotations-complexity[TAE002]
def _find_nosa(path: str) -> Iterator[Tuple[str, bool, int, Tuple[int, int]]]:
    """Find NOSA in path."""
    if path is LESS:
        return
    # Test
    scopes: List[TScope] = [(-1, [])]
    line_no = 0
    with open(path, 'rb') as file:
        prev = None
        tokens = _with_scope(tokenize.tokenize(file.readline))
        for spaces, (token_type, value, (line_no, _), _, _) in tokens:
            if spaces > len(scopes):
                for _ in range(spaces - len(scopes)):
                    scopes.append((line_no, []))
            elif spaces < len(scopes):
                for beginning, scope in scopes[spaces:]:
                    for nosa, nosa_type, location in scope:
                        yield nosa, nosa_type, location, (beginning, line_no)
                del scopes[spaces:]

            if token_type == tokenize.COMMENT:
                nosa_type = prev in TOKEN_EMPTY
                scopes[-1][1].append((value, nosa_type, line_no))
            else:
                prev = token_type
    for beginning, scope in scopes:
        for nosa, nosa_type, location in scope:
            yield nosa, nosa_type, location, (beginning, line_no)


class ErrorValue:
    """NOSA error values."""

    def __init__(self, code: str, message: str) -> None:
        """Initialize ErrorValue."""
        self.code = code
        self.message = message

    def __str__(self) -> str:
        """Convert into string form."""
        output = str(self.code)
        if self.message:
            output += ':' + self.message
        return output

    def __contains__(self, item: Message):
        """Check item contains the code and/or message."""
        if self.code and not isinstance(item.code, Less):
            if not item.code.startswith(self.code):
                return False
        if self.message and not isinstance(item.message, Less):
            if self.message not in item.message:
                return False
        return True

    @classmethod
    def from_string(cls, value: str) -> ErrorValue:
        """Build from string form."""
        code, message, *_ = value.split(':') + ['']
        return cls(code, message)


class Error:
    """Contain program and values of NOSA comments."""

    def __init__(self, programs: List[str], values: List[ErrorValue]) -> None:
        """Initialize Error."""
        self.programs = programs
        self.values = values

    def __str__(self) -> str:
        """Convert into non-ambiguous string form."""
        programs = ','.join(self.programs)
        programs = f'({programs})'
        values = ','.join(str(v) for v in self.values)
        values = f'[{values}]'
        return programs + values

    def __contains__(self, item: Message):
        """Check if item is applicable program with value."""
        if self.programs and item.app is not LESS:
            if item.app not in self.programs:
                return False
        if self.values:
            if not any(item in value for value in self.values):
                return False
        return True

    @classmethod
    def from_string(cls, error: str) -> Error:
        """Build from string form."""
        start, end, *_ = error.split('[', 1) + ['']
        if start.startswith('('):
            start = start[1:-1]
        elif not end:
            end = start + ']'
            start = ''
        if start:
            start_ = start.split(',')
        else:
            start_ = []
        if end:
            end = end[:-1]
        return cls(
            start_,
            [
                ErrorValue.from_string(e)
                for e in end.split(',')
            ],
        )


class State:
    """Error parsing states."""

    GLOBAL = object()
    BRACKET = object()


class Errors:
    """Errors holder."""

    def __init__(self, errors: List[Error]) -> None:
        """Initialize Errors."""
        self.errors = errors

    def __str__(self):
        """Convert to string form."""
        return ','.join(str(e) for e in self.errors)

    def __contains__(self, item: Message):
        """Check if contains error."""
        return any(item in error for error in self.errors)

    def __len__(self):
        """Amount of errors."""
        return len(self.errors)

    @staticmethod
    def _split_top_level_errors(errors):
        """Split sub-errors."""
        if errors is None:
            return []
        split_errors = []
        name = []
        state = State.GLOBAL
        for char in errors:
            if char in ' ' and state is State.GLOBAL:
                break
            elif char in '([':
                name.append(char)
                state = State.BRACKET
            elif char in '])':
                name.append(char)
                state = State.GLOBAL
            elif char == ',' and state is State.GLOBAL:
                split_errors.append(''.join(name))
                name = []
            else:
                name.append(char)
        if name:
            split_errors.append(''.join(name))
        return split_errors

    @classmethod
    def from_string(cls, errors: str) -> Errors:
        """Build Errors from string form."""
        return cls([
            Error.from_string(error)
            for error in cls._split_top_level_errors(errors)
        ])


class NOSA:
    """NOSA comment."""

    def __init__(self, name: str, stop: int, start: int, errors: Errors):
        """Initialize NOSA."""
        self.name = name
        self.start = start
        self.stop = stop
        self.errors = errors

    def __str__(self):
        """Build string."""
        ret = f'{self.name}({self.start}->{self.stop})'
        if self.errors:
            ret += f': {self.errors}'
        return ret

    def __contains__(self, item: Message):
        """Check if message should be silenced."""
        if (not isinstance(item.line, Less)
            and not self.start <= int(item.line) <= self.stop
        ):
            return False
        return item in self.errors

    # nosa(2): pylint[R0913]
    @classmethod
    def from_comment(cls,
                     string: str,
                     type_: bool,
                     location: int,
                     start: int,  # nosa: pylint[W0613]
                     stop: int,
                     *,
                     _nosa: str = 'nosa',
                     ) -> Optional[NOSA]:
        """Build NOSA from string."""
        if _nosa not in string:
            return None
        regex = '(' + _nosa + r')(?:\((\d*)(?:,(\d*))?\))?(?:: (.*))?'
        match = re.search(regex, string)
        if match is None:
            return None
        groups: List[Any] = list(match.groups())
        if groups[1] == '' or groups[1] is None:
            groups[1] = stop if type_ else location
        else:
            groups[1] = location + int(groups[1])
        if groups[2] == '' or groups[2] is None:
            groups[2] = location
        else:
            groups[2] = location - int(groups[2])
        if groups[3] == '':
            groups[3] = None
        if groups[3]:
            groups[3] = Errors.from_string(groups[3])
        return cls(*groups)


def _filter_nosa(comments, _nosa='nosa'):
    """Filter all comments to ones that are nosa."""
    for comment, type_, location, (start, stop) in comments:
        nosa = NOSA.from_comment(
            comment,
            type_,
            location,
            start,
            stop,
            _nosa=_nosa,
        )
        if nosa is not None:
            yield nosa


def remove_nosa(objects):
    """Remove errors in accordance to nosa."""
    for path, group in itertools.groupby(objects, _get_path):
        nosas = list(_filter_nosa(_find_nosa(path)))
        unused = [True] * len(nosas)
        for item in group:
            unmuted = True
            for i, nosa in enumerate(nosas):
                if item in nosa:
                    unused[i] = False
                    unmuted = False
            if unmuted:
                yield item
        for nosa in itertools.compress(nosas, unused):
            logger.info(Format('Unused nosa: {0!s}', nosa))
