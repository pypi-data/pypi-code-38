from typing import *

T = TypeVar('T')
TOut = TypeVar('TOut')
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

class KeyValuePair(Generic[TKey,TValue]):
    def __init__(self, key: TKey, value: TValue):
        self.key = key
        self.value = value