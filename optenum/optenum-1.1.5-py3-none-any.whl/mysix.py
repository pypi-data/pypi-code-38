"""
My py2 & py3 compilable module.
"""

import six

if six.PY2:
    import re, tokenize, keyword
    # regx_identifier = re.compile(r'^[a-z][a-z0-9_]*\Z', re.IGNORECASE)
    regx_identifier = re.compile(tokenize.Name + r'\Z', re.IGNORECASE)


def is_identifier(s):
    if six.PY2:
        if keyword.iskeyword(s):
            return False
        m = regx_identifier.match(s)
        return bool(m)
    else:
        return s.isidentifier()
