from tokenizer_tools.tagset.NER.BILUO import BILUOEncoderDecoder
from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span


def offset_to_biluo(sequence):
    encoding = ['O'] * len(sequence.text)

    for span in sequence.span_set:
        encoder = BILUOEncoderDecoder(span.entity)
        entity_text = sequence.text[span.start: span.end]
        entity_encoding = encoder.encode(entity_text)

        encoding[span.start: span.end] = entity_encoding

    return encoding


if __name__ == "__main__":
    seq = Sequence("王小明在北京的清华大学读书。")
    seq.span_set.append(Span(0, 3, 'PERSON', '王小明'))
    seq.span_set.append(Span(4, 6, 'GPE', '北京'))
    seq.span_set.append(Span(7, 11, 'ORG', '清华大学'))

    check_result = seq.check_span_set()
    print(check_result)

    encoding = offset_to_biluo(seq)
    print(encoding)
