import contextlib
import csv

from typing import List, Dict, Union, TextIO

from .utils import normalize


def read_csv(fp: Union[str, TextIO], empty_value=None, *args, **kwargs) -> List[Dict]:
    """
    Reads a CSV file into a Python list of dictionaries.
    :param file: CSV file or stream.
    :return: parsed CSV file.
    """
    data = list()
    with contextlib.ExitStack() as stack:
        if type(fp) is str:
            fp = stack.enter_context(open(fp, 'r'))

        r = csv.DictReader(fp, *args, **kwargs)
        for row in r:
            data.append({k:v if v != '' else empty_value for k,v in row.items()})
    return data


def walk_through_csv(fp: Union[str, TextIO], *args, **kwargs):
    with contextlib.ExitStack() as stack:
        if type(fp) is str:
            fp = stack.enter_context(open(fp, 'r'))

        r = csv.DictReader(fp, *args, **kwargs)

        for row in r:
            yield row


def write_csv(data: List[Dict], file: Union[str, TextIO], headers=None, normalize_data=True, default=None, *args, **kwargs):
    """
    Writes a Python list of dictionaries into a CSV file.
    :param data:
    :param filename: CSV file.
    :return:
    """

    if normalize_data:
        data = normalize(data, headers=headers, default=default)

    headers = headers or data[0].keys()

    with contextlib.ExitStack() as stack:
        if type(file) is str:
            fp = stack.enter_context(open(file, 'w'))
        else:
            fp = file

        w = csv.DictWriter(fp, headers, *args, **kwargs)
        w.writeheader()
        try:
            w.writerows(data)
        except ValueError:
            raise ValueError('Data must be normalized for CSV files (i.e. all dicts must have same keys). Suggestion: use normalize_data=True')
