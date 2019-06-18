# -*- coding: utf-8 -*-
from stackifyapm.conf.constants import KEYWORD_MAX_LENGTH
from stackifyapm.utils import compat


def keyword_field(string):
    if not isinstance(string, compat.string_types) or len(string) <= KEYWORD_MAX_LENGTH:
        return string
    return string[: KEYWORD_MAX_LENGTH - 1] + u"…"
