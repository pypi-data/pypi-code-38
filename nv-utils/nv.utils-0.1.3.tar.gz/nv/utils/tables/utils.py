from typing import List, Dict, MutableSet

from ..collections.sets import OrderedSet


__all__ = ["extract_headers", "normalize", "check_normalized"]


def check_normalized(input_list: List[Dict], headers=None) -> bool:
    check = set(headers) if headers else set(input_list[0].keys())
    for row in input_list:
        if set(row.keys()) != check:
            return False

    return True


def extract_headers(input_list: List[Dict]) -> MutableSet:
    # New implementation is heavier, but tries to maintain keys in order (as dicts in Python 3.6 are preserving order)
    headers = OrderedSet()
    for row in input_list:
        if len(headers):
            headers_set = set()
            cur_headers = OrderedSet(row.keys())
            if cur_headers != headers:
                # Check if inequality is caused by different items
                cur_headers_set = set(cur_headers)
                if set(cur_headers) != headers_set:
                    # Different items found
                    new_items = cur_headers_set - headers_set
                    # Append different items
                    for i in new_items:
                        headers.add(i)
        else:
            headers = OrderedSet(row.keys())
            headers_set = set(row.keys())
    return headers


def normalize(input_list: List[Dict], headers=None, default=None, check_before=True) -> List[Dict]:
    """
    Normalizes a list of dictionaries, so that all items in the list have same keys by setting non-existent fields to default.
    :param input_list: list of dictionaries.
    :param default: default value to be set to non existent items (typically either None or empty string)
    :param check_before: check if list is already normalized. 
    :return: normalized copy of list.
    """

    if check_before and check_normalized(input_list, headers=headers):
        return list(input_list)

    # Creates a set with all keys
    if not headers:
        headers = extract_headers(input_list)

    # Creates a new list with normalized dicts
    output_list = list()

    for row in input_list:
        new_row = dict()
        for k in headers:
            new_row.update({k: row.get(k, default)})
        output_list.append(new_row)

    return output_list
