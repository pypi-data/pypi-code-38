from enum import Enum
from typing import Type, List, Any, cast, Iterable

from tjpy_click_util.choices import DynamicChoiceParamType


class EnumChoiceParamType(DynamicChoiceParamType):
    def __init__(self,
                 enum_type: Type[Enum]):
        super().__init__()
        self._enum_type = enum_type

    @property
    def _choices(self) -> List[Any]:
        iterable = cast(Iterable, self._enum_type)  # enum types are always iterable
        return list(iter(iterable))

    def _choice_to_string(self, choice: Any) -> str:
        return choice.name
