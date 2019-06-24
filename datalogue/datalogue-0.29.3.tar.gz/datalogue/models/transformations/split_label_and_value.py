from typing import List, Union
from datalogue.errors import DtlError
from datalogue.models.transformations.commons import Transformation

class SplitLabelAndValue(Transformation):
    """
    Finds all nodes that has a label matching to the given regex and attaches two child nodes. 
    One of the node contains the label as a value and the other contains the same value
    """
    type_str = "SplitLabelAndValue"

    def __init__(self, regex: str, labelKey: str, valueKey: str):
        """
        :param regex: a string input to find which nodes should be split into two
        :param labelKey: label of node for label
        :param valueKey: label of node for value
        """
        Transformation.__init__(self, SplitLabelAndValue.type_str)
        self.regex = regex
        self.labelKey = labelKey
        self.valueKey = valueKey

    def __eq__(self, other: 'SplitLabelAndValue'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"SplitLabelAndValue(regex: {self.regex}, labelKey: {self.labelKey}, valueKey: {self.valueKey})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["regex"] = self.regex
        base["labelKey"] = self.labelKey
        base["valueKey"] = self.valueKey
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'SplitLabelAndValue']:
        regex = json.get("regex")
        if not isinstance(regex, str):
            return DtlError("regex field is not a string in %s transformation" % SplitLabelAndValue.type_str)

        labelKey = json.get("labelKey")
        if not isinstance(labelKey, str):
            return DtlError("labelKey field is not a string in %s transformation" % SplitLabelAndValue.type_str)

        valueKey = json.get("valueKey")
        if not isinstance(valueKey, str):
            return DtlError("valueKey field is not a string in %s transformation" % SplitLabelAndValue.type_str)

        return SplitLabelAndValue(regex, labelKey, valueKey)
