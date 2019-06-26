import os
from multiprocessing import Pool
from .defaults import (LABEL_ORDER, USE_OTHER_CLASS, OTHER_CLASS)
from ntai.ranges import LabeledRange, LabeledRanges
class Labeler:
    def __init__(
        self,
        label_order: str = LABEL_ORDER,
        use_other_class: bool = USE_OTHER_CLASS,
        other_class: str = OTHER_CLASS,
        processes: int = 1
    ):
        '''
        Arguments:
            label_order (str): the order labels should be embedded.
            use_other_class (bool): whether or not a class `"Other"` should be
                used.
            other_class (str): the class name of `"Other"`
            processes (int): number of CPU cores to use when encoding / decoding.
                By default 1. If set to None, uses all.
        '''
        if processes is None: processes = os.cpu_count()
        self.processes = processes
        self.use_other_class = use_other_class
        self.other_class = other_class

        if (use_other_class):
            if other_class not in label_order:
                label_order += [other_class]
        self.label_order = label_order

    def processes_to_use(self, n):
        '''
        Only intialize at most self.processes, but less if less is needed

        Arguments:
            n (int): number of things to process
        Returns:
            number of processes to use
        '''
        return min(n, self.processes)

    def encode_index(self, index:int, ranges) -> list:
        '''
        Arguments:
            index (int): the index to be encoded:
            ranges (LabeledRanges): the class ranges to reference when making
                the embedding for the index.
        Returns:
            encoded (list): the index encoded.
        '''
        encoded = [0 for label in self.label_order]
        for _range in ranges:
            if index in _range:
                encoded[self.label_order.index(_range.name)] = 1
        if 1 not in encoded and self.use_other_class:
            encoded[self.label_order.index(self.other_class)] = 1
        return encoded

    def encode(self, sequence:str, ranges, offset:int=0) -> list:
        '''
        Arguments:
            sequence (str): the sequence to embed.
            ranges (LabeledRanges): the reference ranges to use to generate the
                embedding of the sequence.
            offset (int): how far to offset each index. By default `0`.
        Returns:
            embedding (list): the embedded sequence.
        '''
        _range = range(len(sequence))
        if self.processes == 1:
            return [self.encode_index(offset+i, ranges) for i in _range]
        else:
            processes = self.processes_to_use(len(sequence))
            with Pool(processes=processes) as pool:
                return pool.starmap(self.encode_index, [(offset+i, ranges) for i in _range])

    def label(self, sequence:list, reference_labels:dict):
        '''
        Arguments:
            sequence (list): a list consisting of the at least the bed6
                information of the sequence e.g.
                    `[chromosome, start, stop, name, score, strand,]`

            reference_labels (dict): a dctionary consisting the following
                structure:
                    ```
                    {
                        <chromosome>: {
                            <strand>: LabeledRanges(...),
                            ...
                        }, ...
                    }
                    ```
        Returns:
            sequence_ranges (LabeledRanges): the ranges for which a given class
                appear in the provided sequence
        '''
        chromosome, start, stop, name, score, strand, *_ = sequence
        reference_ranges = reference_labels[chromosome][strand]

        if self.processes == 1:
            res = []
            for _range in reference_ranges:
                if (self._keep_range(start, stop, _range)) is not None:
                    res.append(_range)
        else:
            processes = self.processes_to_use(len(sequence))
            with Pool(processes=processes) as pool:
                res = pool.starmap(self._keep_range, [(start, stop, _range) for _range in reference_ranges])
                res = list(filter(lambda e: e is not None, res))
        return LabeledRanges(res)


    def _keep_range(self, start, stop, _range):
        '''
        Arguments:
            start (int): the start of sequence under consideration
            stop (int): the stop of sequence under consideration
            _range (list / LabeledRange): a labeled range
        Returns:
            (None / Range): None is returned in _range is not contained inside
                the range `[start, stop]`, else _range is returned
        '''
        _class, range_start, range_stop = _range
        if range_stop < start: return
        if range_start > stop: return
        if not (
            start       <= range_start <= stop       or \
            start       <= range_stop  <= stop       or \
            range_start <= start       <= range_stop or \
            range_start <= stop        <= range_stop
        ):
            return
        return _range
