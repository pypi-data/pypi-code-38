# -*- coding:utf-8 -*-
import re

from yandex_parser.utils import to_unicode


class YandexBarParser(object):
    params = {
        'domain': ur'domain="(.*?)"',
        'title': ur'title="(.*?)"',
        'value': ur'value="(.*?)"',
        'rang': ur'rang="(.*?)"',
        'textinfo': ur'<textinfo>(.*?)</textinfo>',
        'url': ur'<topic[^>]+title[^>]+url="(.*?)"'
    }
    
    def __init__(self, content):
        self.content = to_unicode(content)
    
    def get_tic(self):
        bar = self.get_bar_info()
        tic = bar.get('value', 0)
        return int(tic)
    
    def get_theme(self):
        bar = self.get_bar_info()
        title = bar.get('title', '')
        return title
    
    def get_bar_info(self):
        bar = {}
        for key, regexp in self.params.items():
            bar[key] = self._get_bar_part(regexp, self.content)
        return bar

    def _get_bar_part(self, regexp, response):
        result = ''
        match_part = re.findall(regexp, response, re.DOTALL | re.IGNORECASE | re.UNICODE | re.MULTILINE)
        if match_part:
            result = str(match_part[0].strip())
        return result
        