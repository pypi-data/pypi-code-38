from typing import List, Union
from datalogue.errors import DtlError, _property_not_found
from datalogue.models.transformations.commons import Transformation
from datalogue.utils import _parse_string_list


class AppendIndexToLabel(Transformation):
    """
    Adds indexes to all the nodes that are present at the same path to be able to distinguish them
    """
    type_str = "AppendIndexToLabel"

    def __init__(self, path: List[str]):
        """
        :param path: Adds indexes to all the nodes at the same path
        """
        Transformation.__init__(self, AppendIndexToLabel.type_str)
        self.path = path

    def __eq__(self, other: 'AppendIndexToLabel'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"AppendIndexToLabel(path: {self.path})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'AppendIndexToLabel']:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        return AppendIndexToLabel(path)
