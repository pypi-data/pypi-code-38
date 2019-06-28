from tokenizer_tools.tagset.NER.base_tagset import BaseTagSet
from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span


class BILUOEncoderDecoder(BaseTagSet):
    # O is very easy confused with zero, using oscar instead in the code
    oscar = 'O'

    def generate_tag(self, prefix):
        if self.tag_name == self.oscar:
            # O tag is very special, it always return O
            return self.oscar

        if self.tag_name is not None:
            tag = "{}-{}".format(prefix, self.tag_name)
        else:
            # if tag_name is None, no more tag_name in tag
            tag = prefix

        return tag

    def encode(self, sequence):
        len_of_sequence = len(sequence)

        if len_of_sequence == 1:
            return [self.generate_tag('U')]

        elif len_of_sequence == 2:
            return [self.generate_tag('B'), self.generate_tag('L')]

        else:
            return [self.generate_tag('B')] + [self.generate_tag('I')] * (len_of_sequence - 2) + [self.generate_tag('L')]

    def decode(self, sequence):
        pass

    def all_tag_set(self):
        tag_set = {self.generate_tag(i) for i in 'BILU'}
        tag_set_oscar = {self.oscar}
        tag_set.update(tag_set_oscar)
        return tag_set


class BILUOSequenceEncoderDecoder(object):
    # O is very easy confused with zero, using oscar instead in the code
    oscar = 'O'

    prefix_set = set('BILU')

    def __init__(self, *args, **kwargs):
        self.ignore_error = kwargs.get('ignore_error', True)

    def parse_tag(self, tag):
        if tag == self.oscar:
            return self.oscar, None

        # set maxsplit to 1, so raw_tag_name can contains '-' char legally
        raw_prefix, raw_tag_name = tag.split('-', maxsplit=1)

        prefix = raw_prefix.strip()
        tag_name = raw_tag_name.strip()

        if prefix and tag_name and prefix in self.prefix_set:
            return prefix, tag_name

        raise ValueError("tag: {} is not a avoid tag".format(tag))

    def is_prefix_legal(self, previous, current):
        node = (previous, current)

        legal_set = {
            ('B', 'I'),
            ('B', 'L'),
            ('I', 'I'),
            ('I', 'L'),
            (self.oscar, 'B'),
            ('L', self.oscar),
            (self.oscar, 'U'),
            ('U', self.oscar),
            ('U', 'B'),
            ('L', 'U'),
            ('U', 'U')
        }

        return node in legal_set

    def decode_to_offset(self, sequence):
        offset_list = []

        tag_prefix_cache = []
        tag_name_cache = None

        for index, item in enumerate(sequence):
            prefix, tag_name = self.parse_tag(item)

            if not tag_prefix_cache:
                if prefix == self.oscar:
                    # ignore it
                    continue
                elif prefix == 'B':
                    tag_name_cache = tag_name
                    tag_prefix_cache.append(prefix)
                elif prefix == 'U':
                    offset_list.append(
                        (index, index + 1, tag_name)
                    )
                else:
                    if not self.ignore_error:
                        raise ValueError("sequence: {} is not a valid tag sequence".format(sequence[:index + 1]))
                    else:
                        continue
            else:
                last_tag_prefix = tag_prefix_cache[-1]

                if not self.is_prefix_legal(last_tag_prefix, prefix):
                    raise ValueError(
                        "sequence: {} is not a valid tag sequence".format(
                            sequence[:index + 1]))

                if prefix == 'L':
                    if tag_name_cache == tag_name:
                        offset_list.append(
                            (index - len(tag_prefix_cache), index + 1, tag_name_cache)
                        )

                        # clean up
                        tag_prefix_cache = []
                        tag_name_cache = None
                    else:
                        raise ValueError("sequence: {} is not a valid tag sequence".format(sequence[:index + 1]))
                elif prefix == 'I':
                    if tag_name_cache == tag_name:
                        tag_prefix_cache.append(prefix)
                    else:
                        raise ValueError("sequence: {} is not a valid tag sequence".format(sequence[:index + 1]))

        return offset_list

    def to_offset(self, sequence, text, label=None):
        seq = Sequence(text)

        plain_offset_list = self.decode_to_offset(sequence)

        for offset in plain_offset_list:
            seq.span_set.append(Span(offset[0], offset[1], offset[2]))

        seq.label = label

        return seq


if __name__ == '__main__':
    decoder = BILUOSequenceEncoderDecoder()
    result = decoder.decode_to_offset(['U-XX'])
    print(result)
    assert result == [(0, 1, 'XX')]

    result = decoder.decode_to_offset(['U-XX', 'U-YY'])
    print(result)
    assert result == [(0, 1, 'XX'), (1, 2, 'YY')]

    result = decoder.decode_to_offset(['B-XX', 'I-XX', 'L-XX'])
    print(result)
    assert result == [(0, 3, 'XX')]
