from typing import List, Union
from datalogue.errors import DtlError
from datalogue.models.transformations.commons import Transformation


class FlatMap(Transformation):
    """
    Creates multiple ADGs from one ADG and put each child into the given path of the new ADG.

    """
    type_str = "FlatMap"

    def __init__(self, on: List[str]):
        """
        :param on: array of string that represents the path where to put created ADGs 
        """
        Transformation.__init__(self, FlatMap.type_str)
        self.on = on

    def __eq__(self, other: 'FlatMap'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"FlatMap(on: {'.'.join(self.on)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["on"] = self.on
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'FlatMap']:
        on = json.get("on")
        if isinstance(on, DtlError):
            return on

        return FlatMap(on)
