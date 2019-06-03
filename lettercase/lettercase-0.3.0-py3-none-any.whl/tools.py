"""Utilities for making conversion easier."""

from collections import UserDict
from contextlib import suppress
from functools import wraps
from typing import Any, Iterable, Iterator, Mapping, MutableMapping, MutableSequence, Optional, Set, TypeVar, Union

from .converters import ConverterType, get_converter
from .letter_case import LetterCaseType, get_letter_case

__all__ = ["ConversionMemo", "memo_converter", "is_memo_converter",
           "convert_iter_items",
           "mut_convert_items", "mut_convert_keys"]

T = TypeVar("T")


class ConversionMemo(UserDict):
    """Mapping specialised for converter memoization.

    This is a two-way mapping so adding key: value will also add value: key.
    The consequence of this is that the `keys` and `values` methods will return
    identical sets.

    The getitem method is the same as with any normal dictionary, apart from it being two-way, but
    the `get` method automatically converts the text if it doesn't already exist.
    This can also be achieved manually using the `convert` method.

    Since this is a two-way mapping, setting a key to a value will also set the value to the key
    and deleting a key will also remove the converted key.

    Attributes:
        from_case (LetterCase): First letter case
        to_case (LetterCase): Second letter case

    Args:
        from_case (LetterCaseType): First letter case
        to_case (LetterCaseType): Second letter case

    Notes:
        The cases need to be specified because the memo cannot handle more than two cases
        at once.

        The order of the cases in the constructor matters! The order determines how
        the `direction` parameter is interpreted.
    """

    def __init__(self, from_case: LetterCaseType, to_case: LetterCaseType) -> None:
        super().__init__()
        self.from_case = get_letter_case(from_case)
        self.to_case = get_letter_case(to_case)

    def __setitem__(self, text: str, converted_text: str) -> None:
        setter = super().__setitem__
        setter(text, converted_text)
        setter(converted_text, text)

    def __delitem__(self, text: str) -> None:
        converted_text = self.__getitem__(text)
        deleter = super().__delitem__
        deleter(text)
        deleter(converted_text)

    @property
    def forward_converter(self) -> ConverterType:
        """Get the converter which converts from `from_case` to `to_case`.

        See Also:
            `forward_converter`
        """
        return get_converter(self.from_case, self.to_case)

    @property
    def backward_converter(self) -> ConverterType:
        """Get the converter which converts from `to_case` to `from_case`.

        See Also:
            `forward_converter`
        """
        return get_converter(self.to_case, self.from_case)

    def convert(self, text: str, direction: bool) -> str:
        """Convert a text and add it to the memo.

        Args:
            text: Text to convert
            direction: `True` to use `forward_converter`,
                `False` for `backward_converter`
        """
        try:
            value = self[text]
        except KeyError:
            converter = self.forward_converter if direction else self.backward_converter
            value = self[text] = converter(text)

        return value

    # noinspection PyMethodOverriding
    def get(self, text: str, *, direction: bool = None, default: T = None) -> Optional[Union[str, T]]:
        """Get the converted text.

        Args:
            text: Text to get the converted text for.
            direction: See `convert` for an explanation of this keyword argument.
                If you pass `None` instead of a `bool`, the text will not be converted
                if it does not exist and the `default` value is used.
            default: Value to return when the text is not
                in the memo and `convert` is `False`.
                If `convert` is `True`, this value will never
                be returned.
        """
        try:
            return self[text]
        except KeyError:
            if direction is not None:
                return self.convert(text, direction)

            return default


MEMO_CONVERTER_FLAG = "__memoized__"


def memo_converter(converter: ConverterType, memo: Union[Mapping[str, str], MutableMapping[str, str]]) -> ConverterType:
    """Decorator which adds memoization to a converter.

    Args:
        converter: Converter to patch
        memo: Memoization mapping to use. If the mapping is mutable it will automatically be updated with new keys.

    Examples:
        >>> memo_data = {}
        >>> converter = memo_converter(get_converter("snake", "dromedary"), memo_data)
        >>> print(converter("snake_test"))
        snakeTest
        >>> print(memo_data)
        {'snake_test': 'snakeTest'}
    """

    @wraps(converter)
    def wrapper(text: str) -> str:
        try:
            return memo[text]
        except KeyError:
            pass

        new_text = converter(text)

        with suppress(Exception):
            memo[text] = new_text

        return new_text

    setattr(wrapper, MEMO_CONVERTER_FLAG, True)

    return wrapper


def is_memo_converter(converter: ConverterType) -> bool:
    """Check if a converter is memoized using `memo_converter`.

    Args:
        converter: Converter to check

    Returns:
        `True` if the converter is memoized, `False` otherwise.
    """
    return getattr(converter, MEMO_CONVERTER_FLAG, False)


def _get_converter(from_case: Optional[LetterCaseType], to_case: LetterCaseType,
                   memo: Optional[Mapping[str, str]]) -> ConverterType:
    """Internal utility function to get a patched converter.

    Raises:
        ValueError: If no converter was found from `from_case` to `to_case`
    """
    converter = get_converter(from_case, to_case)
    if not converter:
        if from_case:
            text = f"No converter for {from_case} -> {to_case}"
        else:
            text = f"No general converter to {to_case}"

        raise ValueError(text)

    if memo is not None:
        converter = memo_converter(converter, memo)

    return converter


def convert_iter_items(iterable: Iterable[str], from_case: Optional[LetterCaseType], to_case: LetterCaseType, *,
                       memo: Mapping[str, str] = None) -> Iterator[str]:
    """Patch an iterable so that all items are converted to the case.

    Args:
        iterable: Iterable to convert
        from_case: `LetterCase` to convert from, passing `None` will use a general converter.
        to_case: `LetterCase` to convert to
        memo: Memoization mapping to make conversion faster.
    """
    converter = _get_converter(from_case, to_case, memo)
    return map(converter, iterable)


def mut_convert_items(seq: MutableSequence[str], from_case: Optional[LetterCaseType], to_case: LetterCaseType, *,
                      memo: Mapping[str, str] = None) -> None:
    """Convert all items in a mutable sequence to the given case."""
    converter = _get_converter(from_case, to_case, memo)

    for i, item in enumerate(seq):
        new_item = converter(item)
        if new_item != item:
            seq[i] = new_item


def mut_convert_keys(mapping: MutableMapping[str, Any], from_case: Optional[LetterCaseType], to_case: LetterCaseType, *,
                     memo: Mapping[str, str] = None) -> None:
    """Convert all keys in a mutable mapping to the given case.

    Args:
        mapping: Mapping whose keys are to be converted
        from_case: Specify the case to convert from. If not provided a general converter is used.
        to_case: `LetterCase` to convert to
        memo: Memoization map to use.
    """
    converter = _get_converter(from_case, to_case, memo)

    original_keys: Set[str] = set(mapping.keys())

    for key in original_keys:
        new_key = converter(key)
        if new_key != key:
            mapping[new_key] = mapping.pop(key)
