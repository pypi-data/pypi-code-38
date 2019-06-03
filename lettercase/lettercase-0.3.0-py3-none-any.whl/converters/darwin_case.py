from .snake_case import darwin_to_snake_case, dromedary_to_snake_case, pascal_to_snake_case, to_snake_case

__all__ = ["dromedary_to_darwin_case", "pascal_to_darwin_case",
           "snake_to_darwin_case", "darwin_to_darwin_case",
           "to_darwin_case"]


# All implemented as x case -> snake_case -> Darwin_Case

def dromedary_to_darwin_case(text: str) -> str:
    """Convert from dromedaryCase to Darwin_Case."""
    return snake_to_darwin_case(dromedary_to_snake_case(text))


def pascal_to_darwin_case(text: str) -> str:
    """Convert PascalCase to Darwin_Case."""
    return snake_to_darwin_case(pascal_to_snake_case(text))


def snake_to_darwin_case(text: str) -> str:
    """Convert snake_case to Darwin_Case."""
    return "_".join(map(str.capitalize, text.split("_")))


def darwin_to_darwin_case(text: str) -> str:
    """Convert Darwin_Case to Darwin_Case."""
    return snake_to_darwin_case(darwin_to_snake_case(text))


def to_darwin_case(text: str) -> str:
    """Detect case and convert to Darwin_Case."""
    return snake_to_darwin_case(to_snake_case(text))
