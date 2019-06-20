from typing import List, Tuple

from .base import Operator, LabelAligner
from .tokens import PAD_TOKEN
from .label_transducer import get_not_entity

from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup
from ..edit.label_propagation import propagate_by_replacement_group


class Pad(Operator):

    """
    Pad sequence to the given length using PAD_TOKEN (<pad>).

    E.g.
    >>> from uttut.pipeline.ops.pad import Pad
    >>> op = Pad(5)
    >>> output_seq, label_aligner = op.transform(['apple'])
    >>> output_labels = label_aligner.transform([1])
    >>> output_seq
    ['apple', '<pad>', '<pad>', '<pad>', '<pad>']
    >>> output_labels
    [1, 0, 0, 0, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1]

    """

    _input_type = list
    _output_type = list

    def __init__(self, maxlen: int, pad_token: str = PAD_TOKEN):
        self.pad_token = pad_token
        self.maxlen = maxlen

    def _transform(self, input_sequence: List[str]) -> Tuple[List[str], 'LabelAligner']:

        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = lst2lst.apply(input_sequence, forward_replacement_group)

        label_aligner = PadAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )

        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_lst: List[str]) -> ReplacementGroup:

        seqlen = len(input_lst)
        diff = self.maxlen - seqlen

        if seqlen == self.maxlen:
            replacement_group = ReplacementGroup.add_all([])
        elif seqlen > self.maxlen:
            replacement_group = ReplacementGroup.add_all(
                [(self.maxlen, seqlen, [])],
            )
        else:
            replacement_group = ReplacementGroup.add_all(
                [(seqlen, seqlen, [self.pad_token] * diff)],
            )
        return replacement_group


class PadAligner(LabelAligner):

    def _transform(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels, output_size)

    def _inverse_transform(self, labels: List[int]) -> List[int]:
        inverse_replacement_group = lst2lst.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels, output_size)
