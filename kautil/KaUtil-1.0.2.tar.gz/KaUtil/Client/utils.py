from enum import Enum
from KaUtil.Client import Request
from typing import Type, List, Tuple, Dict
from urllib.parse import urljoin
import re


def is_url(url: str):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url)


def url_query_to_dict(query: str):
    query_list: List[str] = query.split('&')
    data: Dict[str, str] = {}
    for q in query_list:
        key, value = q.split('=')
        data[key] = value
    return data


class Extract(object):

    @classmethod
    def replace_trashy_symbol(cls, text: str):
        pass

    @classmethod
    def extract_title(cls, request: Type[Request]):
        data: List[Tuple[str, str]] = []
        html = request.html
        infos = html.xpath('//a')
        for info in infos:
            url = ''.join(info.xpath('./@href'))
            title = ''.join([char.strip() for char in info.xpath('string(.)')])
            if url and title:
                if is_url(url):
                    data.append((urljoin(request.response.url, url), title))
        return data

    @classmethod
    def filter_space_char(cls, text: str, replace_char: str = ''):
        space_char: List[str] = ['\n', '\r', '\t']
        for char in space_char:
            text = text.replace(char, replace_char)
        return text.strip()

    @classmethod
    def extract_content(cls, request: Type[Request]):
        pass