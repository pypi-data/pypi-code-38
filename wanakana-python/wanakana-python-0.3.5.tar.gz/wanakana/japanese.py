import re
from typing import List, Union
from .common import (
    is_japanese,
    is_kana,
    is_kanji,
    tokenise,
    is_char_kana,
    is_char_kanji,
)
from .constants import TO_KANA_METHODS
from .utils import (
    get_romaji_to_kana_tree,
    USE_OBSOLETE_KANA_MAP,
    apply_mapping,
    merge_custom_mapping,
    is_char_uppercase,
    hiragana_to_katakana,
)

is_leading_without_initial_kana = lambda input, leading: leading and (
    not is_kana(input[0])
)
is_trailing_without_final_kana = lambda input, leading: (not leading) and (
    not is_char_kana(input[-1])
)
is_invalid_matcher = lambda input, match_kanji: (
    match_kanji and (not any(is_char_kanji for char in match_kanji))
) or ((not match_kanji) and is_kana(input))


def strip_okurigana(
    input: str = "", leading: bool = False, match_kanji: str = ""
) -> str:
    """Strips Okurigana. If `leading` is set, okurigana will be stripped from the
    beginning instead of the end. If `match_kanji` is set, the input will be treated as
    furigana, and the result will be kana"""
    if (
        (not is_japanese(input))
        or is_leading_without_initial_kana(input, leading)
        or is_trailing_without_final_kana(input, leading)
        or is_invalid_matcher(input, match_kanji)
    ):
        return input
    chars = match_kanji or input
    okurigana_regex = re.compile(
        f"^{tokenise(chars).pop(0)}" if leading else f"{tokenise(chars).pop()}$"
    )
    return okurigana_regex.sub("", input)


custom_mapping = None


def create_romaji_to_kana_map(
    use_obsolete_kana: bool = False, custom_kana_mapping: dict = None
) -> dict:
    map = get_romaji_to_kana_tree()
    global custom_mapping

    map = USE_OBSOLETE_KANA_MAP(map) if use_obsolete_kana else map

    if custom_kana_mapping:
        if not custom_mapping:
            custom_mapping = merge_custom_mapping(map)
        map = custom_mapping

    return map


def _split_into_converted_kana(
    input: str = "",
    use_obsolete_kana: bool = False,
    custom_kana_mapping: dict = None,
    convert_ending: bool = True,
    map: dict = None,
) -> List[List[int, int, str]]:
    if not map:
        map = create_romaji_to_kana_map(
            use_obsolete_kana=use_obsolete_kana, custom_kana_mapping=custom_kana_mapping
        )

    return apply_mapping(input.lower(), map, convert_ending)


def to_kana(
    input: str = "",
    use_obsolete_kana: bool = False,
    custom_kana_mapping: dict = None,
    convert_ending: bool = True,
    full_map: dict = None,
    enforce: Union[None, "hira", "kata"] = None,
) -> str:
    """Converts Romaji to Kana, lowercase will become Hiragana and uppercase will
    become Katakana"""
    if enforce not in [None, "hira", "kata"]:
        enforce = None
    if not full_map:
        kana_map = create_romaji_to_kana_map(
            use_obsolete_kana=use_obsolete_kana, custom_kana_mapping=custom_kana_mapping
        )

    def _process(kana_token: List[int, int, str]) -> str:
        start, end, kana = kana_token
        if not kana:
            # we didn't convert the end of the string
            return input[start:]
        enforce_hiragana = enforce == "hira"
        enforce_katakana = enforce == "kata" or all(
            is_char_uppercase(char) for char in input[start:end]
        )

        return (
            kana
            if enforce_hiragana or (not enforce_katakana)
            else hiragana_to_katakana(kana)
        )

    return "".join(
        map(
            _process,
            _split_into_converted_kana(
                input,
                use_obsolete_kana=use_obsolete_kana,
                custom_kana_mapping=custom_kana_mapping,
                convert_ending=convert_ending,
                map=kana_map,
            ),
        )
    )
