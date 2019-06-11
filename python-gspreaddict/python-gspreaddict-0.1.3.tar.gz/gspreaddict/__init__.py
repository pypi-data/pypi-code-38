# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    from pip._vendor.distlib.util import cached_property
except ImportError:
    cached_property = property


class GSpreadDictIncompleteConfigured(Exception):
    pass


class GSpreadDictSheetNotFound(Exception):
    pass


class CacheNotProvided(object):
    pass


class GSpreadDictManager(object):
    owner = None

    def __get__(self, instance, owner):
        self.owner = owner
        return self

    @property
    def credentials(self):
        if self.owner.credentials:
            return self.owner.credentials
        elif self.owner.credentials_json_path:
            self.owner.credentials = \
                ServiceAccountCredentials.from_json_keyfile_name(
                    self.owner.credentials_json_path,
                    self.owner.api_scopes)
            return self.owner.credentials
        else:
            raise GSpreadDictIncompleteConfigured('No credentials')

    @cached_property
    def gspread_client(self):
        return gspread.authorize(self.credentials)

    @cached_property
    def gspread_document(self):
        return self.gspread_client.open_by_key(self.owner.spreadsheet_key)

    @cached_property
    def worksheet(self):
        if self.owner.sheet_name:
            for ws in self.gspread_document.worksheets():
                if self.owner.sheet_name == ws.title:
                    return ws
            else:
                raise GSpreadDictSheetNotFound(self.owner.sheet_name)
        else:
            return self.gspread_document.sheet1

    @cached_property
    def _all_values(self):
        return self.worksheet.get_all_values()

    def _make_instance(self, header, values):
        """
        OrderedDict に値を詰めて返す
        :param header:
        :param values:
        :return:
        """
        instance = self.owner()
        for i, name in enumerate(header):
            if not name:
                continue
            if len(values) < len(header):
                # 足りない
                instance[name] = None
            else:
                instance[name] = values[i]
        return instance

    def _get_all(self):
        header = []
        for i, r in enumerate(self._all_values):
            if i < self.owner.header_row_starts_zero:
                continue
            if i == self.owner.header_row_starts_zero:
                header = r
            else:
                yield self._make_instance(header, r)

    def _get_cache_key(self, suffix):
        return '{}:{}:{}'.format("gspread-dict", self.owner.__name__, suffix)

    def all(self):
        cache_key = self._get_cache_key('all()')
        result = self.owner.cache_get(cache_key)
        if result is CacheNotProvided:
            result = list(self._get_all())
            self.owner.cache_set(cache_key, result)
        return result

    def filter(self, *args, **kwargs):
        """
        全レコードを検査するフィルタ
        効率は良くない
        * args : callable のリスト。全て True のものを返す
        * kwargs: key: value の一致をテストし、全て True のものを返す
        """

        def _match(r):
            if args:
                for a in args:
                    if callable(a):
                        if not a(r):
                            return False
            if kwargs:
                for n, v in kwargs.items():
                    if n not in r:
                        return False
                    if r[n] != v:
                        return False
            return True

        return filter(_match, self.all())

    def get(self, *args, **kwargs):
        all_matches = list(self.filter(*args, **kwargs))
        if not len(all_matches):
            raise self.owner.DoesNotExist(
                'args={}, kwargs={}'.format(args, kwargs))
        if len(all_matches) >= 2:
            raise self.owner.MultipleObjectsReturned(
                'args={}, kwargs={}'.format(args, kwargs))
        return all_matches[0]


class GSpreadDict(OrderedDict):
    spreadsheet_key = None
    credentials = None
    credentials_json_path = None
    api_scopes = ['https://spreadsheets.google.com/feeds']
    sheet_name = None
    header_row_starts_zero = 0

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    objects = GSpreadDictManager()

    @classmethod
    def cache_set(cls, key, value):
        pass

    @classmethod
    def cache_get(cls, key):
        return CacheNotProvided
