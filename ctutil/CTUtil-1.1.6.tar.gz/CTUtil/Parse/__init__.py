from typing import Dict, Any, List
from CTUtil.Parse.util import DjangoSerializer

__all__ = ['DjangoSerializer', 'parse_multiple_key']

def parse_multiple_key(data: Dict[Any, Any],
                       key_string: str,
                       split_word: str='.',
                       deepest: int=5):
    keys_list: List[str] = key_string.split(split_word)
    if not keys_list:
        raise TypeError('Keys_string: key1.key2.key3')
    if len(keys_list) > deepest:
        raise TypeError('Too much keys')
    if len(keys_list) == 1:
        return data.setdefault(keys_list[0], None)
    else:
        first_key: str = keys_list[0]
        data: Dict[Any, Any] = data.setdefault(first_key, {})
        if not data:
            return
        else:
            return parse_multiple_key(
                data,
                '.'.join(keys_list[1:]),
                split_word=split_word,
                deepest=deepest - 1)
