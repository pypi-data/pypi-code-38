from enum import Enum
from typing import Set, Union

__all__ = ["LetterCase", "CAMEL_CASE", "UNDERSCORE_CASE", "LetterCaseType", "get_letter_case"]


class LetterCase(Enum):
    """Supported letter cases.

    - snake_case
    - SCREAMING_SNAKE_CASE
    - Darwin_Case
    - PascalCase
    - dromedaryCase
    """
    SNAKE = "snake"
    SCREAMING_SNAKE = "screaming_snake"
    DARWIN = "darwin"

    PASCAL = "pascal"
    DROMEDARY = "dromedary"


CAMEL_CASE: Set[LetterCase] = {LetterCase.PASCAL, LetterCase.DROMEDARY}

UNDERSCORE_CASE: Set[LetterCase] = {LetterCase.SNAKE, LetterCase.SCREAMING_SNAKE, LetterCase.DARWIN}

LetterCaseType = Union[LetterCase, str]


def get_letter_case(case: LetterCaseType) -> LetterCase:
    """Get a `LetterCase` from `LetterCaseType`.

    Args:
        case: `LetterCase` specification.
            This can either be a `LetterCase` or a string.
            If it is a string, it has to be the name of a case
            (strings are converted to lowercase, so it's case-insensitive).
            "_case" is stripped from the string, so snake_case will resolve to
            snake which will then resolve to `LetterCase.SNAKE`

    Raises:
        ValueError: If the passed value is invalid and cannot be resolved to
            `LetterCase`
        TypeError: If something other than `LetterCaseType` is passed
    """
    try:
        return LetterCase(case)
    except ValueError:
        pass

    if not isinstance(case, str):
        raise TypeError(f"Type {type(case).__name__} can not be used as a LetterCase")

    cleaned_case = case.lower()
    cleaned_case = cleaned_case.partition("_case")[0]

    return LetterCase(cleaned_case)
