from datalogue.models.transformations.commons import Transformation, DataType
from datalogue.utils import _parse_string_list, SerializableStringEnum
from datalogue.errors import _enum_parse_error, DtlError, _property_not_found, _invalid_property_type
from typing import List, Union


class Operator(SerializableStringEnum):
    """
    Operations that can be done between 2 Operands
    """
    Add = "+"
    Sub = "-"
    Div = "/"
    Mul = "*"
    Pow = "*"
    Mod = "%"

    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("operator", s)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, 'Operator']:
        return SerializableStringEnum.from_str(Operator)(string)


class Math(Transformation):
    """
    Allows to do math between nodes in the adg
    """
    type_str = "Math"

    def __init__(self, left: Union[List[str], float, int], op: Operator, right: Union[List[str], float, int], out: List[str]):
        """
        Builds a Math transformation

        :param left: Left side of the operation. Can either be a value or a path to a value in the tree
        :param op: Operator to be used to execute the operation
        :param right: Right side of the operation. Can either be a value or a path to a value in the tree
        :param out: path where to put the result of the operation
        """
        Transformation.__init__(self, Math.type_str)
        self.left = left
        self.op = op
        self.right = right
        self.out = out

    def __eq__(self, other: 'Math'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Math({self.left} {self.op.value} {self.right} -> {self.out})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["operand1"] = Math._operand_as_payload(self.left)
        base["operand2"] = Math._operand_as_payload(self.right)
        base["operator"] = self.op.value
        base["resultPath"] = self.out

        return base

    @staticmethod
    def _operand_as_payload(op: Union[List[str], float, int]) -> dict:
        if isinstance(op, list):
            return {
                "type":"Path",
                "path": op
            }
        else:
            return {
                "type": "Value",
                "value": float(op)
            }

    @staticmethod
    def _operand_from_payload(json: dict) -> Union[List[str], float, int, DtlError]:
        value = json.get("path")
        if value is not None:
            return _parse_string_list(value)

        value = json.get("value")
        if value is not None:
            return value

        return DtlError(f"Could not parse operand: {json}")

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Math']:
        right = json.get("operand2")
        if right is None:
            return _property_not_found("operand1", json)

        right = Math._operand_from_payload(right)
        if isinstance(right, DtlError):
            return right

        left = json.get("operand1")
        if left is None:
            return _property_not_found("operand3", json)

        left = Math._operand_from_payload(left)
        if isinstance(left, DtlError):
            return left

        op = json.get("operator")
        if op is None:
            return _property_not_found("operator", json)

        op = Operator.from_str(op)
        if isinstance(op, DtlError):
            return op

        out = json.get("resultPath")
        if out is None:
            return _property_not_found("resultPath", json)

        out = _parse_string_list(out)
        if isinstance(out, DtlError):
            return out

        return Math(left, op, right, out)
