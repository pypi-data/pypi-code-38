from .defaults import (LABEL_ORDER, USE_OTHER_CLASS, OTHER_CLASS)
from ntai.ranges import LabeledRange, LabeledRanges
class Labeler:
    def __init__(
        self,
        label_order: str = LABEL_ORDER,
        use_other_class: bool = USE_OTHER_CLASS,
        other_class: str = OTHER_CLASS
    ):
        self.use_other_class = use_other_class
        self.other_class = other_class

        if (use_other_class):
            label_order += [other_class]
        self.label_order = label_order


    def encode_index(self, index, ranges):
        encoded = [0 for label in self.label_order]
        for _range in ranges:
            if index in _range:
                encoded[self.label_order.index(_range.name)] = 1
        if 1 not in encoded and self.use_other_class:
            encoded[self.label_order.index(self.other_class)] = 1
        return encoded

    def encode(self, sequence, ranges, offset=0):
        return [
            self.encode_index(offset+i, ranges)
            for i in range(len(sequence))
        ]

    def label(self, sequence, reference_labels):
        chromosome, start, stop, name, score, strand, *_ = sequence
        reference_ranges = reference_labels[chromosome][strand]
        sequence_ranges = LabeledRanges()
        for _range in reference_ranges:
            _class, range_start, range_stop = _range
            if not (
                start       <= range_start <= stop       or \
                start       <= range_stop  <= stop       or \
                range_start <= start       <= range_stop or \
                range_start <= stop        <= range_stop
            ):
                continue
            sequence_ranges += LabeledRange(*_range)
        return sequence_ranges

    # def decode(self, emb):
    #     pass
    # def decode_index(self, labels):
    #     self.label_order[]
