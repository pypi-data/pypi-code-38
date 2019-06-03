"""Letter case detection."""

from typing import Iterator, Set

from .letter_case import CAMEL_CASE, LetterCase

_all__ = ["detect_case"]


def detect_case(text: str, fast_return: bool = True, *, ignore_space: bool = True) -> Set[LetterCase]:
    """Determine the `LetterCase` of a word.

    Leading underscores are ignored in order to support
    "private" names. If the text includes a non-alphanummeric
    character the empty set is returned.

    Args:
      text: String to analyze
      fast_return: When set to `False` the function is forced
        to analyse the entire string. By default it continues
        until the result is either specifically determined, or
        the text runs out.
      ignore_space: When set to `False` the function no longer
        ignores spaces in the text and instead treats them
        like a normal character which leads to an empty set
        being returned.
    """
    # noinspection PyTypeChecker
    possible = set(iter(LetterCase))
    char_iter: Iterator[str] = iter(text)

    prev_is_underscore: bool = False
    found_alnum: bool = False

    while len(possible) > 1 or not fast_return:
        try:
            char = next(char_iter)
        except StopIteration:
            break

        is_underscore: bool = False

        if char.isalnum():
            if char.isupper():
                possible.discard(LetterCase.SNAKE)

                if not found_alnum:
                    possible.discard(LetterCase.DROMEDARY)
                elif not prev_is_underscore:
                    possible.discard(LetterCase.DARWIN)
            else:
                possible.discard(LetterCase.SCREAMING_SNAKE)

                if not found_alnum:
                    possible.discard(LetterCase.PASCAL)
                    possible.discard(LetterCase.DARWIN)

                if prev_is_underscore:
                    possible.discard(LetterCase.DARWIN)

            found_alnum = True
        elif char == "_":
            if found_alnum:
                possible -= CAMEL_CASE

            is_underscore = True
        elif char.isspace() and ignore_space:
            pass
        else:
            return set()

        prev_is_underscore = is_underscore

    return possible
