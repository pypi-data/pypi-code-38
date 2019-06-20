import re
from typing import Iterator, Match, NewType, Tuple

from .metadata import NAME, VERSION

Flake8Message = NewType("Flake8Message", str)
Flake8Result = NewType("Flake8Result", Tuple[int, Flake8Message])


# Find any TODOs
RX_TODO = re.compile(r"\bTODO\b")
# Find only a correctly formatted todo
RX_TODO_NAME_TICKET = re.compile(r"\bTODO\([a-zA-Z0-9_]+\)\[\d+\]")


def is_incorrect_todo(todo_match: Match[str]) -> bool:
    # truncate original line to start of match
    # if matches correct pattern at start of line
    # return False
    # otherwise, return True (may be other corredct matches after this one)
    start_at_todo = todo_match.string[todo_match.start() :]
    match = RX_TODO_NAME_TICKET.match(start_at_todo)
    return not bool(match)


def match_to_flake8_result(match: Match[str]) -> Flake8Result:
    result = Flake8Result(
        (
            match.start(),
            Flake8Message(
                "T400 Badly formatted TODO. Use TODO(name)[ticket_number]"  # noqa: T400
            ),
        )
    )
    return result


def check(physical_line: str) -> Iterator[Flake8Result]:
    todos = RX_TODO.finditer(physical_line)
    incorrect_todos = filter(is_incorrect_todo, todos)
    results = map(match_to_flake8_result, incorrect_todos)
    yield from results


check.name = NAME  # type: ignore
check.version = VERSION  # type: ignore
