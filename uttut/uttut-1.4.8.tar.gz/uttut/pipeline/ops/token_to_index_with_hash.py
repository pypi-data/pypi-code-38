from typing import List, Tuple, Dict

from .base import Operator

from ..edit import lst2lst
from ..edit.replacement import ReplacementGroup
from .utils.consistent_hash import consistent_hash
from .token_to_index import validate_continuity, Token2IndexAligner


class Token2IndexwithHash(Operator):

    """
    Map token (str) to index (int) given token2index dictionary

    If the input token is not in dictionary, return hash(token).

    E.g.
    >>> from uttut.pipeline.ops.token_to_index_with_hash import Token2IndexwithHash
    >>> from uttut.pipeline.ops.utils.consistent_hash import consistent_hash
    >>> token2index = {'oh': 0, 'I': 1, 'like': 2, 'apples': 3}
    >>> op = Token2IndexwithHash(token2index)
    >>> output_seq, label_aligner = op.transform(['I', 'like', 'apples', '!'])
    >>> output_labels = label_aligner.transform([3, 4, 5, 6])
    >>> output_seq
    [1, 2, 3, consistent_hash('!', len(token2index))]
    >>> output_labels
    [3, 4, 5, 6]
    >>> label_aligner.inverse_transform(output_labels)
    [3, 4, 5, 6]

    """

    _input_type = list
    _output_type = list

    def __init__(self, token2index: Dict[str, int]):
        self._validate_token2index(token2index)
        self.token2index = token2index

    def _validate_token2index(self, token2index: Dict[str, int]):
        validate_continuity(token2index)

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
                index = consistent_hash(token, len(self.token2index))
            replacement_group.add(
                start=idx,
                end=idx + 1,
                new_value=[index],
                annotation='token2indexwithhash',
            )
        replacement_group.done()
        return replacement_group
