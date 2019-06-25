"""
Formatting output
=================

Morelia complies with Unix's `Rule of Silence` [#ROS]_ so when you hook it like this:

.. code-block:: python

    verify(filename, self)

and all tests passes it would say nothing:

.. code-block:: console

    $ python -m unittest test_acceptance
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.028s

    OK

(here's only information from test runner)

But when something went wrong it would complie with Unix's `Rule of Repair` [#ROR]_
and fail noisily:

.. code-block:: console

    F
    ======================================================================
    FAIL: test_addition (__main__.CalculatorTestCase)
    Addition feature.
    ----------------------------------------------------------------------
    AssertionError:
    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Then the result should be "120" on the screen

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      File "./test_acceptance.py", line 31, in test_addition
        verify(filename, self)
      File "(...)/morelia/__init__.py", line 119, in verify
        execute_script(feature, suite, scenario=scenario, config=conf)
      File "(...)/morelia/parser.py", line 75, in execute_script
        raise exc from AssertionError(breadcrumbs)
      File "./test_acceptance.py", line 46, in step_the_result_should_be_on_the_screen
        self.assertEqual(int(number), self.calculator.get_result())
    AssertionError: 120 != 121

    ----------------------------------------------------------------------
    Ran 1 test in 0.020s

    FAILED (failures=1)

Verbosity
---------

In Behaviour Driven Development participate both programmers and non-programmers
and the latter are often used to programs which report all the time what is going on.
So to make Morelia a little more verbose you can configure custom output in pyproject.toml file.
E.g.

.. code-block:: toml

    [tool.morelia.default.output]
    formatter.format="text"
    writer.type="terminal"

.. code-block:: python

    verify(filename, self)

.. code-block:: console

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "120" on the screen            # pass  0.001s
    Scenario: Subsequent additions
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        And I enter "20" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "140" on the screen            # pass  0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.027s

    OK

Formatter Classes
-----------------

"""

import sys
import time
from abc import ABC, abstractmethod
from io import StringIO

import requests

from morelia.grammar import Feature, Step
from morelia.visitors import VisitorObserver

colors = {
    "normal": "\x1b[30m",
    "fail": "\x1b[31m",
    "error": "\x1b[31m",
    "pass": "\x1b[32m",
    "reset": "\x1b[0m",
}


class PlainTextFormatter:
    def __init__(self, stream=None):
        self._stream = stream if stream is not None else sys.stderr

    def output(self, node, line, status, duration):
        if isinstance(node, Feature):
            self._stream.write("\n")
        if isinstance(node, Step):
            status = status.lower()
            text = "{:<60} # {:<5} {:.3f}s\n".format(line.strip("\n"), status, duration)
        else:
            text = "%s\n" % line.strip("\n")
        self._stream.write(text)
        self._stream.flush()


class ColorTextFormatter(PlainTextFormatter):
    def output(self, node, line, status, duration):
        if isinstance(node, Feature):
            self._stream.write("\n")
        if isinstance(node, Step):
            status = status.lower()
            text = "{}{:<60} # {:.3f}s{}\n".format(
                colors[status], line.strip("\n"), duration, colors["reset"]
            )
        else:
            text = "%s\n" % line.strip("\n")
        self._stream.write(text)
        self._stream.flush()


class Writer(VisitorObserver):
    def __init__(self, formatter):
        self.__formatter = formatter

    def step_started(self, node):
        self.status = "pass"
        self.start_time = time.time()

    def step_failed(self, node):
        self.status = "fail"

    def step_errored(self, node):
        self.status = "error"

    def step_finished(self, node):
        duration = time.time() - self.start_time
        self.__formatter.output(node, node.interpolated_source(), self.status, duration)

    def node_started(self, node):
        self.__formatter.output(node, node.interpolated_source(), "", 0)


class IOutput(ABC):
    @abstractmethod
    def write(self, text):  # pragma: nocover
        pass

    @abstractmethod
    def close(self):  # pragma: nocover
        pass


class FileOutput(IOutput):
    default_buffered = True

    def __init__(self, path, open_func=open):
        self._path = path
        self.__open = open_func

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self._path == other._path)

    def write(self, text):
        file = self._get_file()
        file.write(text)
        file.flush()

    def close(self):
        self._get_file().close()

    def _get_file(self):
        try:
            return self.__file
        except AttributeError:
            self.__file = self.__open(self._path, "w")
            return self.__file


class TerminalOutput(FileOutput):
    default_buffered = False

    def __init__(self, dest="stderr"):
        self._path = dest

    def _get_file(self):
        if self._path == "stdout":
            return sys.stdout
        else:
            return sys.stderr

    def close(self):
        pass


class RemoteOutput(IOutput):
    default_buffered = True

    def __init__(self, url, transport=requests):
        self._url = url
        self.__transport = transport

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self._url == other._url)

    def write(self, text):
        self.__transport.post(self._url, text)

    def close(self):
        pass


class Buffered(IOutput):
    def __init__(self, wrapped: IOutput):
        self._wrapped = wrapped
        self.__buffer = StringIO()

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self._wrapped == other._wrapped)

    def write(self, text):
        self.__buffer.write(text)

    def close(self):
        self._wrapped.write(self.__buffer.getvalue())
        self.__buffer.close()
        self._wrapped.close()


class TextFormat(VisitorObserver):
    def __init__(self, output: IOutput, color=False):
        self._color = color
        self._output = output

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__)
            and (self._color == other._color)
            and (self._output == other._output)
        )

    def step_started(self, node):
        self.status = "pass"
        self.start_time = time.time()

    def step_failed(self, node):
        self.status = "fail"

    def step_errored(self, node):
        self.status = "error"

    def step_finished(self, node):
        duration = time.time() - self.start_time
        line = node.interpolated_source()
        if self._color:
            text = "{}{:<60} # {:.3f}s{}\n".format(
                colors[self.status], line.strip("\n"), duration, colors["reset"]
            )
        else:
            text = "{:<60} # {:<5} {:.3f}s\n".format(
                line.strip("\n"), self.status, duration
            )
        self._output.write(text)

    def feature_started(self, node):
        self._output.write("\n")

    def node_started(self, node):
        line = node.interpolated_source()
        text = line.strip("\n") + "\n"
        self._output.write(text)

    def verify_finished(self):
        self._output.close()
