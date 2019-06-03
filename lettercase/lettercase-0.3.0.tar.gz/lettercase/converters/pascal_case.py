from typing import List

from .dromedary_case import darwin_to_dromedary_case, screaming_snake_to_dromedary_case, snake_to_dromedary_case, \
    to_dromedary_case

__all__ = ["dromedary_to_pascal_case", "screaming_to_pascal_case", "snake_to_pascal_case",
           "darwin_to_pascal_case", "to_pascal_case"]


# All implemented as x case -> dromedaryCase -> PascalCase

def dromedary_to_pascal_case(text: str) -> str:
    """Convert from dromedaryCase to PascalCase."""
    characters: List[str] = []
    letter_seen = False

    for char in text:
        if not letter_seen and char.isalpha():
            letter_seen = True
            characters.append(char.upper())
        else:
            characters.append(char)

    return "".join(characters)


def screaming_to_pascal_case(text: str) -> str:
    """Convert SCREAMING_SNAKE_CASE to PascalCase."""
    return dromedary_to_pascal_case(screaming_snake_to_dromedary_case(text))


def snake_to_pascal_case(text: str) -> str:
    """Convert snake_case to PascalCase."""
    return dromedary_to_pascal_case(snake_to_dromedary_case(text))


def darwin_to_pascal_case(text: str) -> str:
    """Convert Darwin_Case to PascalCase."""
    return dromedary_to_pascal_case(darwin_to_dromedary_case(text))


def to_pascal_case(text: str) -> str:
    """Detect case and convert to PascalCase."""
    return snake_to_pascal_case(to_dromedary_case(text))
