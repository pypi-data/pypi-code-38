import click
from abc import abstractmethod
from typing import List, Any, Optional


class _DynamicChoiceParamTypeClickOverride(click.Choice):
    name = 'dynamic-choice'

    def __init__(self, case_sensitive=True):
        super().__init__(None, case_sensitive)  # type: ignore

    @property
    @abstractmethod
    def _string_choices(self) -> List[str]:
        pass

    @property  # type: ignore
    def choices(self) -> List[str]:  # type: ignore
        return self._string_choices

    @choices.setter
    def choices(self, value: Optional[Any]) -> None:
        """Stub method for access from super().__init__"""
        pass


class DynamicChoiceParamType(_DynamicChoiceParamTypeClickOverride):

    def __init__(self, case_sensitive: bool = True):
        super().__init__(case_sensitive)

    def convert(self, value, param, ctx):
        string_value: str = super().convert(value, param, ctx)
        for choice in self._choices:
            if self._choice_to_string(choice) == string_value:
                return choice
        raise Exception("should never be able to reach this")

    @property
    def _string_choices(self) -> List[str]:
        return [self._choice_to_string(x) for x in self._choices]

    @property
    @abstractmethod
    def _choices(self) -> List[Any]:
        pass

    def _choice_to_string(self, choice: Any) -> str:
        return str(choice)
