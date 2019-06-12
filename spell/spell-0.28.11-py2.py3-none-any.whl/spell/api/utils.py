# -*- coding: utf-8 -*-
from six.moves.urllib.parse import quote_plus


def url_path_join(*tokens):
    return '/'.join(quote_plus(str(s).strip('/'), ":") for s in tokens)


def to_RFC3339_string(dt):
    # create RFC3339 compliant time zone string
    return dt.isoformat() + ("" if dt.tzinfo else "Z")
