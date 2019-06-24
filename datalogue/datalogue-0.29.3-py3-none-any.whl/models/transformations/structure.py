from typing import List, Union, Dict, Optional
from datalogue.errors import DtlError, _property_not_found, _enum_parse_error, _invalid_property_type
from datalogue.models.transformations.commons import Transformation, DataType
from datalogue.utils import _parse_string_list, SerializableStringEnum, _parse_list


class PickStrategy(SerializableStringEnum):
    """
    Data Types that can be specified in the pipeline
    """
    HighScore = "HighScore"
    Non = "None"
    Random = "Random"
    All = "All"

    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("PickStrategy", s)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, 'PickStrategy']:
        return SerializableStringEnum.from_str(PickStrategy)(string)


class ClassNodeDescription:
    """
    Description of a node that will be selected from a class and that specifies its path location in the output.
    """
    def __init__(self, path: List[str], tag: str, pick_strategy: PickStrategy, data_type: DataType = DataType.String):
        """
        Builds a ClassNodeDescription to be used in the Structure transformation.

        :param path: path of the node to be created
        :param tag: class of the value to be picked up
        :param pick_strategy: How to pick up the value to be used
        :param data_type: Type of the output value
        """
        self.path = path
        self.tag = tag
        self.pick_strategy = pick_strategy
        self.data_type = data_type

    def __eq__(self, other: 'ClassNodeDescription'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ClassNodeDescription(path: {self.path}, tag: {self.tag}, strategy: {self.pick_strategy}, dataType: {self.data_type})"

    def _as_payload(self) -> dict:
        return {
            "type": "Class",
            "outputDataType": self.data_type.value,
            "outputPath": self.path,
            "class": self.tag,
            "pickStrategy": self.pick_strategy.value
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ClassNodeDescription']:
        if json.get("type") is None and json.get("type") != "Class":
            return DtlError("Invalid json payload type for ClassNodeDescription")

        path = json.get("outputPath")
        if path is None:
            return _property_not_found("outputPath", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        tag = json.get("class")
        if tag is None:
            return _property_not_found("class", json)

        pick = json.get("pickStrategy")
        if pick is None:
            return _property_not_found("pickStrategy", json)

        pick = PickStrategy.from_str(pick)
        if isinstance(pick, DtlError):
            return pick

        data_type = json.get("outputDataType")
        if data_type is not None:
            data_type = DataType.from_str(data_type)
            if isinstance(data_type, DtlError):
                return data_type
        else:
            data_type = DataType.String

        return ClassNodeDescription(path, tag, pick, data_type)


class PathNodeDescription:
    """
    Instruction to copy a node from input into the output
    """
    def __init__(self, path: List[str], output_path: List[str], output_data_type: DataType = DataType.String,
                 is_output_array: bool = False):
        """
        Builds a PathNodeDescription to be used in the Structure transformation.

        :param path: path of the node to be used as input
        :param output_path: path of the node to be created in the output
        :param output_data_type: type for the node to be used as output
        :param is_output_array: will the output contain several nodes with identical paths
        """
        self.path = path
        self.output_path = output_path
        self.output_dataType = output_data_type
        self.is_output_array = is_output_array

    def __eq__(self, other: 'PathNodeDescription'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"PathNodeDescription(path: {self.path}, output_path: {self.output_path}, output_dataType: {self.output_dataType}, is_output_array: {self.is_output_array})"

    def _as_payload(self) -> dict:
        return {
            "type": "Path",
            "path": self.path,
            "outputPath": self.output_path,
            "outputDataType": self.output_dataType.value,
            "outputIsArray": self.is_output_array
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'PathNodeDescription']:
        if json.get("type") is None and json.get("type") != "Path":
            return DtlError("Invalid json payload type for PathNodeDescription")

        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        output_path = json.get("outputPath")
        if output_path is None:
            return _property_not_found("outputPath", json)

        output_path = _parse_string_list(output_path)
        if isinstance(output_path, DtlError):
            return output_path

        is_output_array = json.get("is_output_array")
        if is_output_array is None:
            is_output_array = False

        output_data_type = json.get("outputDataType")
        if output_data_type is None:
            return _property_not_found("output_dataType", json)

        output_data_type = DataType.from_str(output_data_type)
        if isinstance(output_data_type, DtlError):
            return output_data_type

        return PathNodeDescription(path, output_path, output_data_type, is_output_array)


class Structure(Transformation):
    """
    Enables to pick nodes based on their class or path and organize them as you wish for the output

    When using a class to select a node, there are different strategies that can be used to pick it.

       * HighScore: Uses the node classified with the highest score
       * None: If several matches do not use any
       * Random: Just picks one
       * All: Picks all

    If no nodes with the specified class or path are found, the output node will be created with an empty value.

    If a cast fails, the element is dropped from the stream.
    """

    type_str = "Structure"

    def __init__(self, structure: List[Union[ClassNodeDescription, PathNodeDescription]]):
        """
        Builds StructureByClass transformation

        :param structure: List of nodes to include in the output
        """
        Transformation.__init__(self, Structure.type_str)
        self.structure = structure

    def __eq__(self, other: 'Structure'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Structure(structure: {self.structure!r})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["outputSchema"] = list(map(lambda s: s._as_payload(), self.structure))
        return base

    @staticmethod
    def _parse_class_or_path_description(json: Dict) -> Union[ClassNodeDescription, PathNodeDescription, DtlError]:
        description_type = json.get("type")
        if json.get("type") is None:
            return DtlError("Invalid node description inside the Structure transformation")

        if description_type == "Class":
            return ClassNodeDescription._from_payload(json)
        elif description_type == "Path":
            return PathNodeDescription._from_payload(json)
        else:
            return DtlError("Invalid type for the node description")

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Structure']:
        structure = json.get("outputSchema")
        if structure is None:
            return _property_not_found("outputSchema", json)

        structure = _parse_list(Structure._parse_class_or_path_description)(structure)
        if isinstance(structure, DtlError):
            return structure

        return Structure(structure)
