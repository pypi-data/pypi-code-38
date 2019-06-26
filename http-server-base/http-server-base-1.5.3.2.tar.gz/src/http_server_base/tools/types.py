import re
from typing import Union, Tuple, Type, Any, Dict, List, TypeVar

RegExpType = type(re.compile(r'some_regular'))
JsonSerializable = Union[str, int, float, Dict[str, 'JsonSerializable'], List['JsonSerializable'], None]
Binary = Union[bytes, bytearray, None]
