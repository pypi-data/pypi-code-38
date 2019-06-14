import re

from ..tokens import FLOAT_TOKEN
from .int_token import IntTokenAligner
from .base import PatternRecognizer


class FloatToken(PatternRecognizer):

    """
    Recognize float (ex: 12.3, 1.7) in the input string
    and replace them with FLOAT_TOKEN (_float_)

    E.g.
    >>> from uttut.pipeline.ops.float_token import FloatToken
    >>> op = FloatToken()
    >>> output_seq, label_aligner = op.transform("10.7")
    >>> output_labels = label_aligner.transform([1, 1, 1, 1])
    >>> output_seq
    "_float_"
    >>> output_labels
    [1, 1, 1, 1, 1, 1, 1]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 1, 1]

    """

    _label_aligner_class = IntTokenAligner

    REGEX_PATTERN = re.compile(
        r"(?<![\.\d\uFF10-\uFF19])[\d\uFF10-\uFF19]+\.[\d\uFF10-\uFF19]+(?![\.\d\uFF10-\uFF19])",
    )
    TOKEN = FLOAT_TOKEN

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='float-token',
        )
