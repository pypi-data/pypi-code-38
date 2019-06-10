"""
Defines tools for filtering file names out of the compare result
"""

class Filters(object):
    """
    Holds multiple functions for filtering out file names from
    the :py:func:`dynamo_consistency.datatypes.compare` function.

    :param args: An optional list of functions to build the filter
    """

    def __init__(self, *args):
        self._funcs = []
        for arg in args:
            self.add(arg)


    def protected(self, file_name):
        """
        Checks if any of the filtering functions passed here return ``True``.
        Exceptions are not handled here.

        :param str file_name: A file to check against all other filters
        :returns: Result of OR of all stored functions
        :rtype: bool
        """
        for filt in self._funcs:
            if filt(file_name):
                return True

        return False


    def add(self, func):
        """
        The function must take a single argument, which is passed
        by the ``__call__`` operator of this class.
        Exceptions should be handled by the function.

        :param function func: A function to add to this filter
        """
        self._funcs.append(func)


class PatternFilter(object):
    """
    This tells if the named file contains one of the ignored patterns.
    These are just checked to see that the file name contains one of the listed strings.
    There's no regex in here.

    :param list patterns: List of "patterns" to check.
    """

    def __init__(self, patterns):
        self._patterns = patterns

    def protected(self, file_name):
        """
        :param str file_name: Name of the file to check for patterns in
        :returns: True if one of the stored patterns is in the file_name
        :rtype: bool
        """

        # Skip over paths that include part of the list of ignored directories
        for pattern in self._patterns:
            if pattern in file_name:
                return True

        return False


class FullFilter(object):
    """
    Always returns true
    """

    def protected(self, _):  # pylint: disable=no-self-use
        """
        Takes the file name as a dummy variable, but doesn't check it
        """
        return True
