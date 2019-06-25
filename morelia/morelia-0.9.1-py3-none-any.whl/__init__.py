# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import requests

from morelia.config import TOMLConfig
from morelia.formatters import ColorTextFormatter, PlainTextFormatter
from morelia.parser import Parser, execute_script

__version__ = "0.9.1"


def has_color_support():
    """Check if color in terminal is supported."""
    return sys.platform != "win32"  # pragma: nocover


def run(
    filename,
    suite,
    as_str=None,
    scenario=r".*",
    verbose=False,
    show_all_missing=True,
    **kwargs
):  # NOQA
    """Parse file and run tests on given suite.

    :param str filename: file name
    :param unittest.TestCase suite: TestCase instance
    :param string as_str: None to use file or a string containing the feature to parse
    :param string scenario: a regex pattern to match the scenario to run
    :param boolean verbose: be verbose
    :param boolean show_all_missing: show all missing steps
    """
    formatter = kwargs.get("formatter", None)
    if verbose and not formatter:
        if has_color_support():
            formatter = ColorTextFormatter()
        else:
            formatter = PlainTextFormatter()
        kwargs["formatter"] = formatter
    kwargs["show_all_missing"] = show_all_missing
    if as_str is None:
        source = File(filename)
    else:
        source = Text(as_str, filename)
    feature = Parser().parse_features(source)
    return execute_script(feature, suite, scenario=scenario, **kwargs)


def verify(script, suite, scenario: str = ".*", config: str = "default") -> None:
    """Verifies script with steps from suite.

    :param script: feature script
    :param suite: object with steps defined
    :param str scenario: regex pattern for selecting single scenarios
    :param str config: section from configuration to apply

    Script can be passed directly to verify method as first argument.

    .. code-block:: python

        >>> from morelia import verify
        >>> verify(
        ...    \"""
        ...    Feature: Addition
        ...    Scenario: Add two numbers
        ...      Given I have entered 50 into the calculator
        ...      And I have entered 70 into the calculator
        ...      When I press add
        ...      Then the result should be 120 on the screen
        ...    \""",
        ...    test_case_with_steps,
        )

    When given path to file with script morelia will read that file and verify:

    .. code-block:: python

        >>> verify('calculator.feature', test_case_with_steps)

    Similary url pointing to script can be given:

    .. code-block:: python

        >>> verify('http://example.com/calculator', test_case_with_steps)

    Two last invocations will work only for single line strings.
    If it starts with "http[s]://" it is considered an url.
    If it ends with ".feature" it is considered a file.

    To explicity mark parameter's type it can be wrapped in helper classes:

    - :py:func:`File`
    - :py:func:`Url`
    - :py:func:`Text`

        >>> from morelia import verify, File, Text, Url
        >>> verify(File('calculator.txt'), test_case_with_steps)
        >>> verify(Url('http://example.com/calculator.feature'), test_case_with_steps)
        >>> verify(
        ...    Text(\"""
        ...    Feature: Addition
        ...    Scenario: Add two numbers
        ...      Given I have entered 50 into the calculator
        ...      And I have entered 70 into the calculator
        ...      When I press add
        ...      Then the result should be 120 on the screen
        ...    \"""),
        ...    test_case_with_steps,
        )

    """
    conf = TOMLConfig(config)
    script = _coerce_type(script)
    feature = Parser().parse_features(script)
    execute_script(feature, suite, scenario=scenario, config=conf)


def _coerce_type(script):
    if isinstance(script, Source):
        return script
    script = str(script)
    if "\n" in script:
        return Text(script)
    elif script.startswith("http://") or script.startswith("https://"):
        return Url(script)
    elif script.endswith(".feature"):
        return File(script)
    else:
        return Text(script)


class Source:
    pass


class Text(Source):
    """Marks string as a text source.

    :param str text: text source
    :param str name: optional name show in tracebacks
    """

    def __init__(self, text, name="<stdin>"):
        self.filename = name
        self.__text = text

    def __str__(self):
        return self.__text


class File(Source):
    """Marks string as a file path."""

    def __init__(self, path):
        self.__path = Path(path)
        self.filename = str(path)

    def __str__(self):
        try:
            return self.__text
        except AttributeError:
            self.__text = self.__path.read_text()
            return self.__text


class Url(Source):
    """Marks string as an url endpoint."""

    def __init__(self, url):
        self.__url = url
        self.filename = url

    def __str__(self):
        try:
            return self.__text
        except AttributeError:
            self.__text = requests.get(self.__url).text
            return self.__text


__all__ = ("Parser", "run", "verify", "File", "Url")
