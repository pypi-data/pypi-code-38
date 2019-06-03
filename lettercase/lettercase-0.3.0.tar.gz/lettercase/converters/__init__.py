"""Specific converters between cases."""
from functools import lru_cache
from typing import Callable, Optional

from lettercase import LetterCaseType, get_letter_case
from . import darwin_case, dromedary_case, pascal_case, screaming_snake_case, snake_case
from .darwin_case import *
from .dromedary_case import *
from .pascal_case import *
from .screaming_snake_case import *
from .snake_case import *

__all__ = ["ConverterType", "get_converter", "convert_to",
           *darwin_case.__all__,
           *dromedary_case.__all__,
           *pascal_case.__all__,
           *screaming_snake_case.__all__,
           *snake_case.__all__]

ConverterType = Callable[[str], str]


@lru_cache(maxsize=None)
def get_converter(from_case: Optional[LetterCaseType], to_case: LetterCaseType) -> Optional[ConverterType]:
    """Find a converter which converts between the given cases.

    This function uses an LRU cache to speed up the lookup process.

    The arguments are looked up using `get_letter_case`, so you may pass all values
    supported by it.

    Args:
        from_case: `LetterCase` of the original text. If `None` a generic handler will be searched.
        to_case: Target `LetterCase`
    """
    to_case = get_letter_case(to_case)

    name = f"to_{to_case.name.lower()}_case"

    if from_case is not None:
        from_case = get_letter_case(from_case)
        name = f"{from_case.name.lower()}_{name}"

    return globals().get(name)


def convert_to(text: str, case: LetterCaseType) -> Optional[str]:
    """Convert the given text to the case.

    Args:
        text: Text to convert
        case: `LetterCase` to convert to
    """
    case = get_letter_case(case)

    converter = get_converter(None, case)
    if converter:
        return converter(text)

    return None
