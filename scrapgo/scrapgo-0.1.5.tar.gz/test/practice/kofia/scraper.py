import os
import re
import json
import math
from pprint import pprint
from urllib.parse import unquote
from datetime import datetime, timedelta

import pandas as pd

from scrapgo import LinkRelayScraper, urlpattern, url, root

from .payloaders import get_fund_list_payload, get_fund_detail_payload, get_fund_etc_payload, get_price_change_progress_payload, get_fund_exso_payload
from .columns import FUND_LIST_COLUMNS, FUND_DETAIL_COLUMNS, PRICE_PROGRESS_COLUMNS, SETTLE_EXSO_COLUMNS
from .utils import parse_record


class KofiaScraper(LinkRelayScraper):
    # ROOT_URL = 'http://dis.kofia.or.kr'
    CACHE_NAME = 'KOFIA'
    # CACHE_EXPIRATION = timedelta(seconds=60)


class KofiaFundListScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_list_payloader',
            parser='fund_list_parser',
            name='fund_list',
        )
    ]

    payload = get_fund_list_payload(start_date, end_date)
    yield payload

    def fund_list_parser(self, response, **kwargs):
        soup = response.scrap.soup
        fund_list = parse_record(soup, 'selectmeta', FUND_LIST_COLUMNS)
        self.fund_std_code_list = [row['표준코드'] for row in fund_list]
        return fund_list


class KofiaFundInfoScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_detail_payloader',
            parser='fund_detail_parser',
            name='fund_detail'
        ),
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_etc_payloader',
            parser='fund_etc_parser',
            name='fund_etc',
        ),
    ]

    def fund_detail_payloader(self, fund_std_code):
        payload = get_fund_detail_payload(fund_std_code)
        self.fund_std_code = fund_std_code
        yield payload

    def fund_detail_parser(self, response, **kwargs):
        soup = response.scrap.soup
        fund = parse_record(
            soup, 'comfundbasinfooutdto', FUND_DETAIL_COLUMNS,
            many=False
        )
        fund['표준코드'] = self.fund_std_code
        self.company_code = fund['회사코드']
        return fund

    def fund_etc_payloader(self, fund_std_code):
        payload = get_fund_etc_payload(fund_std_code, self.company_code)
        yield payload

    def fund_etc_parser(self, response, fund_std_code):
        soup = response.scrap.soup
        etc = parse_record(
            soup, 'comfundstdcotinfodto', FUND_DETAIL_COLUMNS,
            many=False
        )
        etc['표준코드'] = fund_std_code
        etc['회사코드'] = self.company_code
        return etc


class KofiaPriceProgressScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='price_progress_payloader',
            parser='price_progress_parser',
            name='price_progress',
        ),
    ]

    def price_progress_payloader(self, fund_std_code, company_code, initial_date):
        start_date = initial_date
        end_date = datetime.today().strftime("%Y%m%d")
        payload = get_price_change_progress_payload(
            fund_std_code, company_code,
            start_date=start_date,
            end_date=end_date
        )
        yield payload

    def price_progress_parser(self, response, fund_std_code, company_code, **kwargs):
        soup = response.scrap.soup
        price_progresses = parse_record(
            soup, 'pricemodlist', PRICE_PROGRESS_COLUMNS
        )
        for progress in price_progresses:
            progress['표준코드'] = fund_std_code
            progress['회사코드'] = company_code
        return price_progresses


class KofiaSettleExSoScraper(KofiaScraper):
    LINK_RELAY = [
        url(
            '/proframeWeb/XMLSERVICES/',
            payloader='fund_exso_payloader',
            parser='fund_exso_parser',
            name='fund_exso',
        ),
    ]

    def fund_exso_payloader(self, fund_std_code, company_code):
        payload = get_fund_exso_payload(fund_std_code, company_code)
        return payload

    def fund_exso_parser(self, response, **kwargs):
        soup = response.scrap.soup
        exso = parse_record(soup, 'settleexlist', SETTLE_EXSO_COLUMNS)
        return exso


def get_kofia_fund_list(start_date, end_date):
    kflist = KofiaFundListScraper()
    r = kflist.scrap(start_date=start_date, end_date=end_date)
    df = pd.DataFrame(r['fund_list'])
    print(df.shape)
    return df


def get_kofia_fund_detail(fund_std_code):
    kfinfo = KofiaFundInfoScraper()
    r = kfinfo.scrap(fund_std_code=fund_std_code)
    df_detail = pd.DataFrame(r['fund_detail'])
    df_etc = pd.DataFrame(r['fund_etc'])
    df = pd.merge(df_detail, df_etc)
    if df.shape[0] > 0:
        return df.iloc[0]


def get_kofia_fund_price_progress(fund_std_code, company_code=None, initial_date=None):
    if company_code is None or initial_date is None:
        fund = get_kofia_fund_detail(fund_std_code)
        company_code = fund['회사코드']
        initial_date = fund['설정일']
    fkprg = KofiaPriceProgressScraper()
    r = fkprg.scrap(
        fund_std_code=fund_std_code,
        company_code=company_code,
        initial_date=initial_date
    )
    df = pd.DataFrame(r['price_progress'])
    return df


def get_kofia_fund_settle_exso(fund_std_code, company_code=None):
    if company_code is None:
        fund = get_kofia_fund_detail(fund_std_code)
        company_code = fund['회사코드']
    kfexso = KofiaSettleExSoScraper()
    r = kfexso.scrap(fund_std_code=fund_std_code, company_code=company_code)
    records = r['fund_exso']
    df = pd.DataFrame(records)
    return df
