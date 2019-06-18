from pprint import pformat
from typing import Any, Dict


def _pprint(obj: Any, *keys: str) -> str:
    return pformat({key: getattr(obj, key) for key in keys}, indent=2)


def move_dict_value_up_one_level(dictionary: Dict, key: str) -> None:
    """Changes dict {'key': {'sub_key': 'sub_value'}} to {'key': 'sub_value'}"""
    if key in dictionary:
        dictionary[key] = get_first_value(dictionary[key])


def get_first_key(dictionary: Dict) -> str:
    return list(dictionary.keys())[0]


def get_first_value(dictionary: Dict) -> Any:
    return list(dictionary.values())[0]


get_choice_name = get_first_key  # pylint: disable=invalid-name
get_choice_value = get_first_value  # pylint: disable=invalid-name
