from typing import List

from ..ops.base import Operator, LabelAligner


class MockLabelAligner(LabelAligner):

    def _transform(self, labels):
        return labels

    def _inverse_transform(self, labels):
        return labels


class Str2Str(Operator):

    _input_type = str
    _output_type = str

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _transform(self, input_sequence: str):  # type: ignore
        return input_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(input_sequence),
        )


class Lst2Lst(Operator):

    _input_type = list
    _output_type = list

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _transform(self, input_sequence: List[str]):  # type: ignore
        return input_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(input_sequence),
        )


class Str2Lst(Operator):

    _input_type = str
    _output_type = list

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _transform(self, input_sequence: str):  # type: ignore
        output_sequence = list(input_sequence)
        return output_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(output_sequence),
        )


class Lst2Str(Operator):

    _input_type = list
    _output_type = str

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _transform(self, input_sequence: List[str]):  # type: ignore
        output_sequence = ''.join(input_sequence)
        return output_sequence, MockLabelAligner(
            edit={},
            input_sequence=input_sequence,
            output_length=len(output_sequence),
        )
