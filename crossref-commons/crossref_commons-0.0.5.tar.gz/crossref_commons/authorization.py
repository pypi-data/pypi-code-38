import json
import os

from functools import lru_cache
from pathlib import Path

from crossref_commons.config import CRAPI_KEY_FN


@lru_cache(maxsize=None)
def crapi_key():
    """Extract Polite/Plus settings from a file or env vars."""
    try:
        with open(Path.home() / CRAPI_KEY_FN, mode='r') as kf:
            key_value = kf.read()
        return json.loads(key_value)
    except FileNotFoundError:
        headers = {}
        if 'CR_API_PLUS' in os.environ:
            headers['Authorization'] = os.environ['CR_API_PLUS']
            if not headers['Authorization'].startswith('Bearer '):
                headers['Authorization'] = 'Bearer ' + headers['Authorization']
        if 'CR_API_AGENT' in os.environ:
            headers['User-Agent'] = os.environ['CR_API_AGENT']
        if 'CR_API_MAILTO' in os.environ:
            headers['Mailto'] = os.environ['CR_API_MAILTO']
        return headers
