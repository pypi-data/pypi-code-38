# -*- coding: utf-8 -*-

import json
import os
from pkg_resources import resource_filename

CURRENCY = {"uk": "£", "us": "$"}


def read_json_file(jsonfile: str):
    """Return Python dictionary from json file

    Args:
        jsonfile: path to JSON file
    Returns:
        jsondict: python dictionary
    """
    if not os.path.exists(jsonfile):
        raise FileNotFoundError("{} does not exist".format(jsonfile))

    with open(jsonfile) as f:
        data = json.load(f)

    new_data = {}

    for key in data:
        new_key = int(key)
        new_data[new_key] = data[key]
        new_data[new_key]["inflation"] = int(data[key]["inflation"])
    del data
    return new_data


def get_country_json(country: str):
    """Returns data from json file given country
    
    Args:
        country: Country, either [UK/US]
    Returns:
        jsonfile: Path to JSON file
    """
    jsonfile = resource_filename(
        "inflate", "data/{}_inflation.json".format(country.lower())
    )
    return read_json_file(jsonfile)


def get_inflation_amount(
    country: str, start_year: int, end_year: int, amount: int, inclusive: bool
):
    """Computes how much amount in start_year is worth in end_year

    Args:
        country: Country of inflation
        start_year: starting year to begin calculation
        end_year: ending year to being calculation
        amount: amount to compute inflation on
    Returns:
        inflated_amount: how much $amount in $start_year is worth in $end_year
    """

    data = get_country_json(country)
    if not start_year in data:
        raise KeyError("No data for {} year".format(start_year))
    if not end_year in data:
        raise KeyError("No data for {} year".format(end_year))

    inflated_amount = amount

    if start_year > end_year:
        if inclusive:
            end_year -= 1
        for counter in range(start_year, end_year, -1):
            inflated_amount /= data[counter]["inflation"] / 100 + 1
    else:
        if inclusive:
            end_year += 1
        for counter in range(start_year, end_year):
            inflated_amount *= data[counter]["inflation"] / 100 + 1

    return round(inflated_amount, 2)


def get_average_inflation(
    country: str, start_year: int, end_year: int, inclusive: bool
):
    inflated_amount = get_inflation_amount(country, start_year, end_year, 1, inclusive)
    percentage = (inflated_amount - 1) * 100
    average = (
        percentage / abs(end_year - start_year + 1)
        if inclusive
        else percentage / abs(end_year - start_year)
    )
    return round(average, 2)

