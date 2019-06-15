from collections.abc import MutableSequence, Iterable

from itertools import accumulate, dropwhile


class ChainList(MutableSequence, list):
    """
    This chains the sequences (ideally lists, as we will se why) provided on __init__, so that the output behaves as
    list with all the components of the sequences in order.

    This object inherits from list with the sole purpose of passing as a list in any type check. However, you have
    to bear in mind that the ChainList itself will raise an error if you try to mutate it directly.

    The sequences are provided at __init__ time and the set of sequences is not mutable per se. However, you can mutate
    the content of the sequences directly, while ChainList will preserve the set order.

    E.g.:
    # Useful when order must be preserved, but the content may change!
    DJANGO_PACKAGES = ['django.package']
    MY_PACKAGES = ['my_app']
    INSTALLED APPS = ChainList(DJANGO_PACKAGES, MY_PACKAGES)

    ...
    DJANGO_PACKAGES += ['third_party']

    The resulting INSTALLED_APPS will continue to show MY_PACKAGES after DJANGO_PACKAGES:
    ['django.package', 'third_party', 'my_app']
    """

    def __init__(self, *seqs):
        # Sequences once defined are immutable
        self._seqs = tuple(seqs)

    def _get_relative_position(self, index):
        if index < 0:
            index = (self.__len__() + index)

        try:
            seq_index, seq_abs_start = next(dropwhile(lambda r: r[1] <= index, ((i, x) for i, x in enumerate(accumulate(len(seq) for seq in self._seqs)))))
        except StopIteration:
            raise IndexError(f"IndexError: ChainList index is out of range")
        return seq_index, index - seq_abs_start

    def _get_slice(self, start, stop, step):
        l = self.__len__()

        # Deal with None (blanks) in slices
        start, stop, step = start or 0, stop or l, step or 1

        # Deal with negative numbers
        start = start if start >= 0 else l + start
        stop = stop if stop >= 0 else l + stop

        if step < 0:
            start, stop = stop - 1, start - 1

        return [self.__getitem__(i) for i in range(start, stop, step)]

    def __getitem__(self, index):
        # Address slices
        if isinstance(index, slice):
            return self._get_slice(index.start, index.stop, index.step)

        seq_index, relative_index = self._get_relative_position(index)
        return self._seqs[seq_index][relative_index]

    def __len__(self):
        return sum(len(seq) for seq in self._seqs)

    def _raise_error(self, *args, **kwargs):
        raise TypeError(f"ChainList is not directly mutable. Use MutableChainList instead")

    __setitem__ = _raise_error
    __delitem__ = _raise_error
    insert = _raise_error


class MutableChainList(ChainList):
    """
    This is a mutable version of ChainList. The only caveat to have in mind is that items inserted in a position
    that falls exactly in a frontier of two internal sequences will be inserted at the beginning of the next sequence
    (as opposed to the end of the previous sequence). This behaviour is a bit annoying, but mutating the ChainList
    itself has never been its very own purpose! That's why I made ChainList non-mutable...

    The example below shows exactly what I mean by annoying:

    >>> a = [0, 1, 2]
    >>> b = [3, 4, 5]
    >>> s = MutableChainList(a, b)

    >>> list(s)
    [0, 1, 2, 3, 4, 5]

    Let's delete the last item of a component sequence and put it back where it belongs:
    >>> del s[2]
    >>> s.insert(2, 2)

    The ChainList sequence itself preserves its original content...
    >>> list(s)
    [0, 1, 2, 3, 4, 5]

    ... but the internal components were not mutated back to their original state due to that frontier behaviour
     that I mentioned above.

    >>> a
    [0, 1]

    >>> b
    [2, 3, 4, 5]

    """

    def __setitem__(self, index, value):
        seq_index, relative_index = self._get_relative_position(index)
        self._seqs[seq_index][relative_index] = value

    def __delitem__(self, index):
        seq_index, relative_index = self._get_relative_position(index)
        del self._seqs[seq_index][relative_index]

    def insert(self, index, value):
        seq_index, relative_index = self._get_relative_position(index)
        self._seqs[seq_index].insert(relative_index, value)


def flatten(items, ignore_types=(str, bytes)):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x)
        else:
            yield x



