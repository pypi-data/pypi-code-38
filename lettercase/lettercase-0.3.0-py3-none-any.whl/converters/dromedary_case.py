from typing import List

from lettercase import LetterCase, detect_case

__all__ = ["snake_to_dromedary_case", "screaming_snake_to_dromedary_case", "darwin_to_dromedary_case",
           "pascal_to_dromedary_case",
           "to_dromedary_case"]


def snake_to_dromedary_case(text: str) -> str:
    """Convert from snake_case to dromedaryCase."""
    if not text:
        return text

    chars: List[str] = []
    next_is_upper: bool = False
    letter_seen: bool = False

    for c in text:
        if c == "_":
            if letter_seen:
                next_is_upper = True
                continue
        elif c.isalpha():
            letter_seen = True

            if next_is_upper:
                c = c.upper()
                next_is_upper = False

        chars.append(c)

    return "".join(chars)


def screaming_snake_to_dromedary_case(text: str) -> str:
    """Convert from SCREAMING_SNAKE_CASE to dromedaryCase."""
    from .snake_case import screaming_snake_to_snake_case
    return snake_to_dromedary_case(screaming_snake_to_snake_case(text))


def darwin_to_dromedary_case(text: str) -> str:
    """Convert from Darwin_Case to dromedaryCase."""
    from .snake_case import darwin_to_snake_case
    return snake_to_dromedary_case(darwin_to_snake_case(text))


def pascal_to_dromedary_case(text: str) -> str:
    """Convert from PascalCase to dromedaryCase."""
    chars: List[str] = []
    found_alnum: bool = False

    for char in text:
        if not found_alnum and char.isalnum():
            char = char.lower()
            found_alnum = True

        chars.append(char)

    return "".join(chars)


def to_dromedary_case(text: str) -> str:
    """Detect case and convert to dromedaryCase."""
    possible = detect_case(text)

    if not possible:
        raise TypeError(f"Unsupported letter case: {text}")

    if LetterCase.DROMEDARY in possible:
        return text

    if LetterCase.SNAKE in possible:
        return snake_to_dromedary_case(text)
    if LetterCase.SCREAMING_SNAKE in possible:
        return screaming_snake_to_dromedary_case(text)
    if LetterCase.DARWIN in possible:
        return darwin_to_dromedary_case(text)

    if LetterCase.PASCAL in possible:
        return pascal_to_dromedary_case(text)

    raise TypeError(f"Cannot convert any of {possible} to dromedaryCase")
