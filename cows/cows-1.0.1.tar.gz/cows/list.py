from .trie import Trie


class List:
    """A list for storing potentially ambiguous strings.

    This class allows strings with ambiguous characters to be searched.
    Insertion via :meth:`.append`, :meth:`.extend`, and :meth:`.insert`
    function normally, simply inserting values into a list.  Accessor methods
    :meth:`.index`, :meth:`.count`, and :meth:`.__contains__` all take into
    account ambiguous characters, however.

    Example:

    .. code-block:: python

        import cows

        l = cows.List(['ABCD', 'ABC*', 'DEFG'])
        print(l)
        # prints: cows.List(['ABCD', 'ABC*', 'DEFG'])

        l.insert(2, '****')

        print(l)
        # print: cows.List(['ABCD', 'ABC*', '****', 'DEFG'])

        print(l.index('D***'))
        # prints: 2

        print(l.count('A***'))  # 3
        # prints: 3
    """
    def __init__(self, iterable=None):
        self.list = list(iterable) if iterable else []
        self.trie = Trie(initialize=[
            (element, True) for element in self.list
        ] if iterable else None)

    def __contains__(self, key):
        """Returns if `key` is in the list taking into account ambiguity"""
        return key in (m[0] for m in self.trie.get_matches(key))

    def __iter__(self):
        """Yields items in the list"""
        yield from self.list

    def __repr__(self):
        """Returns the representation of the list"""
        return f'cows.List({[e for e in self]})'

    def __len__(self):
        """Returns the number of elements in the list"""
        return len(self.list)

    def append(self, value):
        """Appends ``value`` to the list"""
        self.insert(len(self), value)

    def extend(self, iterable):
        """Appends all elements in ``iterable`` to the list"""
        for element in iterable:
            self.append(element)

    def insert(self, i, value):
        """Inserts ``value`` at position ``i`` in the list"""
        self.list.insert(i, value)
        self.trie[value] = True

    def index(self, value, start=None, end=None):
        """Finds the first index of ``value`` in the list.

        Determines if ``value`` is in the list taking into account ambiguity
        and returns the first matching index.

        If ``start`` and/or ``end`` is specified, only searches that portion of
        the list using the slice operator.  If ``value`` is not found raises a
        ValueError.

        Example:

            .. code-block:: python

                l = cows.List(['ABCD', 'ABC*', '****', 'DEFG'])

                print(l.index('D***'))

            The output of the print statement is ``2`` since the first match
            for ``D***`` is at position 2 (with a value of ``****``).


        Args:
            value (str): The value for which to search.
            start (int): The minimum index to start searching.
            end (int): The maximum index to search through

        Returns:
            The minimum index that matches ``value``

        Raises:
            ValueError: If no matches for ``value`` are found.

        """

        if start is None:
            start = 0
        if end is None:
            end = len(self.list)

        matches = [m[0] for m in self.trie.get_matches(value)]
        try:
            return min([
                self.list[start:end].index(match) + start for match in matches
                if match in self.list[start:end]
            ])
        except ValueError:
            raise ValueError(f'No matches for {value} found')

    def count(self, value):
        """Counts the number of times ``value`` occurs in the list.

        This method takes into account ambiguity.

        """

        matches = [m[0] for m in self.trie.get_matches(value)]
        return sum([self.list.count(match) for match in matches])

    def reverse(self):
        self.list.reverse()
