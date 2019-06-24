from datalogue.models.transformations.commons import Transformation
from datalogue.utils import _parse_string_list, SerializableStringEnum, _parse_list
from datalogue.errors import _enum_parse_error, DtlError, _property_not_found
from typing import List, Union


class Function(SerializableStringEnum):
    """
    Functions that can be used to classify the context
    """
    EditDistance = "EditDistance"

    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("ClassifyContextFunction", s)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, 'Function']:
        return SerializableStringEnum.from_str(Function)(string)


class ClassMapping:
    """
    Mapping between a class, references and a threshold
    """

    def __init__(self, tag: str, refs: List[str], threshold: int):
        """

        :param tag: class to be used as a tag
        :param refs: list of reference to compare the context to
        :param threshold: maximum distance allowed between the context and the reference for the datapoint to be
         classified as tag
        """
        self.tag = tag
        self.refs = refs
        self.threshold = threshold

    def __eq__(self, other: 'ClassMapping'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ClassMapping(tag: {self.tag!r}, refs: {self.refs}, threshold: {self.threshold})"

    def _as_payload(self) -> dict:
        return {
            "type": "ClassMapping",
            "class": self.tag,
            "refs": self.refs,
            "threshold": self.threshold
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ClassMapping']:
        t = json.get("type")
        if t != "ClassMapping":
            return DtlError("type property is not ClassMapping")

        tag = json.get("class")
        if tag is None:
            return _property_not_found("class", json)

        refs = json.get("refs")
        if refs is None:
            return _property_not_found("refs", json)
        else:
            refs = _parse_string_list(refs)
            if isinstance(refs, DtlError):
                return refs

        threshold = json.get("threshold")
        if threshold is None:
            return _property_not_found("threshold", json)

        return ClassMapping(tag, refs, threshold)


class ClassifyContext(Transformation):
    """
    ClassifyContext: Runs a function on the context (label) to be classify the datapoint
    """

    type_str = "ClassifyContext"

    def __init__(self, use: Function, options: List[ClassMapping]):
        """
        :param use: Function to be used to do the classification
        """
        Transformation.__init__(self, ClassifyContext.type_str)
        self.use = use.value
        self.options = options

    def __eq__(self, other: 'ClassifyContext'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ClassifyContext(use: {self.use!r}, options: {self.options})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["use"] = self.use
        base["options"] = list(map(lambda o: o._as_payload(), self.options))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ClassifyContext']:
        t = json.get("type")
        if t != "ClassifyContext":
            return DtlError("type property is not ClassifyContext")

        use = json.get("use")
        if use is None:
            return _property_not_found("use", json)

        use = Function.from_str(use)
        if isinstance(use, DtlError):
            return use

        options = json.get("options")
        if options is None:
            return _property_not_found("options", json)

        options = _parse_list(ClassMapping._from_payload)(options)
        if isinstance(options, DtlError):
            return options

        return ClassifyContext(use, options)
