# -*-coding: utf-8 -*-
import re
from yandex_parser import YandexParser


class YandexAdParser(YandexParser):
    USE_IGNORE_BLOCK = False

    PAGECOUNT_PATTERNS = (
        re.compile(ur'<div class="?serp-adv__found"?>Наш[^ ]+\s+(.*?)\s*об', re.U | re.M | re.DOTALL | re.I),
    )

    def _exclude_if_ya_domains(self, snippets):
        return snippets