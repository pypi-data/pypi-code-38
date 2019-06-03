from collections import deque
from typing import Deque

from lettercase import LetterCase, detect_case
from .dromedary_case import pascal_to_dromedary_case

__all__ = ["dromedary_to_snake_case", "pascal_to_snake_case", "screaming_snake_to_snake_case", "darwin_to_snake_case", "to_snake_case"]


def dromedary_to_snake_case(text: str) -> str:
    """Convert from dromedaryCase to snake_case.

    If there is a space just before it, no underscore
    will be used, however, the character will still be
    lowercase ("hello World" -> "hello world").
    """
    if not text:
        return text

    chars: Deque[str] = deque()
    next_is_upper: bool = False

    for i in range(len(text) - 1, -1, -1):
        char = text[i]
        if char.isupper():
            char = char.lower()
            if not next_is_upper:
                next_is_upper = True
        else:
            if next_is_upper and not char.isspace():
                chars.appendleft("_")

            next_is_upper = False

        chars.appendleft(char)

    return "".join(chars)


def pascal_to_snake_case(text: str) -> str:
    """Convert PascalCase to snake_case."""
    return dromedary_to_snake_case(pascal_to_dromedary_case(text))


def screaming_snake_to_snake_case(text: str) -> str:
    """Convert SCREAMING_SNAKE_CASE to snake_case."""
    return text.lower()


def darwin_to_snake_case(text: str) -> str:
    """Convert Darwin_Case to snake_case."""
    return screaming_snake_to_snake_case(text)


def to_snake_case(text: str) -> str:
    """Detect case and convert to snake_case."""
    possible = detect_case(text)

    if not possible:
        raise TypeError(f"Unsupported letter case: {text}")

    if LetterCase.SNAKE in possible:
        return text

    if LetterCase.SCREAMING_SNAKE in possible:
        return screaming_snake_to_snake_case(text)

    if LetterCase.DARWIN in possible:
        return darwin_to_snake_case(text)

    if LetterCase.DROMEDARY in possible:
        return dromedary_to_snake_case(text)

    if LetterCase.PASCAL in possible:
        return pascal_to_snake_case(text)

    raise TypeError(f"Cannot convert any of {possible} to snake_case")
