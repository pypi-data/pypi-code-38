# -*- coding: utf-8 -*-

"""Tools for parsing different topics
"""

import abc

import json
import requests
from datetime import datetime

import pandas as pd
from pandas.io.json import json_normalize

from statnett_api_client import config
from statnett_api_client.constants import OutputFmt

__all__ = [
    'Flow', 'Balance', 'Frequency'
]


class Topic(abc.ABC):
    """Base class for getting data from API topic
    """
    def __init__(self, **kwargs):
        """
        :keyword uri: str, URI to send requests to
        :keyword fmt: {'json', 'pandas'}, format of returned object
        :keyword date2index: boolean, if True then set index using dates (valid only with fmt='pandas')
        :keyword time_cet: boolean, if True then add CET time (Central European Time),
            by default, time is UTC (valid only with fmt='pandas')
        :keyword add_hour: boolean, if True then add 'hour' column, if time_cet is True
            then two columns are added, 'hour' and 'hour_cet'
        """
        self.uri = kwargs.get('uri', config.URI)
        self.fmt = str.lower(kwargs.get('fmt', 'pandas'))
        self.date2index = kwargs.get('date2index', False)
        self.time_cet = kwargs.get('time_cet', False)
        self.add_hour = kwargs.get('add_hour', False)

    def get(self, topic_config, **kwargs):
        """Requesting data from topic and return formatting data

        :param topic_config: dictionary, topic parameters
        :return: formatted data
        """
        data = None
        # request data from API
        response = self._send_request(topic_config['endpoint'], **kwargs)

        if self._is_valid_response(response):
            try:
                # convert data to output format
                data = self._format_response(topic_config, response)
            except ValueError:
                return None

        return data

    def _format_response(self, topic_config, response):
        """convert topic contents to output format
        """
        if self.fmt == OutputFmt.json.value:
            return self._to_json(response)
        elif self.fmt == OutputFmt.pandas.value:
            return self._to_pandas(topic_config, response)
        return None

    def _to_json(self, response):
        """convert to json array
        """
        if self._is_json(response.text):
            return response.text
        return None

    def _to_pandas(self, topic_config, response):
        """convert to pandas dataframe
        """
        parsed = self._response_to_pandas(topic_config, json.loads(response.text))

        if self.time_cet:
            parsed['date_cet'] = parsed['date_utc'].dt.tz_localize('UTC').dt.tz_convert('CET')

        if self.add_hour:
            parsed['hour_utc'] = parsed['date_utc'].dt.hour
            if self.time_cet:
                parsed['hour_cet'] = parsed['date_cet'].dt.hour

        if self.date2index:
            parsed.set_index('date_utc', inplace=True)

        return parsed

    @abc.abstractmethod
    def _send_request(self, endpoint, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def _response_to_pandas(self, topic_config, response):
        raise NotImplementedError()

    @staticmethod
    def _is_valid_response(response):
        return response.ok and hasattr(response, 'text')

    @staticmethod
    def _is_json(obj):
        try:
            _ = json.loads(obj)
        except ValueError:
            return False
        return True


class Flow(Topic):
    """Reading nordic power flow data
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _send_request(self, endpoint, **kwargs):
        return requests.get(self.uri + '/' + endpoint)

    def _response_to_pandas(self, topic_config, response):
        parsed = json_normalize(response)
        # convert timestamp to datetime
        parsed['date_utc'] = pd.to_datetime(parsed[topic_config['date_var']], unit='ms')

        return parsed


class Balance(Topic):
    """Reading nordic power balance data
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _send_request(self, endpoint, **kwargs):
        return requests.get(self.uri + '/' + endpoint)

    def _response_to_pandas(self, topic_config, response):
        # extract headers from json
        headers = json_normalize(response, record_path=topic_config['headers'])
        # get zone names from headers
        parsed = self._headers_to_zones(headers)
        # add timestamp
        parsed['date_utc'] = pd.to_datetime(response[topic_config['date_var']], unit='ms')

        for record in topic_config['records']:
            # extract specific record from json
            rec = json_normalize(response, record_path=[record])
            rec.rename(columns={'value': record}, inplace=True)
            # convert values to numeric
            rec[record] = self._to_numeric(rec[record])
            # add record to output
            parsed = parsed.merge(rec[[record]], left_index=True, right_index=True, how='left')

        parsed.reset_index(drop=True, inplace=True)

        return parsed

    @staticmethod
    def _headers_to_zones(headers):
        zones = headers.copy().query('value != ""')
        zones.rename(columns={'value': 'zone'}, inplace=True)
        return zones[['zone']]

    @staticmethod
    def _to_numeric(series):
        """remove all non-numeric characters from pandas series and convert in to numeric
        """
        return pd.to_numeric(series.str.replace(r'\D', ''), errors='coerce')


class Frequency(Topic):
    """Reading grid frequency data
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _send_request(self, endpoint, **kwargs):
        date_from = kwargs.get('date_from', None)

        params = {}

        if date_from is not None:
            params['From'] = date_from

        return requests.get(self.uri + '/' + endpoint, params=params)

    def _response_to_pandas(self, topic_config, response):
        parsed = pd.DataFrame()

        date_start = datetime.fromtimestamp(response[topic_config['date_start']] / 1000)
        date_end = datetime.fromtimestamp(response[topic_config['date_end']] / 1000)

        # add timestamp
        parsed['date_utc'] = pd.date_range(start=date_start, end=date_end, freq='T')

        # extract record from json
        record = topic_config['record']
        rec = json_normalize(response, record_path=[record])
        parsed[record] = rec.values

        return parsed

