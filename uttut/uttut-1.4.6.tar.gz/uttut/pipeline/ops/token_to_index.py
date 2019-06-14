from typing import List, Tuple, Dict

from .base import Operator, NullLabelAligner
from .tokens import UNK_TOKEN

from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup


def validate_continuity(token2index: Dict[str, int]):
    indices = set([index for _, index in token2index.items()])
    if len(token2index) != len(indices):
        raise ValueError("duplicated index")

    start_from_zero = min(indices) == 0
    end_at_size = max(indices) == len(token2index) - 1
    if not (start_from_zero and end_at_size):
        raise ValueError("indices are not continuous.")


class Token2Index(Operator):

    """
    Map token (str) to index (int) given token2index dictionary

    Note that token2index should have UNK_TOKEN (<unk>).

    E.g.
    >>> from uttut.pipeline.ops.token_to_index import Token2Index
    >>> op = Token2Index({'unk': 0, 'I': 1, 'like': 2, 'apples': 3}, 'unk')
    >>> output_seq, label_aligner = op.transform(['I', 'like', 'apples', 'oh'])
    >>> output_labels = label_aligner.transform([3, 4, 5, 6])
    >>> output_seq
    [1, 2, 3, 0]
    >>> output_labels
    [3, 4, 5, 6]
    >>> label_aligner.inverse_transform(output_labels)
    [3, 4, 5, 6]

    """

    _input_type = list
    _output_type = list

    def __init__(self, token2index: Dict[str, int], unk_token: str = UNK_TOKEN):
        self._validate_token2index(token2index, unk_token)
        self.token2index = token2index
        self.unk_token = unk_token

    def _validate_token2index(self, token2index: Dict[str, int], unk_token: str):
        validate_continuity(token2index)
        if unk_token not in token2index:
            raise KeyError(f"token2index should have token {unk_token}")

    def _transform(self, input_sequence: List[str]) -> Tuple[List[int], 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = lst2lst.apply(input_sequence, forward_replacement_group)

        label_aligner = Token2IndexAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_lst: List[str]) -> ReplacementGroup:

        replacement_group = ReplacementGroup()
        for idx, token in enumerate(input_lst):
            if token in self.token2index:
                index = self.token2index[token]
            else:
                index = self.token2index[self.unk_token]
            replacement_group.add(
                start=idx,
                end=idx + 1,
                new_value=[index],
                annotation='token2index',
            )
        replacement_group.done()
        return replacement_group


Token2IndexAligner = NullLabelAligner
