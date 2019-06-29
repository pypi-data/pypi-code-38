def fasttext_parser(data_generator_func):
    for sentence in data_generator_func():
        data = '__label_{}  {}'.format(sentence.label, ' '.join(sentence.text))
        yield data


if __name__ == "__main__":
    from uuid import UUID

    from tokenizer_tools.tagset.offset.sequence import Sequence
    from tokenizer_tools.tagset.offset.span import Span
    from tokenizer_tools.tagset.offset.span_set import SpanSet

    data = [
        Sequence(text='我要听周杰伦的青花瓷', span_set=SpanSet([Span(7, 10, '地点')]),
                 id=UUID('59139985-367e-44c3-8540-b6340d07f79e'), label='媒体'),
        Sequence(text='我要听周杰伦的夜曲', span_set=SpanSet([Span(7, 10, '地点')]),
                 id=UUID('59139985-367e-44c3-8540-b6340d07f79e'), label='媒体')
    ]

    def faked_data_generator_func():
        return data

    result = fasttext_parser(faked_data_generator_func)

    for i in result:
        print(i)
