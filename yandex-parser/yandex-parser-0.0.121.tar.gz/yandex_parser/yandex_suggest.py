# -*- coding:utf-8 -*-
import json
import re

from yandex_parser.utils import to_unicode


class YandexSuggestParser(object):
    def __init__(self, content):
        self.content = to_unicode(content)

    def get_suggest(self):
        matches = re.findall("suggest.apply\((.*?)\)", self.content, re.DOTALL | re.IGNORECASE | re.UNICODE | re.MULTILINE)
        if not matches:
            return []
        matches = matches[0].replace(',[]', '')
        try:
            return json.loads(matches)[1]
        except Exception:
            return []
        