from typing import Iterable
from .utils import (
    is_empty,
    is_char_hiragana,
    is_char_katakana,
    is_char_japanese,
    is_char_kana,
    is_char_kanji,
    is_char_romaji,
)


def is_hiragana(input: str = "") -> bool:
    """Tests if `input` is Hiragana"""
    return (not is_empty(input)) and all(is_char_hiragana(char) for char in input)


def is_katakana(input: str = "") -> bool:
    """Tests if `input` is Katakana"""
    return (not is_empty(input)) and all(is_char_katakana(char) for char in input)


def is_japanese(input: str = "", augmented: Iterable = None) -> bool:
    """Tests if `input` includes only Kanji, Kana, zenkaku numbers, and
    JA punctuation/symbols"""
    return (not is_empty(input)) and all(
        is_char_japanese(char) or (augmented and char in augmented) for char in input
    )


def is_kana(input: str = "") -> bool:
    """Tests if `input` is Kana (Katakana and/or Hiragana)"""
    return (not is_empty(input)) and all(is_char_kana(char) for char in input)


def is_kanji(input: str = "") -> bool:
    """Tests if `input` is Kanji (Japanese CJK Ideographs)"""
    return (not is_empty(input)) and all(is_char_kanji(char) for char in input)


def is_mixed(input: str = "", ignore_kanji: bool = True) -> bool:
    """Tests if `input` contains a mix of Romaji *and* Kana, ignoring Kanji by default"""
    return (
        (not is_empty(input))
        and any(is_char_kana(char) for char in input)
        and any(is_char_romaji)
        and (ignore_kanji or not any(is_char_kanji(char) for char in input))
    )


def is_romaji(input: str = "", augmented: Iterable = None) -> bool:
    """Tests if `input` includes only Romaji characters (allowing Hepburn romanisation)"""
    return (not is_empty(input)) and all(
        is_char_romaji(char) or (augmented and char in augmented) for char in input
    )
