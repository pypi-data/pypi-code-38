# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods and classes used to get public holidays infomation."""
from typing import Dict, Optional
from warnings import warn

from datetime import date, timedelta
from io import BytesIO, StringIO
import datetime
import os.path
import pkg_resources
import pickle

from pandas import Series
import lzma
import numpy as np
import pandas as pd

PACKAGE_NAME = 'azureml.automl.core'
HOLIDAYS_DATA_PATH = pkg_resources.resource_filename(PACKAGE_NAME,
                                                     os.path.join('featurizer', 'transformer', 'timeseries',
                                                                  'publicholidays', 'data', 'holidays.7z'))


def _holiday_data_loader(_path=HOLIDAYS_DATA_PATH):
    """Static initializer that loads holiday data."""
    with lzma.open(_path, "rb") as fr:
        return pickle.loads(fr.read())


class Holidays:
    """Methods and classes used to get public holidays infomation."""

    HOLIDAYS_DF = _holiday_data_loader()  # type: pd.DataFrame

    def __init__(self):
        """Create a Holidays object."""
        self.holidays_dates = None  # type: Optional[Dict[datetime.datetime, None]]
        self.holidays_dates_country = None  # type: Optional[str]
        self.holidays_dates_country_code = None  # type: Optional[str]
        mappings_cr = Series(Holidays.HOLIDAYS_DF.CountryCode.values, index=Holidays.HOLIDAYS_DF.CountryOrRegion)
        mappings_cc = Series(Holidays.HOLIDAYS_DF.CountryOrRegion.values, index=Holidays.HOLIDAYS_DF.CountryCode)
        mappings_cr = mappings_cr.append(mappings_cc)
        self.holidays_country_mappings = mappings_cr.to_dict()

    def get_window_by_effect_gap(self, effect: str, gap: int) -> int:
        """
        Generate holiday window number.

        :param effect: holiday window effect level
        :param gap: the delta days between current holiday and the last/next holiday
        """
        effect_num = 0
        if effect == 'Low':
            effect_num = 2
        if effect == 'Meduim':
            effect_num = 5
        if effect == 'High':
            effect_num = 10
        if effect_num > gap:
            return gap
        else:
            return effect_num

    def adding_holidayname_by_window(self, _country: str, _countryCode: str, _name: str,
                                     window: int, window_type: str, curDate: date, data: pd.DataFrame) \
            -> pd.DataFrame:
        """
        Generate holiday window name.

        :param _country: country/region of current data.
        :param _countryCode: countryCode of current data.
        :param _name: holiday name which needs be processed.
        :param window: window of current holiday.
        :param window_type: lower window or upper window.
        :param curDate: date of the holiday.
        :param data: holiday data which needs be processed.
        :return: The dataframe with holidayname base on the window added row by row.
        """
        for i in range(1, window + 1):
            newDate = curDate
            windowInName = ' days '
            if i == 1:
                windowInName = ' day '
            if window_type == 'lower':
                windowInName = windowInName + 'before '
                newDate = curDate + timedelta(days=-i)
            if window_type == 'upper':
                windowInName = windowInName + 'after '
                newDate = curDate + timedelta(days=i)
            if np.datetime64(newDate) not in data['Date'].values:
                name = str(i) + windowInName + _name
                data = data.append({'Name': name, 'Date': newDate, 'CountryOrRegion': _country,
                                    'CountryCode': _countryCode}, ignore_index=True)
        return data

    def adding_holidayname_by_window_row_by_row(self, data: pd.DataFrame, target_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate holiday window names row by row.

        :param data: holiday data which needs be iterated.
        :param target_data: holiday data which needs be processed.
        :return: The dataframe with holidayname base on the window added row by row.
        """
        target_data_origin = target_data.copy()
        country_lst = Series(data.CountryCode.values, index=data.CountryOrRegion).to_dict().keys()
        for item in country_lst:
            temp_target = target_data[target_data.CountryOrRegion == item]
            temp_country_df = data[data.CountryOrRegion == item]
            for idx, row in temp_country_df.iterrows():
                lower = row['lowerWindow']
                upper = row['upperWindow']

                _country = row['CountryOrRegion']
                _countryCode = row['CountryCode']
                curDate = pd.to_datetime(row['Date'])
                _name = row['Name']
                temp_target = self.adding_holidayname_by_window(_country, _countryCode, _name,
                                                                lower, 'lower', curDate, temp_target)
                temp_target = self.adding_holidayname_by_window(_country, _countryCode, _name,
                                                                upper, 'upper', curDate, temp_target)
            target_data_origin = pd.concat([target_data_origin, temp_target], ignore_index=True) \
                .drop(columns=['index']).drop_duplicates()
            target_data_origin.reset_index(drop=True)
        return target_data_origin

    def update_holidays_by_adding_window(self) -> None:
        """Generate the holidays csv with window into name."""
        holiday_origin_dataPath = pkg_resources \
            .resource_filename(PACKAGE_NAME,
                               os.path.join('featurizer', 'transformer', 'timeseries', 'publicholidays',
                                            'data', 'holidays_origin.7z'))
        window_dataPath = pkg_resources \
            .resource_filename(PACKAGE_NAME,
                               os.path.join('featurizer', 'transformer', 'timeseries', 'publicholidays',
                                            'data', 'holiday_effect_window.7z'))
        with lzma.open(holiday_origin_dataPath, "rb") as f:
            df_origin = pickle.loads(f.read())
        df_origin = df_origin.rename(columns={'normalizeHolidayName': 'Name', 'countryOrRegion': 'CountryOrRegion',
                                              'countryRegionCode': 'CountryCode', 'date': 'Date',
                                              'isPaidTimeOff': 'IsPaidTimeOff'})
        with lzma.open(window_dataPath, "rb") as fr:
            holiday_window = pickle.loads(fr.read())
        df_com = df_origin.set_index(['holidayName', 'CountryOrRegion']) \
            .join(holiday_window.set_index(['holidayName', 'CountryOrRegion']), how='left')
        df_com = df_com.reset_index()
        df_com['isObserved'] = df_com['holidayName'].apply(lambda x: x.find("(Observed)"))
        df_com = df_com[df_com.isObserved < 0]
        _holidays = df_com.reset_index()

        country_lst = Series(_holidays.CountryCode.values, index=_holidays.CountryOrRegion).to_dict().keys()

        current_df = pd.DataFrame(columns=['Date', 'CountryOrRegion', 'gapFormer', 'gapNext'])
        for item in country_lst:
            temp_dts = list(dict.fromkeys(_holidays[_holidays.CountryOrRegion == item]['Date'].tolist(), None).keys())
            temp_dts.sort()
            i = 0
            while i < len(temp_dts):
                gapN = 0
                gapF = 0
                if i == len(temp_dts) - 1:
                    gapN = 0
                elif i >= 0:
                    gapN = (temp_dts[i + 1] - temp_dts[i]).days
                    if i > 0:
                        gapF = (temp_dts[i] - temp_dts[i - 1]).days
                current_df = current_df.append({'Date': temp_dts[i], 'CountryOrRegion': item,
                                                'gapFormer': gapF, 'gapNext': gapN}, ignore_index=True)
                i = i + 1

        temp = _holidays.copy()
        temp.drop(columns=['holidayName', 'isObserved', 'effectLevel'], inplace=True)

        _holidays = _holidays.set_index(['Date', 'CountryOrRegion']) \
            .join(current_df.set_index(['Date', 'CountryOrRegion']), how='left')
        _holidays = _holidays.reset_index()
        temp.reset_index(inplace=True, drop=True)

        _holidays['lowerWindow'] = _holidays.apply(lambda row:
                                                   self.get_window_by_effect_gap(row['effectLevel'],
                                                                                 row['gapFormer']),
                                                   axis=1)
        _holidays['upperWindow'] = _holidays.apply(lambda row:
                                                   self.get_window_by_effect_gap(row['effectLevel'],
                                                                                 row['gapNext']),
                                                   axis=1)

        # Here is the part to generate holiday window names
        temp = self.adding_holidayname_by_window_row_by_row(_holidays, temp)

        temp['_IsPaidTimeOff'] = [1 if isinstance(x, bool) and x else 0 for x in temp['IsPaidTimeOff']]
        temp.drop(columns=['IsPaidTimeOff'], inplace=True)
        temp = temp.rename(columns={'_IsPaidTimeOff': 'IsPaidTimeOff'}).sort_values(by=['Date'])
        csv_content = temp.to_csv(index=False, date_format='%m/%d/%Y')
        df = pd.read_csv(StringIO(csv_content),
                         parse_dates=['Date'],
                         date_parser=lambda x: pd.datetime.strptime(x, '%m/%d/%Y'))
        with lzma.open(HOLIDAYS_DATA_PATH, "wb") as f:
            f.write(pickle.dumps(df))

    def get_holidays_dates(self, country_code: Optional[str] = None, country_or_region: Optional[str] = None) \
            -> Optional[Dict[datetime.datetime, None]]:
        """
        Get a Dict with Key of the dates of holidays.

        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: The dict with dates of holidays as the keys and None as values.
        """
        date_col_name = 'Date'
        if date_col_name in Holidays.HOLIDAYS_DF.columns:
            if country_code:
                if self.holidays_dates_country_code != country_code:
                    self.holidays_dates = \
                        dict.fromkeys(Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryCode ==
                                                           country_code][date_col_name].tolist(), None)
                    self.holidays_dates_country_code = country_code
                    self.holidays_dates_country = self.holidays_country_mappings[country_code]
                elif self.holidays_dates_country_code == country_code and self.holidays_dates is None:
                    self.holidays_dates = \
                        dict.fromkeys(Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryCode ==
                                                           country_code][date_col_name].tolist(), None)
            elif country_or_region:
                if self.holidays_dates_country != country_or_region:
                    self.holidays_dates = \
                        dict.fromkeys(Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryOrRegion ==
                                                           country_or_region][date_col_name].tolist(), None)
                    self.holidays_dates_country_code = self.holidays_country_mappings[country_or_region]
                elif self.holidays_dates_country == country_or_region and self.holidays_dates is None:
                    self.holidays_dates = \
                        dict.fromkeys(Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryOrRegion ==
                                                           country_or_region][date_col_name].tolist(), None)
            else:
                self.holidays_dates_country = None
                self.holidays_dates = None
        else:
            warn("Missing Date column in the holiday data.", ResourceWarning)
            return None

        return self.holidays_dates

    def is_holiday(self, target_date: date, country_code: str = "US") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        country_holiday_dates = self.get_holidays_dates(country_code=country_code)
        if country_holiday_dates:
            return (target_date in country_holiday_dates)
        else:
            return False

    def is_holiday_by_country_or_region(self, target_date: date, country_or_region: str = "United States") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        country_holiday_dates = self.get_holidays_dates(country_or_region=country_or_region)
        if country_holiday_dates:
            return (target_date in country_holiday_dates)
        else:
            return False

    def get_holidays_in_range(self, start_date: date, end_date: date, country_code: str = "US") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        rs = pd.DataFrame(columns=["Name", "Date", "IsPaidTimeOff"])
        rsdf_country = Holidays.HOLIDAYS_DF
        if country_code is not None:
            rsdf_country = Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryCode == country_code]
        else:
            return rs
        rs_date = rsdf_country[(rsdf_country.Date >= start_date) & (rsdf_country.Date <= end_date)]
        rs_date.drop(columns=['CountryOrRegion', 'CountryCode'], inplace=True)
        rs_date.reset_index(inplace=True, drop=True)
        rs = rs_date
        return rs

    def get_holidays_in_range_by_country_or_region(self, start_date: date, end_date: date,
                                                   country_or_region: str = "United States") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        rs = pd.DataFrame(columns=["Name", "Date", "IsPaidTimeOff"])
        rsdf_country = Holidays.HOLIDAYS_DF
        if country_or_region is not None:
            rsdf_country = Holidays.HOLIDAYS_DF[Holidays.HOLIDAYS_DF.CountryOrRegion == country_or_region]
        else:
            return rs
        rs_date = rsdf_country[(rsdf_country.Date >= start_date) & (rsdf_country.Date <= end_date)]
        rs_date.drop(columns=['CountryOrRegion', 'CountryCode'], inplace=True)
        rs_date.reset_index(inplace=True, drop=True)
        rs = rs_date
        return rs
