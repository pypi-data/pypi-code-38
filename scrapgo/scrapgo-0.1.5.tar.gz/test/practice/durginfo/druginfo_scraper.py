import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote, urljoin, unquote
from collections import OrderedDict
from pprint import pprint


from .shortcuts import hexMD5, get_public_ip

from scrapgo import LinkRelayScraper, url, urlpattern
from scrapgo.utils import mkdir_p, cp, parse_query, queryjoin, parse_root


class DrugInfoScraper(LinkRelayScraper):
    LOGIN_URL = 'https://www.druginfo.co.kr/login/login.aspx'
    ROOT_URL = 'https://www.druginfo.co.kr/search2/search.aspx'
    CACHE_NAME = 'druginfo'

    HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.druginfo.co.kr',
        'Origin': 'https://www.druginfo.co.kr',
        'Referer': 'https://www.druginfo.co.kr/',
    }

    LINK_RELAY = [
        urlpattern(
            r'^/detail/product.aspx\?pid=(?P<pid>.+)$',
            parser='detail_parser', refresh=True
        )
    ]

    def _gen_login_data(self, id, pw, ip):
        timestamp = datetime.now().strftime("%Y%m%d%H")
        return {
            'id': id,
            'ip': ip,
            't_passwd': pw,
            'passwd': hexMD5(timestamp+hexMD5(pw)+ip),
            'timestamp': timestamp
        }

    def login(self, id, passwd):
        ip = get_public_ip()
        print('ip', ip)
        login_data = self._gen_login_data(id, passwd, ip)
        super().login(login_data)

    def detail_parser(self, response, **kwargs):
        match = response.scrap.match
        soup = response.scrap.soup
        print('detail_parser:pid', match('pid'))
        title = re.sub('\s+', ' ', soup.title.text).strip()
        print(title)


def drug_search(params):
    params['q'] = quote(params['q'], encoding='cp949')
    di = DrugInfoScraper(root_params=params)
    print(di.LINK_RELAY[0].refresh)
    di.login('anonymous04', 'admindg04!')
    di.scrap()
