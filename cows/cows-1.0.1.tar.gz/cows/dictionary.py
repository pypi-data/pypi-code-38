from .trie import Trie


class Dict:
    """Creates a dict-like object which checks has potentially ambiguous keys

    This class provides a key/value store where the keys are strings and may
    contain wildcards.  Unlike the builtin ``dict`` type where setting a key
    overwrites the existing associated value if it exists, this class allows
    for a user-defined updating function, ``updater``.  Since a given key
    may match more than one key in the Dict (due to wildcards), a ``selector``
    function will be passed the list of matches which will select which to pass
    to ``updater``.

    Args:
        selector (func): Called when ``__setitem__`` is called with `key`
            and a (possibly wildcard) match to `key` exists.

            Must accept one argument, an iterable of ``(key, value)`` matches,
            and return a single element from the iterator that will be updated
            with ``updater``.
        updater (func): Called when ``__setitem__`` is called with `key` and
            ``value`` and a (possibly ambiguous) match to `key` exists.

            Must accept three arguments ``match``, ``current_value``, and
            ``new_value``.  ``match`` and ``current_value`` will be passed the
            key and value returned by the ``selector`` and ``new_value`` will
            be passed the ``value`` passed to ``__setitem__``.

            Returns the value to set the value associated with ``match`` to.
        **kwargs: Passed to underlying Trie


    Example:
        .. code-block:: python

            import cows

            def increment(match, old_value, new_value):
                return old_value + new_value

            my_dict = cows.Dict(updater=increment)
            my_dict['ABC'] = 1
            my_dict['DEF'] = 2
            my_dict['AB*'] = 10

            for k, v in sorted(my_dict.items()):
                print(f'{k} --> {v}')

        This code would output:

        .. code-block:: none

            ABC --> 11
            DEF --> 2

        Now consider a more complicated example:

        .. code-block:: python

            ...
            my_dict = cows.Dict(updater=increment)
            my_dict['ABC'] = 1
            my_dict['*EF'] = 2
            my_dict['GHF'] = 3
            my_dict['G*F'] = 5

        Here the setting of ``G*F`` matches both ``*EF`` and ``GHF``.  By
        default, the first lexicographic match (in this case ``*EF``) is chosen
        for update:

        .. code-block:: none

            *EF --> 7
            ABC --> 1
            GHF --> 3

        However, this behavior can be overridden by passing a function as the
        ``selector`` parameter.  This function must take one parameter,
        ``matches`` which yields ``(key, value)`` pairs for each matching entry
        and return the key of the desired pair.

        For example, this selector chooses the _last_ match when sorted in
        lexicographic order:

        .. code-block:: python

            ...
            def last_match(matches):
                return sorted(matches, key=lambda m: m[0], reverse=True)[0]

            my_dict = cows.Dict(updater=increment, selector=last_match)
            ...


        This will output:

        .. code-block:: none

            *EF --> 2
            ABC --> 1
            GHF --> 8

    """
    def __init__(self, selector=None, updater=None, **kwargs):
        initialize = kwargs.pop('initialize', None)

        def _default_selector(matches):
            return sorted(matches, key=lambda m: m[0])[0]

        self.selector = selector or _default_selector
        self.updater = updater
        self.trie = Trie(**kwargs)

        # This needs to override the same loop in Trie because
        # __setitem__ processes calls before calling the same method in
        # Trie
        if initialize:
            for init_key, init_val in initialize:
                self[init_key] = init_val

    def keys(self):
        """
        Returns:
            The keys in the dictionary.

        """
        return self.trie.keys()

    def values(self):
        """
        Returns:
            The values in the dictionary.

        """
        return self.trie.values(extract_values=True)

    def items(self):
        """
        Returns:
            ``(key, value)`` tuples for each association in the dictionary.

        """
        return self.trie.items(extract_values=True)

    def __iter__(self):
        """Yields the keys in the dictionary"""
        yield from self.keys()

    def __setitem__(self, key, value):
        """Sets a value in the dictionary.

        Sets `key` to `value` if no match for `key` already exists.  If matches
        do exist, one is selected with ``self.selector`` function and is
        optionally updated with the ``self.updater`` function.

        Args:
            key (str): The key to set
            value (obj): The value to set

        """
        matches = [m for m in self.trie.get_matches(key)]
        if matches:
            key, current_value = self.selector(matches)
            if self.updater:
                value = self.updater(key, current_value.value, value)
        self.trie[key] = value

    def __getitem__(self, key):
        """Gets items matching ``key``.

        Args:
            key (str): The key string to match

        Yields:
            The values that match ``key``.  Order is not guaranteed.

        """
        yield from (m[1].value for m in self.trie.get_matches(key))

    def __len__(self):
        """Returns the number of elements in the dictionary."""
        return len([l for l in self.values()])

    def __repr__(self):
        """Returns the representation of the dictionary"""
        return f'cows.Dict()'
