from datalogue.errors import DtlError, _enum_parse_error
from datalogue.utils import _parse_string_list, SerializableStringEnum
import abc
from typing import Union, List


class Transformation(abc.ABC):

    type_field = "type"

    def __init__(self, transformation_type: str):
        self.type = transformation_type
        super().__init__()

    def _base_payload(self) -> dict:
        return dict([(Transformation.type_field, self.type)])

    @abc.abstractmethod
    def _as_payload(self) -> dict:
        """
        Represents the transformation in its dictionary construction

        :return:
        """


class DataType(SerializableStringEnum):
    """
    Data Types that can be specified in the pipeline
    """
    String = "String"
    Boolean = "Boolean"
    Integer = "Integer"
    DateTime = "DateTime"
    Double = "Double"

    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("data type", s)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, 'DataType']:
        return SerializableStringEnum.from_str(DataType)(string)


def _array_from_dict(json: dict, transformation_type: str, array_field_key: str) -> Union[DtlError, List[str]]:
    """
    Generic method to extract an array from a json transformation dictionary

    :param json: dictionary built from json
    :param transformation_type: type of the transformation
    :param array_field_key: key at which the array is
    :return:
    """
    if json.get(Transformation.type_field) != transformation_type:
        return DtlError("Dictionary input is not of type %s" % transformation_type)

    array_field = json.get(array_field_key)
    if array_field is None:
        return DtlError("'%s' is missing from the json transformation" % array_field_key)

    array = _parse_string_list(array_field)

    if isinstance(array, DtlError):
        return array

    return array