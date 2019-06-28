# -*- coding: utf-8 -*-

import json
import os
from pkg_resources import resource_filename

CURRENCY = {"uk": "£", "us": "$"}
__version__ = "0.1rc3"


class Inflate:
    def __init__(
        self,
        start_year: int,
        end_year: int = 2018,
        country: str = "UK",
        inclusive: bool = False,
    ):
        """Implement Inflate class.

            Arguments:
                start_year: the start year to measure inflation from
                end_year: the end year to measure inflation to
                country: the country you want to measure inflation in
                inclusive: should the end year be included or not
            Implements:
                <<<put in methods documentation here>>>
        """

        self._start_year = start_year
        self._end_year = end_year
        self._country = country
        self._data = self._get_data()
        self._inclusive = inclusive

    @property
    def start_year(self):
        return self._start_year

    @property
    def end_year(self):
        return self._end_year

    @property
    def country(self):
        return self._country

    @start_year.setter
    def set_start_year(self, start_year):
        if start_year < 1751:
            raise ValueError(
                "We only support starting years of 1751 or later. You inputted {0}".format(
                    start_year
                )
            )
        elif start_year not in self._data:
            raise KeyError("{0} not found in our data".format(start_year))
        else:
            self._start_year = start_year

    @end_year.setter
    def set_end_year(self, end_year):
        if end_year > 2018:
            raise ValueError(
                "We only support ending years of 2018 or lower. You inputted {0}".format(
                    self.end_year
                )
            )
        elif end_year not in self._data:
            raise KeyError("{0} not found in our data".format(end_year))
        else:
            self._end_year = end_year

    @country.setter
    def set_country(self, country):
        country = country.lower().strip()
        if country not in ("uk", "us"):
            raise ValueError("We currently only have inflation data for the UK and US")
        else:
            self._country = country

    def inflate(self, amount: float = 1.0, formatted: bool = True):
        """Computes how much amount in start_year is worth in end_year

        Args:
            amount: amount to compute inflation on
        Returns:
            inflated_amount: how much $amount in $start_year is worth in $end_year
        """

        inflated_amount = amount

        if self._start_year > self.end_year:
            if self._inclusive:
                self.end_year -= 1
            for counter in range(self.start_year, self.end_year, -1):
                inflated_amount /= self._data[counter]["inflation"] / 100 + 1
        else:
            if self._inclusive:
                self.end_year += 1
            for counter in range(self.start_year, self.end_year):
                inflated_amount *= self._data[counter]["inflation"] / 100 + 1

        if formatted:
            return round(inflated_amount, 2)
        else:
            return inflated_amount

    def average_inflation(self):
        inflated_amount = self.inflate(amount=1, formatted=False)
        percentage = (inflated_amount - 1) * 100
        period = abs(self.end_year - self.start_year)
        average = percentage / (period + 1) if self._inclusive else percentage / period
        return round(average, 2)

    def _get_data(self):
        """Returns data from json file given country
    
        Args:
            country: Country, either [UK/US]
        Returns:
            jsonfile: Path to JSON file
        """

        jsonfile = resource_filename(
            "inflate", "data/{}_inflation.json".format(self.country)
        )
        return _read_json_file(jsonfile)


def _read_json_file(jsonfile: str):
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
        new_data[new_key]["inflation"] = float(data[key]["inflation"])
    del data
    return new_data

