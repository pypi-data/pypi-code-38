"""
Search a network configuration file

This module holds the primitives that make up a network configuration--configuration
lines and lists of lines.

To begin using `networkparse`, start with :module:`~parse`
"""
import re
from typing import List


class MultipleLinesError(Exception):
    """
    More than one line was found
    """


class NoLinesError(Exception):
    """
    No lines were found and at least one was expected
    """


class ConfigLine:
    """
    A line of a configuration file, which may or may not have children

    Generally supports the same functions as Python strings.
    """

    #: The :class:`~.parse.ConfigBase`-subclass which created the line and will be used for
    #: checking style-specific questions
    config_manager = None

    #: Parent block line (ie, might point to a line that's interface Eth1/1)
    #: Could be a :class:`~.parse.ConfigBase` or another :class:`~ConfigLine`
    parent = None

    #: The line number in the original configuration file
    line_number = None

    #: Text of configuration line, not including any leading or trailing whitespace
    #: Generally, treat the :class:`~ConfigLine` itself as a string, rather than
    #: using `.text`. For example:
    #:
    #: .. code:: python
    #:
    #:      # Prefer these:
    #:      parts = line.split()
    #:      print(line)
    #:
    #:      # To these:
    #:      parts = line.text.split()
    #:      print(line.text)
    text = ""

    #: Lines "under" this one--for example, lines 2 and 3 below would be children
    #: to line 1.
    #:
    #: .. code::
    #:
    #:     1. interface Ethernet0/1
    #:     2.   no shutdown
    #:     3.   switchport mode access
    children = None

    def __init__(
        self,
        config_manager,
        parent,
        text: str,
        line_number: int = None,
        children: List = None,
    ):
        """
        A configuration line. Typically not created manually
        """
        self.config_manager = config_manager
        self.text = text
        self.parent = parent
        self.line_number = line_number
        self.children = children or ConfigLineList()

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Line {self.line_number}: {self.text} ({len(self.children)} children)"

    @property
    def siblings(self):
        """
        Returns a :class:`~ConfigLineList` of all sibling lines

        Does not include this line in the list. If you do want this line in the
        list, try :code:`line.parent.children`.
        """
        siblings = self.parent.children.copy()
        siblings.remove(self)
        return siblings

    def tree_display(
        self,
        initial_indent: int = 0,
        line_number: bool = False,
        internal_indent: int = 0,
    ) -> str:
        """
        Print this line and child lines indented to show hierachy

        :param initial_indent: How many spaces to put before the first text
            on the line. If None, will use the "original" indent level--i.e.,
            if this was a second-level item in the original config, it will
            be displayed with one indent before it.
        :param line_number: Display original line numbers of each line
        :param internal_indent: How many spaces to place *after* the line number
        :return: String of this and all child line items in an indented, human-readable
            format.
        """
        if initial_indent is None:
            initial_indent = self.depth * self.config_manager.indent_size

        start_str = " " * initial_indent
        if line_number:
            start_str += f"{self.line_number}: "

        start_str += " " * internal_indent

        lines = [f"{start_str}{self.text} ({len(self.children)} children)"]
        for c in self.children:
            lines.append(
                c.tree_display(
                    initial_indent=initial_indent,
                    line_number=line_number,
                    internal_indent=internal_indent + self.config_manager.indent_size,
                )
            )
        return "\n".join(lines)

    def is_comment(self) -> bool:
        """
        Check if this line is a comment

        :return: True if line is a commment, False otherwise
        """
        return self.text.startswith(self.config_manager.comment_marker)

    @property
    def depth(self) -> int:
        """
        Returns how logically nested in the config this line is

        For example, the config below has the `.depth` displayed next to each item:

        .. code::

            child                0
            child 1              0
            child 2              0
            child 3              0
                child 4          1
                child 5          1
            child 6              0
                child 7          1
                    child 8      2
                    child 9      2

        :return: 0 for top-level items, 1 or more for child items.
        """
        depth = -1
        curr = self.parent
        while curr is not None:
            depth += 1
            curr = curr.parent
        return depth

    def get_top(self) -> "ConfigLine":
        """
        Returns the top-level line that this child is a line of

        May return the same line if it is a top-level item

        :return: Top-level ConfigLine with no parents (other than the full config itself)
        :rtype: ConfigLine
        """
        top = self
        while isinstance(top.parent, ConfigLine):
            top = top.parent
        return top

    def is_top(self) -> bool:
        """
        Tests if this line is at the top-level of the configuration

        :return: True if the parent is the config itself, False otherwise
        :rtype: bool
        """
        return self.depth == 0

    def __contains__(self, x):
        """
        Support "in"
        """
        return x in self.text

    def __eq__(self, other):
        """
        If compared to another :class:`~ConfigLine`, ensure it's has the same instance

        Otherwise do a string compare
        """
        if isinstance(other, ConfigLine):
            return self is other
        else:
            return self.text == str(other)

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        return self.text[index]

    def __iter__(self):
        return iter(self.text)

    def find(self, sub, start=None, end=None):
        """
        See `str.find`_

        .. _`str.find`: https://docs.python.org/3/library/stdtypes.html#str.find
        """
        return self.text.find(sub, start, end)

    def rfind(self, sub, start=None, end=None):
        """
        See `str.rfind`_

        .. _`str.rfind`: https://docs.python.org/3/library/stdtypes.html#str.rfind
        """
        return self.text.rfind(sub, start, end)

    def rindex(self, sub, start=None, end=None):
        """
        See `str.rindex`_

        .. _`str.rindex`: https://docs.python.org/3/library/stdtypes.html#str.rindex
        """
        return self.text.rindex(sub, start, end)

    def index(self, sub, start=None, end=None):
        """
        See `str.index`_

        .. _`str.index`: https://docs.python.org/3/library/stdtypes.html#str.index
        """
        return self.text.index(sub, start, end)

    def count(self, sub, start=None, end=None):
        """
        See `str.count`_

        .. _`str.count`: https://docs.python.org/3/library/stdtypes.html#str.count
        """
        return self.text.count(sub, start, end)

    def endswith(self, sub, start=None, end=None):
        """
        See `str.endswith`_

        .. _`str.endswith`: https://docs.python.org/3/library/stdtypes.html#str.endswith
        """
        return self.text.endswith(sub, start, end)

    def startswith(self, sub, start=None, end=None):
        """
        See `str.startswith`_

        .. _`str.startswith`: https://docs.python.org/3/library/stdtypes.html#str.startswith
        """
        return self.text.startswith(sub, start, end)

    def upper(self):
        """
        See `str.upper`_

        .. _`str.upper`: https://docs.python.org/3/library/stdtypes.html#str.upper
        """
        return self.text.upper()

    def lower(self):
        """
        See `str.lower`_

        .. _`str.lower`: https://docs.python.org/3/library/stdtypes.html#str.lower
        """
        return self.text.lower()

    def partition(self, sep):
        """
        See `str.partition`_

        .. _`str.partition`: https://docs.python.org/3/library/stdtypes.html#str.partition
        """
        return self.text.partition(sep)

    def rpartition(self, sep):
        """
        See `str.rpartition`_

        .. _`str.rpartition`: https://docs.python.org/3/library/stdtypes.html#str.rpartition
        """
        return self.text.rpartition(sep)

    def split(self, sep=None, maxsplit=-1):
        """
        See `str.split`_

        .. _`str.split`: https://docs.python.org/3/library/stdtypes.html#str.split
        """
        return self.text.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        """
        See `str.rsplit`_

        .. _`str.rsplit`: https://docs.python.org/3/library/stdtypes.html#str.rsplit
        """
        return self.text.rsplit(sep, maxsplit)


class ConfigLineList:
    """
    A searchable list of :class:`~ConfigLine` s

    This class acts like a standard Python list, so indexed access via `[]`,
    `len()`, etc. all work. See the Python 3 documentation on `list`_ for more
    methods.

    This class may not hold only :class:`~ConfigLine` items from the same parent--it can
    store *any* :class:`~ConfigLine`, so be aware that iterating through a
    :class:`~ConfigLineList` does not necessarily mean all items have the same parent.
    In particular, after running :func:`~filter` or :func:`~flatten` the returned
    list will be a mixture of parents.

    .. _list: https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """

    def __init__(self, lines: List[ConfigLine] = None):
        self.lines = lines or []

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    def __iter__(self):
        return iter(self.lines)

    def __getattr__(self, name):
        """
        Defers all failing calls to list
        """
        return getattr(self.lines, name)

    def __str__(self):
        return self.tree_display()

    def __repr__(self):
        return str(self)

    def copy(self) -> List:
        """
        Create a copy of this list

        :return: Copy of list. :class:`~ConfigLine` s are not duplicated.
        :rtype: ConfigLineList
        """
        return ConfigLineList(self.lines.copy())

    def tree_display(self, initial_indent: int = 0, line_number: bool = False) -> str:
        """
        Print all lines in list with indents to show hierachy

        :param initial_indent: How many spaces to put before the first text
            on the line. If None, uses the "original" indent. See
            :func:`~ConfigLine.tree_display` for more details. 
        :param line_number: Display original line numbers of each line
        :return: String of this and all child line items in an indented, human-readable
            format.

        Also refer to :class:`~ConfigLine`'s :func:`~ConfigLine.tree_display`.

        .. note::

            Top-level items may not all have the same parent, as a
            :class:`~ConfigLineList` can hold any combination of lines (even
            duplicates).
        """
        if not self.lines:
            return (" " * initial_indent) + "(empty line list)"

        lines = []
        for line in self.lines:
            lines.append(
                line.tree_display(
                    initial_indent=initial_indent, line_number=line_number
                )
            )
        return "\n".join(lines)

    def one(self) -> ConfigLine:
        """
        Returns the single ConfigLine in list

        :raises MultipleLinesError: There is more than one item in list.
        :raises NoLinesError: There are no items in list. Use
            :func:`~one_or_none` to return `None` if there are no items
        :return: First and only :class:`~ConfigLine`
        """
        item = self.one_or_none()
        if item is None:
            raise NoLinesError()
        return item

    def one_or_none(self) -> ConfigLine:
        """
        Returns the single ConfigLine in list

        :raises MultipleLinesError: There is more than one item in list. Use
            :func:`~one` to raise an exception if there are no items
        :return: First and only :class:`~ConfigLine` if there is one, otherwise `None`
        """
        if len(self) == 0:
            return None
        elif len(self) > 1:
            raise MultipleLinesError()
        else:
            return self[0]

    def flatten(self, depth: int = None) -> List:
        """
        Return a ConfigLineList of all of this list *and* the children

        :param depth: If `None`, returns all children, recursing as deeply as
            needed into the hierarchy (technically, limited to 500). Otherwise,
            flattens only the top `depth` levels.
        :return: New :class:`~ConfigLineList`

        For example, say you have the structure:

        .. code::

            level 1
                level 2
                    level 3

        `flatten(depth=None)` returns:

        .. code::

            level 1
            level 2
            level 3

        `flatten(depth=1)` returns:

        .. code::

            level 1
            level 2
                level 3
        """
        if depth is None:
            depth = 500

        flattened = ConfigLineList()
        for line in self.lines:
            flattened.append(line)

            if depth > 0:
                flattened.extend(line.children.flatten(depth=depth - 1))
        return flattened

    def filter(
        self,
        regex: str,
        *,
        full_match: bool = None,
        ignore_case: bool = False,
        invert: bool = False,
        depth: int = 0,
        skip_comments: bool = True,
    ) -> List:
        """
        Find all lines that match a regular expression

        :param regex: A string in Python's regex format that will be checked against
            each line
        :param full_match: If True, the regex must match the entire line (using
            Python's `re.fullmatch`). If False, the regex can match any where in
            the line (using `re.search`). If None, uses the default for contained
            lines' `config_manager` (typically `True`).
        :param ignore_case: If True, the regex will be compiled with the flag
            `re.IGNORECASE`.
        :param invert: If True, excludes matched items from the list. Default is
            False, matching lines are returned in the new list
        :param depth: Controls whether searches look at direct
            descendents

            - `depth = 0`: Line must be in this list, not a child
            - `depth > 0`: Also search the `children` of each line, up to the given depth
            - `depth = None`: Search through entire tree
        :param skip_comments: Controls whether search never returns comments. Default is True,
            meaning comment lines are never matched. Note that enabling this still means
            `regex` must match the line, *including any comment characters*.
        :return: New ConfigLineList with the filtered items. Returns an empty
            list if none are found.
        :rtype: ConfigLineList

        """
        if not self.lines:
            return ConfigLineList()

        if full_match is None:
            full_match = self.lines[0].config_manager.full_match

        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE

        compiled = re.compile(regex, flags)

        if full_match and not invert:
            match_func = compiled.fullmatch
        elif full_match and invert:
            match_func = lambda t: not compiled.fullmatch(t)
        elif not full_match and not invert:
            match_func = compiled.search
        elif not full_match and invert:
            match_func = lambda t: not compiled.search(t)

        starting_list = self
        if depth != 0:
            starting_list = self.flatten(depth=depth)

        matches = ConfigLineList()
        for s in starting_list:
            # Always skip comments?
            if skip_comments and s.is_comment():
                continue

            if match_func(s.text):
                matches.append(s)

        return matches

    def exclude(self, regex: str, **kwargs) -> List:
        """
        Calls :func:`~filter` with `invert` = `True`

        kwargs are passed through to :func:`~filter`, see that for for argument
        descriptions.

        :return: List with matching lines removed
        :rtype: ConfigLineList
        """
        return self.filter(regex=regex, invert=True, **kwargs)

    def filter_with_child(
        self,
        child_regex: str,
        *,
        full_match: bool = None,
        ignore_case: bool = False,
        depth: int = 0,
    ) -> List:
        """
        Find all lines that have a *child* that matches the given regex.

        :param child_regex: Regular expression that child line must match
        :param full_match: Whether the regex must match the entire child line.
            See :func:`~filter` for more details.
        :param ignore_case: If True, the regex will be compiled with the flag
            `re.IGNORECASE`. See :func:`~filter` for more details.
        :param depth: If is not 0, the child does not need to be a direct
            descendent. See :func:`~filter`'s `depth` argument for more details.
        :return: New filtered list
        :rtype: ConfigLineList

        For example, if this list has these items (children shown as well):

        .. code::

            child
            child 1
            child 2
            child 3
                child 4
                child 5
            child 6
                child 7
                    child 8
                    child 9

        Then `filter_with_child("child 4")` will return the list:

        .. code::

            child 3
                child 4
                child 5

        If `depth` is not 0, the child does not need to be a direct descendent.
        See `filter()`'s `depth` argument for more details. Given the example above,
        _with_child("child 8", depth=None)` will return the list:

        .. code::

            child 6
                child 7
                    child 8
                    child 9
        """
        real_match = ConfigLineList()
        for match in self.lines:
            if match.children.flatten(depth=depth).filter(
                regex=child_regex, full_match=full_match, ignore_case=ignore_case
            ):
                real_match.append(match)

        return real_match

    def filter_without_child(
        self,
        child_regex: str,
        *,
        full_match: bool = None,
        ignore_case: bool = False,
        depth: int = 0,
        skip_childless: bool = False,
    ) -> List:
        """
        Find all lines that do not have a child that matches the given regex.

        Follows the symmatics of :func:`~filter_with_child`, see that function
        for more details.

        :param skip_childless: If False (the default), a line that has no children
            will always be matched by this function.
        :return: New filtered list
        :rtype: ConfigLineList
        """
        real_match = ConfigLineList()
        for match in self.lines:
            if skip_childless and not match.children:
                continue

            if not match.children.flatten(depth=depth).filter(
                regex=child_regex, full_match=full_match, ignore_case=ignore_case
            ):
                real_match.append(match)

        return real_match

    def is_comment(self) -> bool:
        """
        A list of lines is never comment

        This exists to allow `is_comment()` to be called on a Config parser during
        setup, avoiding special cases.

        :return: False
        """
        return False
