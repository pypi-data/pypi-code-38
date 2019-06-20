from typing import List, Tuple

from .base import Operator
from .tokens import END_TOKEN
from .add_sos_eos import AddSosEosAligner
from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup


class AddEndToken(Operator):

    """
    Add end token (<eos>) to a sequence.

    E.g.
    >>> from uttut.pipeline.ops.add_sos_eos import AddSosEos
    >>> op = AddEndToken()
    >>> output_seq, label_aligner = op.transform(
        ['I', 'have', '10.7', 'dollars', '.'])
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5])
    >>> output_seq
    ['I', 'have', '10.7', 'dollars', '.', '<eos>']
    >>> output_labels
    [1, 2, 3, 4, 5, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 4, 5]

    """

    _input_type = list
    _output_type = list

    def __init__(self, end_token: str = END_TOKEN):
        self.end_token = self._validate_end_token(end_token)

    def _validate_end_token(self, end_token: str):
        if end_token is None:
            raise ValueError("The end token can not be None.")

        if not isinstance(end_token, str):
            raise TypeError("The end token should be a string.")

        if len(end_token) == 0:
            raise ValueError("The end token should not be an empty string.")

        return end_token

    def _transform(self, input_sequence: List[str]) -> Tuple[List[str], 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = lst2lst.apply(input_sequence, forward_replacement_group)

        label_aligner = AddSosEosAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_lst: List[str]) -> ReplacementGroup:
        seqlen = len(input_lst)
        replacement_group = ReplacementGroup.add_all(
            [(seqlen, seqlen, [self.end_token], 'add-end-token')],
        )
        return replacement_group
