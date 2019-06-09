import re
from collections import namedtuple, OrderedDict

from bs4 import BeautifulSoup

from scrapgo.utils.shortcuts import parse_src
from scrapgo import settings


def is_parsable(response, allowed_content_types=settings.PARSE_CONTENT_TYPES):
    content_type_info = response.headers.get('Content-Type')
    if content_type_info:
        for ctype in allowed_content_types:
            if ctype in content_type_info:
                return True
    return False


def prettify_text(text):
    lines = []
    for line in text.split('\n'):
        txt = re.sub('\s+', ' ', line).strip()
        lines.append(txt)
    lines = filter(None, lines)
    return '\n'.join(lines)


def prettify_textarea(soup):
    linebreakers = ['a', 'p', 'div', 'h3', 'br']
    if soup:
        for line in soup(linebreakers):
            line.replace_with(line.text + '\n')
        if soup.text:
            content = prettify_text(soup.text)
            return content
    return ''


class SoupParserMixin(object):
    CRAWL_TARGET_ATTRS = settings.CRAWL_TARGET_ATTRS
    PARSE_CONTENT_TYPES = settings.PARSE_CONTENT_TYPES

    def __init__(self, parser=settings.BEAUTIFULSOUP_PARSER, **kwargs):
        super().__init__(**kwargs)
        self.parser = parser

    def _is_parsable(self, response):
        content_type_info = response.headers.get('Content-Type')
        if not content_type_info:
            return False
        for ctype in self.PARSE_CONTENT_TYPES:
            if ctype in content_type_info:
                return True
        return False

    def _get_soup(self, response):
        if self._is_parsable(response):
            content = response.content
            return BeautifulSoup(content, self.parser)
        return BeautifulSoup('', self.parser)

    def _parse_link(self, response, link_pattern):
        soup = self._get_soup(response)
        parsed = set()

        for attr in self.CRAWL_TARGET_ATTRS:
            for link in soup('', {attr: link_pattern}):
                if link not in parsed:
                    parsed.add(link[attr])
                    yield link[attr]

    def find_texts(self, soup, *args, **kwargs):
        ret = []
        for tag in soup(*args, **kwargs):
            text = tag.text or ''
            ret.append(text.strip())
        return ret

    def prettify_textarea(self, soup):
        linebreakers = ['a', 'p', 'div', 'h3', 'br']
        if soup:
            for line in soup(linebreakers):
                line.replace_with(line.text + '\n')
            if soup.text:
                content = prettify_text(soup.text)
                return content
        return ''
    def parse_xml_table_tag(self, soup, target_tag_name, column_mapping=None, many=True):
        if column_mapping is not None:
            records = [
                OrderedDict(
                    (column_mapping.get(r.name, r.name), r.text)
                    for r in r.children
                    if r.name in column_mapping
                )
                for r in soup(target_tag_name)
            ]
        else:
            records = [
                OrderedDict((r.name, r.text))
                for r in r.children
                if r.name
            ]
        if many is True:
            return records
        if records:
            return records[0]
        return {}
