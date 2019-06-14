import re
from typing import (
    Sequence,
    Dict,
)

from tracuni.define.const import (
    TAG_ESSENTIAL_FIELD_NAMES,
    TAG_ESSENTIAL_BODY_NAMES,
)
from tracuni.misc.helper import to_iter


def _render_essential_patterns(tag_essential_field_names):
    """Создание шаблонов для поиска существенных значений

    Parameters
    ----------
    tag_essential_field_names

    Returns
    -------

    """
    ess_flat_names = [
        name
        for el in tag_essential_field_names
        for name in to_iter(el)
    ]
    ess_first_name_map = {}
    for single_field_names in tag_essential_field_names:
        if (
            isinstance(single_field_names, Sequence)
            and
            len(single_field_names) > 1
        ):
            for name in single_field_names:
                ess_first_name_map[name] = single_field_names[0]

    ess_patterns = {}
    regexp_string = r'[\'"]{}[\'"]\s*:\s*[\'"]?(.+?)\s*[\}},\'"]'
    for tag_field_name in ess_flat_names:
        ess_patterns[tag_field_name] = re.compile(
            regexp_string.format(tag_field_name)
        )

    return ess_patterns, ess_flat_names, ess_first_name_map


(
    essential_patterns,
    essential_flat_names,
    essentials_first_name_map
) = _render_essential_patterns(
    TAG_ESSENTIAL_FIELD_NAMES
)


def _this_extractor_a(_, __):
    return None


def _this_extractor_b(field_name, data_values):
    return data_values.get(field_name)


def _this_extractor_c(field_name, data_values):
    ptn = essential_patterns[field_name]
    return ptn.search(str(data_values)).group(1)


def do(data) -> Dict[str, any]:
    if data is None:
        return {}

    data_is_dict = isinstance(data, dict)
    data_field = {}
    for body_field_name in TAG_ESSENTIAL_BODY_NAMES:
        this_data_field = (
            data.get(body_field_name, '')
            if data_is_dict
            else getattr(data, body_field_name, '')
        )

        this_extractor = _this_extractor_a
        if isinstance(this_data_field, dict):
            this_extractor = _this_extractor_b
        elif (
            isinstance(this_data_field, str)
            or
            isinstance(this_data_field, bytes)
        ):
            this_extractor = _this_extractor_c

        data_field[body_field_name] = {
            'this_extractor': this_extractor,
            'this_data': this_data_field,
        }

    def find_value(field_name):
        result = None
        if data_is_dict and field_name in data:
            return data.get(field_name)

        for body_name in TAG_ESSENTIAL_BODY_NAMES:
            try:
                extractor = data_field[body_name]
                result = extractor['this_extractor'](
                    field_name,
                    extractor['this_data']
                )
                if result is not None:
                    break
            except (IndexError, AttributeError):
                continue

        return result

    found_values = dict(
        (
            essentials_first_name_map.get(field_name, field_name),
            found_value
        )
        for field_name, found_value in (
            (field_name, find_value(field_name))
            for field_name in essential_flat_names
        ) if found_value is not None
    )
    return found_values
