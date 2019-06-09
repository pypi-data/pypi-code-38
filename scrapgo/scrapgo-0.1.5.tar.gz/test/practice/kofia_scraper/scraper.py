import os
import re
import json
import math
from pprint import pprint
from urllib.parse import unquote
from datetime import datetime, timedelta

from scrapgo import LinkRelayScraper, urlpattern, url, root

from .payloaders import (
    get_fund_list_payload,
    get_fund_detail_payload,
    get_fund_etc_payload,
    get_price_change_progress_payload,
    get_fund_exso_payload,
    get_fund_exso_payload_by_date,
)
from .scrap_mappings import (
    SCRAPMAP_FUND_LIST_COLUMNS,
    SCRAPMAP_FUND_DETAIL_COLUMNS,
    SCRAPMAP_PRICE_PROGRESS_COLUMNS,
    SCRAPMAP_SETTLE_EXSO_COLUMNS,
    SCRAPMAP_SETTLE_EXSO_BY_DATE_COLUMNS,
)


class KofiaScraper(LinkRelayScraper):
    CACHE_NAME = 'PROFP_SCRAP_CACHE'
    REQUEST_DELAY = 0
    RETRY_INTERVAL_SECONDS = 10, 100, 1000,
    # REQUEST_LOGGING =


class KofiaFundListScraper(KofiaScraper):
    CACHE_NAME = 'PROFP_KOFIA_FUNDLIST_CACHE'
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_list_payloader',
            parser='fund_list_parser',
            name='fund_list'
        )
    ]

    def get_request_log(self, *args, **kwargs):
        # print('get_request_log:', kwargs)
        log = super().get_request_log(*args, **kwargs)
        return "FUND_LIST: {log} {start_date}~{end_date}".format(log=log, **kwargs)

    def fund_list_payloader(self, **kwargs):
        # log = f"Retrieve FundList by Date Range: {start_date}~{end_date}"
        # print(log)
        payload = get_fund_list_payload(**kwargs)
        yield payload

    def fund_list_parser(self, response, **kwargs):
        soup = response.scrap.soup
        fund_list = self.parse_xml_table_tag(
            soup, 'selectmeta', SCRAPMAP_FUND_LIST_COLUMNS)
        return fund_list


class KofiaFundInfoScraper(KofiaScraper):
    # REQUEST_LOGGING = False
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

    def get_request_log(self, *args, **kwargs):
        log = super().get_request_log(*args, **kwargs)
        return "FUND_DETAIL: {log} {fund_std_code}".format(log=log, **kwargs)

    def fund_detail_payloader(self, fund_std_code):
        payload = get_fund_detail_payload(fund_std_code)
        # self.fund_std_code = fund_std_code
        yield payload

    def fund_detail_parser(self, response, fund_std_code, **kwargs):
        soup = response.scrap.soup
        fund = self.parse_xml_table_tag(
            soup, 'comfundbasinfooutdto', SCRAPMAP_FUND_DETAIL_COLUMNS,
            many=False
        )
        fund['표준코드'] = fund_std_code
        self.company_code = fund['회사코드']
        return fund

    def fund_etc_payloader(self, fund_std_code):
        payload = get_fund_etc_payload(fund_std_code, self.company_code)
        yield payload

    def fund_etc_parser(self, response, fund_std_code):
        soup = response.scrap.soup
        etc = self.parse_xml_table_tag(
            soup, 'comfundstdcotinfodto', SCRAPMAP_FUND_DETAIL_COLUMNS,
            many=False
        )
        etc['표준코드'] = fund_std_code
        # etc['회사코드'] = self.company_code
        return etc


class KofiaPriceProgressScraper(KofiaScraper):
    CACHE_NAME = 'PROFP_KOFIA_PRICE_PROGRESS_CACHE'
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='price_progress_payloader',
            parser='price_progress_parser',
            refresh=True,
            name='price_progress',
        )
    ]

    def get_request_log(self, *args, **kwargs):
        log = super().get_request_log(*args, **kwargs)
        return "PriceProgress: {log} {fund_std_code} {start_date}~{end_date}".format(log=log, **kwargs)

    def price_progress_payloader(self, **kwargs):
        payload = get_price_change_progress_payload(**kwargs)
        yield payload

    def price_progress_parser(self, response, fund_std_code, company_code, **kwargs):
        soup = response.scrap.soup
        price_progresses = self.parse_xml_table_tag(
            soup, 'pricemodlist', SCRAPMAP_PRICE_PROGRESS_COLUMNS
        )
        for progress in price_progresses:
            progress['표준코드'] = fund_std_code
            progress['fundinfo_id'] = fund_std_code
        return price_progresses


class KofiaSettleExSoScraper(KofiaScraper):
    CACHE_NAME = 'PROFP_KOFIA_SETTLE_EXSO_CACHE'
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_exso_payloader',
            parser='fund_exso_parser',
            refresh=True,
            name='fund_exso',
        ),
    ]

    def fund_exso_payloader(self, fund_std_code, company_code, **kwargs):
        payload = get_fund_exso_payload(fund_std_code, company_code)
        return payload

    def fund_exso_parser(self, response, fund_std_code, **kwargs):
        soup = response.scrap.soup
        exsos = self.parse_xml_table_tag(
            soup, 'settleexlist', SCRAPMAP_SETTLE_EXSO_COLUMNS)
        for exso in exsos:
            exso['표준코드'] = fund_std_code
        return exsos


class KofiaSettleExSoByDateScraper(KofiaScraper):
    CACHE_NAME = 'PROFP_KOFIA_SETTLE_EXSO_CACHE'
    LINK_RELAY = [
        url(
            'http://dis.kofia.or.kr/proframeWeb/XMLSERVICES/',
            payloader='fund_exso_by_date_payloader',
            parser='fund_exso_by_date_parser',
            name='fund_exso_by_date',
        ),
    ]

    def fund_exso_by_date_payloader(self, start_date, end_date, **kwargs):
        payload = get_fund_exso_payload_by_date(start_date, end_date)
        log = f"Retrieve Fund Exso by Date Range: {start_date}~{end_date}"
        print(log)
        return payload

    def fund_exso_by_date_parser(self, response, **kwargs):
        soup = response.scrap.soup
        exsos = self.parse_xml_table_tag(
            soup, 'selectmeta',
            many=True,
            column_mapping=SCRAPMAP_SETTLE_EXSO_BY_DATE_COLUMNS
        )
        return exsos
