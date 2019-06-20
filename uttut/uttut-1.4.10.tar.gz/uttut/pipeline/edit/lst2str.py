from typing import List

from .span import SpanGroup


def apply(input_lst: List[str], span_group: SpanGroup) -> str:

    _validate_compatibility(input_lst, span_group)

    # apply span group (list -> str)
    output_str = ''.join(input_lst)

    return output_str


def _validate_compatibility(input_lst: List[str], span_group: SpanGroup):
    if len(input_lst) != len(span_group):
        raise ValueError('Input list and span group have different length.')
    for i, (token, span) in enumerate(zip(input_lst, span_group)):
        if len(token) != span.end - span.start:
            raise ValueError(f"{i}-th element is not compatible.")
