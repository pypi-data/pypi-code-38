from typing import Union
from datalogue.errors import DtlError, _property_not_found
from datalogue.models.transformations.commons import Transformation


class MapFunction(Transformation):
    """
    Applies a given function to an ADG that should return and ADG

    It should be of the form:

    (adg: ADG, env: MAP) => {
        // Here the content of function goes
    }

    ALPHA Feature
    """
    type_str = "MapFunction"

    def __init__(self, f: str):
        """
        :param f: function to be applied to the adg
        """
        Transformation.__init__(self, MapFunction.type_str)
        self.f = f

    def __eq__(self, other: 'MapFunction'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"MapFunction(f: {self.f!r})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["f"] = self.f
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'MapFunction']:
        f = json.get("f")
        if f is None:
            return _property_not_found("f", json)

        return MapFunction(f)
