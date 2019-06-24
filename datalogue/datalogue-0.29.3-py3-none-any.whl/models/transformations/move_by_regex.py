from typing import List, Union
from datalogue.errors import DtlError
from datalogue.models.transformations.commons import Transformation, _array_from_dict

class MoveByRegex(Transformation):
    """
    Finds all nodes that has a label matching to the given regex 
    and moves them as children of a new parent identified by the given to path
    """
    type_str = "MoveByRegex"

    def __init__(self, regex: str, to: List[str]):
        """
        :param regex: a string input to find which nodes should be split into two
        :param to: array of string
        """
        Transformation.__init__(self, MoveByRegex.type_str)
        self.to = to
        self.regex = regex

    def __eq__(self, other: 'MoveByRegex'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"MoveByRegex(regex: {self.regex}, to: {'.'.join(self.to)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["regex"] = self.regex
        base["to"] = self.to
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'MoveByRegex']:
        regex = json.get("regex")
        if not isinstance(regex, str):
            return DtlError("regex field is not a string in %s transformation" % MoveByRegex.type_str)

        to = _array_from_dict(json, MoveByRegex.type_str, "to")
        if isinstance(to, DtlError):
            return to

        return MoveByRegex(regex, to)
