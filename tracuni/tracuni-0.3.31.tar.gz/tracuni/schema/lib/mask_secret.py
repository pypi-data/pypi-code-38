import json
import re
from urllib.parse import unquote
from math import fabs
from typing import Sequence

from tracuni.define.const import (
    MASK_PARAMS,
    MASK_PARAMS_PARTIALLY,
    MASK_CHAR,
    MASK_CHAR_PARTIALLY,
    TAG_ESSENTIAL_FIELD_NAMES,
)

essential_target_names = dict(
    (key.lower(), keys[0])
    for keys in [
        key_or_keys if isinstance(key_or_keys, Sequence) and not isinstance(key_or_keys, str) else (key_or_keys,)
        for key_or_keys in TAG_ESSENTIAL_FIELD_NAMES
    ]
    for key in keys
)
essential_keys_to_find = set(essential_target_names.keys())


def mask_partial(row, symbol=MASK_CHAR_PARTIALLY, from_idx=4, to_idx=-4):
    """
    Частичное экранирование строки
    :param row: строка для экранирования
    :param symbol: экранирующий символ
    :param from_idx: стартовая позиция маски
    :param to_idx: конечная позиция маски
    :return:
    """
    row = str(row)
    mask_len = round(len(row) - fabs(from_idx) - fabs(to_idx))
    masked_row = row[:from_idx] + mask_len * symbol + row[to_idx:]
    return masked_row


def mask_full(row, symbol=MASK_CHAR):
    """
    Полное экранирование строки
    :param row: строка
    :param symbol: экранирующий символ
    :return:
    """
    row = str(row)
    masked_row = symbol * len(row)
    return masked_row


def replace_fn(match_obj):
    """
        Пробуем сохранитьб валидный JSON:
            * Если мы число поменяли на строку, оборачиваем в кавычки
            * Если у нас были параметры запроса внутри строки, то возвращаем
            хвостовую кавычку
    :param match_obj:
    :return:
    """
    global collected_essentials
    groups = match_obj.groups()
    start_quote = groups[0]
    keyword = groups[1].lower()
    separator_n_quotes = groups[2] or groups[5]
    value = groups[4] or groups[6]
    value_quotes = groups[3] or ''

    if keyword in MASK_PARAMS:
        if keyword in MASK_PARAMS_PARTIALLY:
            mask_fn = mask_partial
        else:
            mask_fn = mask_full
        masked = mask_fn(value)

    else:
        if '\\' in value_quotes:
            value = value[:-2]
        collected_essentials['data.' + essential_target_names[keyword]] = value
        masked = value if value is not None else ''

    return f'{start_quote}{keyword}{separator_n_quotes}{value_quotes}{masked}{value_quotes}'


def prepare_pattern():
    kwords = r'|'.join(MASK_PARAMS | essential_keys_to_find)
    start_quotes = r'[<"&\?]'
    opt_quotes = r'\\?"?'
    opt_space = r'\s*'
    # https://stackoverflow.com/questions/5695240/php-regex-to-ignore-escaped-quotes-within-quotes
    content = r'[^"\\,}}{}]*(?:\\.[^"\\,}}{}]*)*'

    # выцепляет ключи, если они встречаются как ключи в сериализованном JSON:
    #     "{"secret_key": ..., ...}"
    # или если они встречают в JSON, вложенных как экранированные строковые значения:
    #     "{"NON_secret_key": "{\"secret_key\": ...}", ...}"
    # впрочем, так тоже можно:
    #     "{"secret_key": "{\"secret_key\": ...}", ...}"
    content_dict = content.format(*("<",) * 2)
    dict_value = f'({opt_quotes}{opt_space}[:>]{opt_space})({opt_quotes})({content_dict}){opt_quotes}'
    # capture:     ^2=separator & quotes                ^3=quotes     ^4=value

    # выцепляет ключи, если они встречаются как парметры URL запроса внутри JSON значения:
    # {"url_key": "...secret_key=abc&..."}
    content_url = content.format(*("&",)*2)
    url_param = f'({opt_space}={opt_space})({content_url})'
    # capture:    ^5=separator & quotes    ^6=value

    compiled_pattern = re.compile(
        f'({start_quotes})[^/]?({kwords})(?:{dict_value}|{url_param})',
        # ^0=open quote   ^1=keys   ^2-6=see above      : capture
        re.M | re.S | re.I
    )

    return compiled_pattern


pattern = prepare_pattern()
collected_essentials = {}


def do(data):
    global collected_essentials
    collected_essentials = {}
    try:
        data = json.dumps(json.loads(data))
    except (TypeError, json.JSONDecodeError):
        pass
    try:
        data = unquote(data)
    except TypeError:
        pass
    data = pattern.sub(replace_fn, str(data))
    return data, collected_essentials
