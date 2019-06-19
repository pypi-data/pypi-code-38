"""
Parse a network configuration file

To begin using `networkparse`, typically an subclass of :class:`~ConfigBase` will be
instantiated with the text of the configuration file. Currently, `networkparse` has
support for:

- Cisco IOS: :class:`~ConfigIOS`
- Cisco NX-OS: :class:`~ConfigNXOS`
- Fortinet: :class:`~ConfigFortigate`
- HP: :class:`~ConfigHPCommware`
- Junos: :class:`~ConfigJunos`

The automatic parser, :func:`~automatic` may be a more effecient way to get started if
a single script may work work multiple configuration types.
"""
import re
import math
from dataclasses import dataclass
from collections import namedtuple
from typing import List, Optional
from .core import ConfigLineList, ConfigLine, MultipleLinesError, NoLinesError
import pyparsing


class OneIndexedList(list):
    """
    1-index based list

    Used internally for original_lines
    """

    def __init__(self, *args):
        super().__init__(*args)

    def _change_slice(self, original_slice: slice) -> slice:
        """
        Changes a slice to correspond to a 1-based index
        """
        start = original_slice.start
        if start is not None and start >= 0:
            start -= 1
        stop = original_slice.stop
        if stop is not None and stop >= 0:
            stop -= 1
        return slice(start, stop, original_slice.step)

    def __getitem__(self, index):
        if isinstance(index, int):
            if index > 0:
                return super().__getitem__(index - 1)
            elif index == 0:
                raise IndexError("List is 1-based and cannot access element 0")
            else:
                return super().__getitem__(index)
        elif isinstance(index, slice):
            return super().__getitem__(self._change_slice(index))
        else:
            raise TypeError("index must be an int or slice")

    def __setitem__(self, index, value):
        if isinstance(index, int):
            if index > 0:
                return super().__setitem__(index - 1, value)
            elif index == 0:
                raise IndexError("List is 1-based and cannot access element 0")
            else:
                return super().__setitem__(index, value)
        elif isinstance(index, slice):
            return super().__setitem__(self._change_slice(index), value)
        else:
            raise TypeError("index must be an int or slice")


@dataclass(order=True, frozen=True)
class VersionNumber:
    """
    Firmware version number
    """

    major: int
    minor: int = 0
    revision: int = 0

    @classmethod
    def from_string(cls, string) -> "VersionNumber":
        """
        Given a string containing a release number, returns a VersionNumber

        Supported formats:
        
        - 1.2.3
        - 1.2
        - 1.2(3)

        Version string may appear anywhere in the given string.

        :param string: String to attempt to parse
        :return: VersionNumber with major, minor, and (if available) revision number set
        :rtype: VersionNumber
        """
        if not string:
            return None

        m = re.match(
            r".*?(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<rev1>\d+))?(?:\((?P<rev2>\d+)\))?.*",
            string,
        )
        if not m:
            return None

        major = int(m.group("major"))
        minor = int(m.group("minor"))
        rev = 0
        if m.group("rev1"):
            rev = int(m.group("rev1"))
        if m.group("rev2"):
            rev = int(m.group("rev2"))

        return cls(major=major, minor=minor, revision=rev)


def line_parse_checker(line):
    """
    Checks if the given line parses fully--ie, all quotes are closed
    """
    quote_stack = [None]

    prev_char = None
    for char in line:
        top_stack = quote_stack[-1]

        if char in ("'", '"') and prev_char != "\\":
            if char == top_stack:
                quote_stack.pop()
            else:
                quote_stack.append(char)

        prev_char = char

    return len(quote_stack) == 1


class UnknownConfigError(Exception):
    """
    The correct configuration type could not be determined
    """


def automatic(
    config_content: str,
    *,
    include: List[str] = None,
    fallback: Optional["ConfigBase"] = None,
) -> "ConfigBase":
    """
    Based on the given configuration, guess the best parser.

    Currently, this function can guess the following (ordered base on reliability)

    - ASA: reliable
    - FortiOS: probably reliable
    - JunOS: probably reliable
    - IOS: may catch non-IOS items, but is last thing checked
    - NX: untested, might work

    :param include: Only check the given types. Types are "asa", "ios", "nxos",
        "fortios", "hp", and "junos". By default all options will be checked. The names
        used match with the :attr:`~ConfigBase.name` of each `ConfigBase` subclass.
    :param fallabck: If not match is found, use the specified class as a parser. This 
        should be an object, not an instance (i.e., `parse.ConfigIOS` vs. `parse.ConfigIOS()`).

    :raises UnknownConfigError: The correct configuration type could not be determined
    :return: Parsed configuration
    :rtype: ConfigBase
    """
    if include is None:
        include = ["asa", "ios", "nxos", "fortios", "hp", "junos"]

    # Do the lowest cost checks first
    if "asa" in include and "ASA Version" in config_content:
        return ConfigASA(config_content)

    if "nxos" in include and "boot nxos" in config_content:
        return ConfigNXOS(config_content)

    # Fortinet has many SSH keys and other items named after them--they could have removed it,
    # but that would be a good sign. Alternatively, configs start by specifying the device/version
    # they are pulled from
    if "fortios" in include:
        lowered = config_content.lower().strip()
        if (
            "fortinet" in lowered
            or "fortigate" in lowered
            or lowered.startswith("#config-version=")
        ):
            return ConfigFortigate(config_content)

    # JunOS uses braces
    if (
        "junos" in include
        and "system {" in config_content
        and "interfaces {" in config_content
        and "}" in config_content
    ):
        return ConfigJunos(config_content)

    # Look for the weird indenting HP does on some top-level items
    if (
        "hp" in include
        and "#\n version " in config_content
        and "#\n clock" in config_content
        and "#\n sysname" in config_content
    ):
        return ConfigHPCommware(config_content)

    # IOS probably has version as the first non-comment item
    if "ios" in include:
        bail_line_count = 0
        for line in config_content.splitlines():
            line = line.strip()
            if (
                not line
                or line.startswith("!")
                or line == "Building configuration..."
                or re.match(r"Current configuration.*bytes", line)
            ):
                continue

            if re.match("version \d+.\d+$", line):
                return ConfigIOS(config_content)

            bail_line_count += 1

            # Need to find version fairly early on, I've only ever seen it in the first 3 lines
            if bail_line_count > 30:
                break

    # Failed to find a match
    if fallback:
        return fallback(config_content)
    else:
        raise UnknownConfigError(
            "Unable to indentify configuration type and no fallback was supplied"
        )


class ConfigBase(ConfigLineList):
    """
    Common configuration base operations

    :class:`~ConfigBase` is really just a specialized :class:`~.core.ConfigLineList`
    that can hold some settings and act like a :class:`~.core.ConfigLine`
    in terms of having a parent (`None`) and children.

    Refer to :class:`~.core.ConfigLineList` for filtering and searching options
    after you've parsed a configuration file.
    """

    #: Name of configuration type, usable by scripts that support
    #: multiple configuration types.
    name = "base"

    #: Defaults to ! as the comment marker, following Cisco convention. If more
    #: complex comment checking is needed override is_comment()
    comment_marker = "!"

    #: Default setting for `full_match` in `filter`. Defaults to True to prevent
    #: a search from also matching the "no" version of the line.
    full_match = True

    #: How far tree_display() should indent children. Has no effect on parsing
    indent_size = 2

    #: Original configuration lines, before any parsing occured. The
    #: :attr:`~ConfigLine.line_number` from a :class:`~ConfigLine` will match
    #: up with this list
    original_lines = None

    #: Exists to make walking up a parent tree easier--just look for parent=None to stop
    #:
    #: Contrived example:
    #:
    #: .. code:: python
    #:
    #:     current_line = config.filter("no shutdown", depth=None)
    #:     while current_line.parent is not None:
    #:         print(current_line)
    #:         current_line = current_line.parent
    parent = None

    def __init__(
        self,
        name="base",
        original_lines: List[str] = None,
        comment_marker: str = "!",
        full_match_default: bool = True,
        indent_size_default: int = 2,
    ):
        """
        Configures settings used by :class:`~ConfigLine` methods

        In addition, subclasses should override this to parse the configuration file
        into :class:`~ConfigLine`s. See :class:`~ConfigIOS` for an example of this.
        """
        super().__init__()
        self.name = name
        self.comment_marker = comment_marker
        self.full_match = full_match_default
        self.original_lines = OneIndexedList(original_lines or [])
        self.indent_size = indent_size_default

    @property
    def children(self) -> ConfigLineList:
        """
        Allow for use of ".children" for consistency with :class:`~ConfigLine`

        Returns `self`, which is already a :class:`~ConfigLineList`. It
        is likely cleaner to not use this. I.E.:

        .. code:: python

            config = ConfigIOS(running_config_contents)

            # Prefer this
            config.filter("interface .+")

            # Only use this if it looks clearer in context
            config.children.filter("interface .+")
        """
        return self

    def get_line(self, line_number) -> ConfigLine:
        """
        Get a line by line-number

        Note that if the given line numbers falls in the middle of a multi-line string, it may 
        not be found, depending on how the individual parser represents it.

        :param line_number: Returns the line at the given line number.
        :raises IndexError: The given `line_number` does not exist in the config
        :return: Line at the given line number
        :rtype: ConfigLine
        """
        for line in self.flatten():
            if line.line_number == line_number:
                return line

        raise IndexError(f"{line_number} not found in config")

    @property
    def version(self) -> Optional[VersionNumber]:
        """
        Returns the version number of the configuration

        This is intended to help with major version differences,
        i.e., IOS v12 vs. v15 differences. Generally it indentifies
        the version by looking for a line like "version 12.2", although
        the details vary based on the parser in use. More details
        can be found on each of the base classes.

        :return: Floating-point version number (i.e. 12.1 or 15.4) or None if the version cannot be found
        :rtype: Optional[VersionNumber]
        """
        # By default, we don't know how to do this
        return None


class ConfigIOS(ConfigBase):
    """
    Parses Cisco IOS-style configuration into common config format

    Supported command output:

    - `show running-config`
    - `show running-config all`
    - `show startup-config`

    :attr:`~ConfigBase.name` is set to "ios" for this parser.

    See :class:`~ConfigBase` for more information.
    """

    def __init__(self, config_content: str):
        """
        Break all lines up into tree
        """
        super().__init__(
            name="ios", original_lines=config_content.splitlines(), comment_marker="!"
        )

        parent_stack = {0: self}
        last_line = None
        last_indent = 0
        for lineno, line in enumerate(self.original_lines, start=1):
            if line.strip() == "--More--":
                continue

            # Determine our config depth and compare to the previous line's depth
            # The top-level config is always on the stack, so account for that
            matches = re.match(r"^(?P<spaces>\s*)", line)
            new_indent = len(matches.group("spaces"))

            if new_indent > last_indent:
                # Need to change parents to the last item of our current parent
                parent_stack[new_indent] = last_line

            curr_parent = parent_stack[new_indent]
            last_indent = new_indent
            last_line = ConfigLine(
                config_manager=self,
                parent=curr_parent,
                text=line.strip(),
                line_number=lineno,
            )
            curr_parent.children.append(last_line)

    @property
    def version(self) -> Optional[VersionNumber]:
        """
        Returns the version number of the configuration

        This is intended to help with v12 vs. v15 differences. It indentifies the version
        by looking for a line like "version 12.2".

        :return: Version number (i.e. 12 or 15) or None if the version cannot be found
        :rtype: Optional[VersionNumber]
        """
        ver = self.filter("version .*").one_or_none()
        if not ver:
            return None

        return VersionNumber.from_string(ver.text)


class ConfigNXOS(ConfigIOS):
    """
    Parses Cisco NX-OS-style configuration into common config format

    Currently this parser completely defers to :class:`~ConfigIOS`.

    See :class:`~ConfigIOS` for more information.
    """


class ConfigASA(ConfigBase):
    """
    Parses Cisco ASA-style configuration into common config format

    Supported command output:

    - `show running-config`
    - `show running-config all`
    - `show startup-config`

    :attr:`~ConfigBase.name` is set to "asa" for this parser.

    See :class:`~ConfigBase` for more information.
    """

    def __init__(self, config_content: str):
        """
        Break all lines up into tree
        """
        super().__init__(
            name="asa", original_lines=config_content.splitlines(), comment_marker="!"
        )

        parent_stack = {0: self}
        last_line = None
        last_indent = 0
        for lineno, line in enumerate(self.original_lines, start=1):
            # ASAs are full of blank lines that don't matter
            if not line.strip():
                continue

            # Determine our config depth and compare to the previous line's depth
            # The top-level config is always on the stack, so account for that
            matches = re.match(r"^(?P<spaces>\s*)", line)
            new_indent = len(matches.group("spaces"))

            if new_indent > last_indent:
                # Need to change parents to the last item of our current parent
                parent_stack[new_indent] = last_line

            curr_parent = parent_stack[new_indent]
            last_indent = new_indent
            last_line = ConfigLine(
                config_manager=self,
                parent=curr_parent,
                text=line.strip(),
                line_number=lineno,
            )
            curr_parent.children.append(last_line)

    @property
    def version(self) -> Optional[VersionNumber]:
        """
        Returns the major version number of the configuration

        This is intended to help difference between major versions. It indentifies the version
        by looking for a line like "ASA Version 9.0(3)".

        :return: Version number (i.e. 12.1 or 15.4) or None if the version cannot be found
        :rtype: Optional[VersionNumber]
        """
        ver = self.filter("ASA Version .*").one_or_none()
        if not ver:
            return None

        return VersionNumber.from_string(ver.text)


class ConfigHPCommware(ConfigBase):
    """
    Parses HP Commware-style configuration into common config format

    :attr:`~ConfigBase.name` is set to "hp" for this parser.

    See :class:`~ConfigBase` for more information.
    """

    def __init__(self, config_content: str):
        """
        Break all lines up into tree
        """
        super().__init__(
            name="hp", original_lines=config_content.splitlines(), comment_marker="#"
        )

        # lines = enumerate(self.original_lines, start=1)
        parent_stack = {0: self}
        last_line = None
        last_indent = 0
        for lineno, line in enumerate(self.original_lines, start=1):
            if not line.strip() or line.strip() == "--More--":
                continue

            # Determine our config depth and compare to the previous line's depth
            # The top-level config is always on the stack, so account for that
            matches = re.match(r"^(?P<spaces>\s*)", line)
            new_indent = len(matches.group("spaces"))

            if new_indent > last_indent:
                # Need to change parents to the last item of our current parent
                parent_stack[new_indent] = last_line

            curr_parent = parent_stack[new_indent]
            if curr_parent.is_comment():
                # HP indents the top level lines... sometimes. When there are
                # no children, I think. Reset that
                curr_parent = parent_stack[0]

            last_indent = new_indent
            last_line = ConfigLine(
                config_manager=self,
                parent=curr_parent,
                text=line.strip(),
                line_number=lineno,
            )
            curr_parent.children.append(last_line)

    @property
    def version(self) -> Optional[VersionNumber]:
        """
        Returns the major version number of the configuration

        This is intended to help with v12 vs. v15 differences. It indentifies the version
        by looking for a line like "version 5.20, Release 1513P81".

        :return: Version number (i.e. 5.20) or None if the version cannot be found
        """
        ver = self.filter("version .*").one_or_none()
        if not ver:
            return None

        return VersionNumber.from_string(ver.text)


class ConfigJunos(ConfigBase):
    """
    Parses a Juniper OS (Junos)-style configuration into common config format

    Supported command outputs are:

    - `show configuration`
    - `save`

    :attr:`~ConfigBase.name` is set to "junos" for this parser.

    See :class:`~ConfigBase` for more information.
    """

    def __init__(self, config_content: str):
        """
        Break all lines up into tree
        """
        super().__init__(
            name="junos", original_lines=config_content.splitlines(), comment_marker="#"
        )

        parent_stack = [self]
        last_line = None
        for lineno, line in enumerate(self.original_lines, start=1):
            curr_parent = parent_stack[-1]

            command = True
            block_start = False
            block_end = False
            modified_line = line.strip()
            if modified_line.endswith(";"):
                command = True
            elif modified_line.endswith("{"):
                block_start = True
            elif modified_line.endswith("}"):
                block_end = True

            if block_start or block_end or command:
                modified_line = modified_line[:-1]

            if not block_end:
                last_line = ConfigLine(
                    config_manager=self,
                    parent=curr_parent,
                    text=modified_line.strip(),
                    line_number=lineno,
                )
                curr_parent.children.append(last_line)

            # Change indent?
            if block_start:
                parent_stack.append(last_line)
            elif block_end:
                parent_stack.pop()


class ConfigFortigate(ConfigBase):
    """
    Parses Fortinet-style configuration into common config format

    Supported command output:

    - `show full-configuration`

    :attr:`~ConfigBase.name` is set to "fortios" for this parser.

    See :class:`~ConfigBase` for more information.
    """

    def __init__(self, config_content: str):
        """
        Break all lines up into tree
        """
        super().__init__(
            name="fortios",
            original_lines=config_content.splitlines(),
            comment_marker="#",
        )

        lines = enumerate(self.original_lines, start=1)
        parent_stack = {0: self}
        last_line = None
        last_indent = 0
        for lineno, line in lines:
            if not line.strip() or line.strip() == "--More--":
                continue

            # Determine our config depth and compare to the previous line's depth
            # The top-level config is always on the stack, so account for that
            matches = re.match(r"^(?P<spaces>\s*)", line)
            new_indent = len(matches.group("spaces"))

            while not line_parse_checker(line):
                # Keep adding lines to this one until it parses
                _, added_line = next(lines)
                line += "\n" + added_line

            if new_indent > last_indent:
                # Need to change parents to the last item of our current parent
                parent_stack[new_indent] = last_line

            curr_parent = parent_stack[new_indent]
            last_indent = new_indent
            last_line = ConfigLine(
                config_manager=self,
                parent=curr_parent,
                text=line.strip(),
                line_number=lineno,
            )
            curr_parent.children.append(last_line)

    @property
    def version(self) -> Optional[VersionNumber]:
        """
        Returns the version number of the configuration

        This is intended to help with v12 vs. v15 types of differences. It
        indentifies the version by looking for a line like
        "#config-version=FGVM64-6.2.0-FW-build0866-190328:opmode=0:vdom=0:user=admin".

        :return: Float version number (i.e. 6.2) or None if the version cannot be found
        :rtype: Optional[VersionNumber]
        """
        ver = self.filter(".*config-version=.*", skip_comments=False).one_or_none()
        if not ver:
            return None

        return VersionNumber.from_string(ver.text)
