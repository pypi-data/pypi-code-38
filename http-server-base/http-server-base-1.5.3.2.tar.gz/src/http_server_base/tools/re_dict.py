from collections import UserDict
from typing import Union, TypeVar, Generic, List, Iterable

import re
from http_server_base.tools import RegExpType

T = TypeVar('T')
class ReDict(UserDict, Generic[T]):
    def __getitem__(self, key):
        if (isinstance(key, RegExpType)):
            return super().__getitem__(key)
        elif (isinstance(key, str)):
            _regular = self.find(key)
            return super().__getitem__(_regular)
        else:
            raise TypeError(f"key must be either str or compiled regular, but not f{type(key)}")
    
    def __setitem__(self, key, item):
        if (isinstance(key, RegExpType)):
            return super().__setitem__(key, item)
        elif (isinstance(key, str)):
            regular = re.compile(fr'^{key}$')
            return super().__setitem__(regular, item)
        else:
            raise TypeError(f"key must be either str or compiled regular, but not f{type(key)}")
    
    def __delitem__(self, key):
        if (isinstance(key, RegExpType)):
            return super().__delitem__(key)
        elif (isinstance(key, str)):
            _regular = self.find(key)
            return super().__delitem__(_regular)
        else:
            raise TypeError(f"key must be either str or compiled regular, but not f{type(key)}")
    
    def __contains__(self, key):
        if (isinstance(key, RegExpType)):
            return super().__contains__(key)
        elif (isinstance(key, str)):
            if (self.find(key)):
                return True
            else:
                return False
        else:
            raise TypeError(f"key must be either str or compiled regular, but not f{type(key)}")
    
    def find(self, s:str) -> Union[RegExpType, None]:
        for _regular in self.data:
            if (_regular.match(s)):
                return _regular
        
        return None
    
    def find_all(self, s: str) -> Union[RegExpType, None]:
        for _regular in self.data:
            if (_regular.match(s)):
                yield _regular
    
    def keys(self):
        re_keys:Iterable[RegExpType] = super().keys()
        return (r.pattern for r in re_keys)
