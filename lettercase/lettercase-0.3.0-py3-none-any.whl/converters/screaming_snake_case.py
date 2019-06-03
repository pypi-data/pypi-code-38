from .snake_case import darwin_to_snake_case, dromedary_to_snake_case, pascal_to_snake_case, to_snake_case

__all__ = ["dromedary_to_screaming_snake_case", "pascal_to_screaming_snake_case",
           "snake_to_screaming_snake_case", "darwin_to_screaming_snake_case",
           "to_screaming_snake_case"]


# All implemented as x case -> snake_case -> SCREAMING_SNAKE_CASE

def dromedary_to_screaming_snake_case(text: str) -> str:
    """Convert from dromedaryCase to SCREAMING_SNAKE_CASE."""
    return snake_to_screaming_snake_case(dromedary_to_snake_case(text))


def pascal_to_screaming_snake_case(text: str) -> str:
    """Convert PascalCase to SCREAMING_SNAKE_CASE."""
    return snake_to_screaming_snake_case(pascal_to_snake_case(text))


def snake_to_screaming_snake_case(text: str) -> str:
    """Convert snake_case to SCREAMING_SNAKE_CASE."""
    return text.upper()


def darwin_to_screaming_snake_case(text: str) -> str:
    """Convert Darwin_Case to SCREAMING_SNAKE_CASE."""
    return snake_to_screaming_snake_case(darwin_to_snake_case(text))


def to_screaming_snake_case(text: str) -> str:
    """Detect case and convert to SCREAMING_SNAKE_CASE."""
    return snake_to_screaming_snake_case(to_snake_case(text))
