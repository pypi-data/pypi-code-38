_EMPTY = object()


class Trie:
    """A trie which has accessors for ambiguous lookups.

    This class is the basis of all other cows classes.  It stores *all*
    strings which have been inserted, not taking into account ambiguity.  No
    special methods (starting & ending with double underscores) take into
    account ambiguity.  To search the trie for ambiguous matches, use
    :meth:`.get_matches`.

    Example:

        .. code-block:: python

            import cows

            t = cows.Trie()
            t['ABCD'] = 1
            t['DE*G'] = 5

            print(f'Matches for ABC* {list(t.get_matches("ABC*"))}')
            print(f'Matches for D*FG {list(t.get_matches("D*FG"))}')

        Outputs:

        .. code-block:: none

            Matches for ABC* [('ABCD', cows.Trie(D, 1))]
            Matches for D*FG [('DE*G', cows.Trie(G, 5))]

    Args:
        key (char): The character representing the trie node.
        value (object): An arbitrary Python object representing the data at the
            trie node.
        wildcard (char): The character representing ambiguity.
        initialize (tuple): Pairs of values with which to initialize the trie.

    Note:
        Consider using the other cows data structures, which are more
        intuitive, before using a Trie.


    """
    def __init__(self, key=None, value=_EMPTY, wildcard='*',
                 initialize=None):
        self.children = {}
        self.key = key
        self.value = value
        self.wildcard = wildcard

        if initialize:
            for init_key, init_val in initialize:
                self[init_key] = init_val

    def __getitem__(self, key):
        """Gets an item from the trie.

        Searches the trie for ``key``.  Note this does **not** take into
        account ambiguity, and will only find an exact match.  For ambiguous
        searching, use :meth:`.get_matches`.

        Args:
            key (str): The key to search for

        Returns:
            The matching :class:`.Trie` node if ``key`` was found, else
            ``None``
        """
        node = self
        while True:
            if not key:
                return node
            prefix, rest = key[0], key[1:]
            node = node.children[prefix]
            key = rest

    def __setitem__(self, key, value):
        """Sets a key/value pair in the trie.

        Sets the value of ``key`` to ``value``.  Note this will affect exactly
        one trie node and does not take into account ambiguity.  For a data
        structure that implements setting with ambiguity use :class:`.Dict`.

        Args:
            key (str): The key to set.
            value (obj): The data to associate with ``key``

        """
        node = self
        while True:
            prefix, rest = key[0], key[1:]
            node = node.children.setdefault(
                prefix, Trie(prefix, wildcard=self.wildcard)
            )
            if not rest:
                node.value = value
                break
            key = rest

    def __repr__(self):
        """Returns the representation of the trie"""
        return f'cows.Trie({self.key}, {self.value})'

    def __len__(self):
        """Returns the number of nodes in the trie"""
        return len(list(self.items()))

    def __iter__(self):
        yield from self.keys()

    def keys(self):
        """Yields the keys in the trie"""
        yield from (item[0] for item in self.items())

    def values(self, extract_values=False):
        """Yields the values in the trie"""
        yield from (
            item[1] for item in self.items(extract_values=extract_values)
        )

    def items(self, extract_values=False):
        """Gets all items in the trie.

        Yields:
            ``(node_key, node)`` pairs of all items.
        """
        to_visit = [(self.key or '', self)]

        while True:
            try:
                node_key, node = to_visit.pop()
            except IndexError:
                break

            if node.value != _EMPTY:
                yield (node_key, node.value if extract_values else node)
            for child in node.children.values():
                to_visit.append((node_key + child.key, child))

    def children_matching(self, prefix):
        """Gets all child nodes matching the single character prefix.  If the
        character is a wildcard, it will return all children and if a wildcard
        is included in the children, it will be included.

        For example, if the children are:

        ``[Trie('A'), Trie('B'), Trie('C'), Trie('*')]``

        where ``*`` is the wildcard, passing ``A`` to this method
        will return:

        ``[Trie('A'), Trie('*')]``.

        Args:
            prefix (char): A single character for which to search within
                children.

        Yields:
            Child(ren) matching ``prefix``

        Raises:
            ValueError
                If ``prefix`` is not a string of exactly one character.


        """
        if not (isinstance(prefix, str) and len(prefix) == 1):
            raise ValueError(
                f'Prefix must be a single character, not {prefix}')

        if prefix == self.wildcard:
            yield from self.children.values()
        else:
            if prefix in self.children:
                yield self.children[prefix]
            if self.wildcard in self.children:
                yield self.children[self.wildcard]

    def get_matches(self, key):
        """Searches the trie for strings matching ``key``.

        Example:
            If the trie contains ``ABCD``, ``ABCA``, and ``CBC*``, the
            key ``ABC*`` will return ``ABCD`` and ``ABCA``.

        Args:
            key (str): The string for which to search for matches in the trie

        Yields:
            ``(key, value)`` tuples for nodes that match ``key``.

        Note:
            The order of yielded matches is not defined and is not guaranteed
            to be consistent.

        """
        next_visit = ('', key, self)
        to_visit = []

        while True:
            prev, key, node = next_visit
            prefix, rest = key[0], key[1:]
            matching_children = node.children_matching(prefix)

            if not rest:
                yield from [
                    (prev + c.key, c) for c in matching_children
                    if c.value != _EMPTY
                ]
            else:
                to_visit.extend(
                    (prev + c.key, rest, c) for c in matching_children
                )

            try:
                next_visit = to_visit.pop()
            except IndexError:
                break
