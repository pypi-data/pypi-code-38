from numbers import Number
from copy import copy, deepcopy

class LabeledRange:
    '''
    A helper class for keeping track of the start / stop of a given class in a
    sequence
    '''

    def __init__(self, name:str, start:int, stop:int):
        '''
        Arguments:
            name (str): name of the class
            start (int): the index at which the class starts
            stop (int): the index at which the class stops
        '''
        self.name  = name
        self.start = int(start)
        self.stop  = int(stop)


    '''
    Various conversions from LabeledRange to pythonic types
    '''
    def as_list(self):
        return [self.name, self.start, self.stop]
    def as_str_list(self):
        return [str(e) for e in self.as_list()]
    def as_tuple(self):
        return tuple(self.as_list())
    def as_dict(self):
        return dict(zip(['name', 'start', 'stop'], self.as_list()))
    def as_txt(self, delim='\t', newline='\n', newline_q=True):
        return delim.join(self.as_str_list()) + (newline if newline_q else '')
    def as_csv(self, newline='\n', newline_q=True):
        return self.as_txt(',', newline, newline_q)
    def as_tsv(self, newline='\n', newline_q=True):
        return self.as_txt('\t', newline, newline_q)
    def __hash__(self):
        return hash(self.as_tuple())
    def __repr__(self):
        return '{}{}'.format(self.__class__.__name__, self.as_tuple())
    def __str__(self):
        return self.__repr__()
    def __len__(self):
        return self.stop - self.start
    def __iter__(self):
        return (e for e in self.as_list())
    def __eq__(self, other):
        if not isinstance(other, LabeledRange):
            return False
        return (self.name  == other.name) and \
               (self.start == other.start) and \
               (self.stop  == other.stop)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, other):
        '''
        Arguments:
            other (LabeledRange / int): If other is a LabeledRange, only true
                if other is bounded by self. If other is a number, true if
                self.start <= other <= self.stop
        Returns:
            results (bool)
        '''
        if isinstance(other, Number):
            return self.start <= other <= self.stop
        if not isinstance(other, LabeledRange):
            return False
        if not other.same_q(self):
            return False
        return other.start in self and other.stop in self


    def same_q(self, other):
        '''Whether or not other is of the same class'''
        if not isinstance(other, LabeledRange):
            return False
        return self.name == other.name

    def min(self, other):
        return min([self.start, self.stop, other.start, other.stop])

    def max(self, other):
        return max([self.start, self.stop, other.start, other.stop])

    def overlap_q(self, other):
        if not self.same_q(other):
            return False
        return any([
            other.start in self, other.stop in self,
            self.start in other, self.stop in other
        ])

    def __add__(self, other):
        if not isinstance(other, LabeledRange):
            raise ValueError('{} is not a LabeledRange'.format(other))
        if not self.overlap_q(other):
            return LabeledRanges([deepcopy(self), deepcopy(other)])
        else:
           return LabeledRange(self.name, self.min(other), self.max(other))

    def __iadd__(self, other):
        if self.overlap_q(other):
            self.start = self.min(other)
            self.stop  = self.max(other)
        return self


class LabeledRanges:
    def __init__(self, ranges:list=[]):
        self.ranges = ranges

    def classes(self):
        return set([rng.name for rng in self])
    def as_list(self):
        return [rng.as_list() for rng in self]
    def as_tuple(self):
        return tuple([rng.as_tuple() for rng in self])


    @property
    def ranges(self):
        return self._ranges

    @ranges.setter
    def ranges(self, ranges):
        rngs = []
        for rng in ranges:
            if isinstance(rng, LabeledRange):
                rngs.append(rng)
            else:
                rngs.append(LabeledRange(*rng))
        self._ranges = list(set(rngs))

    @ranges.deleter
    def ranges(self):
        del self._ranges


    def __iter__(self):
        return (rng for rng in self.ranges)

    def __getitem__(self, key):
        return self.ranges[key]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = '{}('.format(self.__class__.__name__)
        if len(self.ranges) == 0:
            return s + ')'
        else:
            s += '\n'
        for i, rng in enumerate(self.ranges):
            s += '\t' + repr(rng) + '\n'
        s += ')'
        return s



    def __eq__(self, other):
        if isinstance(other, LabeledRanges):
            return all([rng in other for rng in self.ranges]) and \
                   all([rng in self for rng in other.ranges])
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


    def __contains__(self, other):
        if isinstance(other, str):
            return any([rng.name == other for rng in self])

        if isinstance(other, LabeledRange):
            return any([rng == other for rng in self])

        if isinstance(other, LabeledRanges):
            return all([self.__contains__(rng) for rng in other])

        return False

    def overlap_q(self, other):
        return any([rng.overlap_q(other) for rng in self.ranges])

    def append(self, other):

        # Append a range
        if isinstance(other, LabeledRange):
            found_q = False
            for rng in self:
                if rng.overlap_q(other):
                    found_q = True
                    rng += other
            if not found_q:
                self.ranges.append(other)

        # Map each range to the above block
        if isinstance(other, LabeledRanges):
            for rng in other:
                self.append(other)

        return self


    def __give__(self, other):
        if isinstance(other, LabeledRange):
            self.append(other)

        if isinstance(other, LabeledRanges):
            for rng in other:
                self.append(rng)

        return self.simplify()

    def simplify(self):
        for rng in self:
            self.append(rng)
        self.ranges = list(set(self.ranges))
        return self

    def __add__(self, other):
        cp = deepcopy(self)
        cp.__give__(other)
        return cp

    def __iadd__(self, other):
        self.__give__(other)
        return self

    def __radd__(self, other):
        cp = deepcopy(self)
        if not isinstance(other, LabeledRange):
            return cp
        cp.__iadd__(other)
        return cp
