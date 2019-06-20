from typing import List, Tuple

from .base import Operator, LabelAligner
from .tokens import START_TOKEN, END_TOKEN
from .label_transducer import get_not_entity
from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup
from ..edit.label_propagation import propagate_by_replacement_group


class AddSosEos(Operator):

    """
    Add start token (<sos>) and end token (<eos>) to a sequence.

    E.g.
    >>> from uttut.pipeline.ops.add_sos_eos import AddSosEos
    >>> op = AddSosEos()
    >>> output_seq, label_aligner = op.transform(
        ['I', 'have', '10.7', 'dollars', '.'])
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5])
    >>> output_seq
    ['<sos>', 'I', 'have', '10.7', 'dollars', '.', '<eos>']
    >>> output_labels
    [0, 1, 2, 3, 4, 5, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 4, 5]

    """

    _input_type = list
    _output_type = list

    def __init__(
            self,
            start_token: str = START_TOKEN,
            end_token: str = END_TOKEN,
        ):
        self.start_token = start_token
        self.end_token = end_token

    def _transform(self, input_sequence: List[str]) -> Tuple[List[str], 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = lst2lst.apply(input_sequence, forward_replacement_group)

        label_aligner = AddSosEosAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(
            self,
            input_lst: List[str],
            annotation: str = None,
        ) -> ReplacementGroup:

        seqlen = len(input_lst)
        replacement_group = ReplacementGroup.add_all(
            [
                (0, 0, [self.start_token]),  # insert start token
                (seqlen, seqlen, [self.end_token]),  # insert end token
            ],
        )
        return replacement_group


class AddSosEosAligner(LabelAligner):

    def _transform(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)

    def _inverse_transform(self, labels: List[int]) -> List[int]:
        inverse_replacement_group = lst2lst.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)
