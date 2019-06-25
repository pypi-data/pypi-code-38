"""
Configuration
-------------

Morelia looks for configuration file "pyproject.toml" in current directory.
If it is not present then it looks for "~/.config/morelia/config.toml".

You can bypass that setting environment variable MORELIA_CONFIG to the path to config file.

Morelia reads it's configuration from "tool.morelia.<section>" namespace.
You can give section part when calling "verify" method.

E.g. if you have configuration:

.. code-block:: toml

    [tool.morelia.default]
    wip=false

    [tool.morelia.myconfig]
    wip=true

and call "verify" as:

.. code-block:: python

   verify(filename, self, config="myconfig")

Then it would be run with wip (work in progress) mode active.

If no config is passed, then "default" is assumed.
"""

import os
from pathlib import Path

import toml

from morelia.formatters import (
    Buffered,
    FileOutput,
    RemoteOutput,
    TerminalOutput,
    TextFormat,
)
from morelia.matchers import MethodNameStepMatcher, ParseStepMatcher, RegexpStepMatcher

MATCHERS = {
    "parse": ParseStepMatcher,
    "regex": RegexpStepMatcher,
    "method": MethodNameStepMatcher,
}


FORMATTERS = {"text": TextFormat}


OUTPUTS = {"terminal": TerminalOutput, "file": FileOutput, "remote": RemoteOutput}


class TOMLConfig:
    def __init__(self, section="default", filename=None):
        self.__section = section
        path = self.__get_path(filename)
        self.__data = {"wip": False, "matchers": ["regex", "parse", "method"]}
        if path:
            data = toml.load(path).get("tool", {}).get("morelia", {}).get(section, {})
        else:
            data = {}
        self.__data.update(data)

    def __get_path(self, filename):
        if filename and Path(filename).exists():
            return filename
        try:
            filename = os.environ["MORELIA_CONFIG"]
            if Path(filename).exists():
                return filename
        except KeyError:
            pass
        paths = [Path("pyproject.toml"), Path("~/.config/morelia/config.toml")]
        paths = [str(path) for path in paths if path.exists()]
        try:
            return paths[0]
        except IndexError:
            return None

    def get_matchers(self):
        return [MATCHERS[matcher] for matcher in self.__data["matchers"]]

    def get_writers(self):
        writers = []
        for writer_conf in self.__data.get("output", []):
            output_config = writer_conf["writer"]
            output = self.__create_output(output_config)
            format_config = writer_conf["formatter"]
            writers.append(self.__create_formatter(format_config, output))
        return writers

    def __create_output(self, config):
        output_type = config.pop("type")
        output_class = OUTPUTS[output_type]
        buffered = config.pop("buffered", output_class.default_buffered)
        output = output_class(**config)
        if buffered:
            output = Buffered(output)
        return output

    def __create_formatter(self, config, output):
        output_format = config.pop("format")
        formatter_class = FORMATTERS[output_format]
        return formatter_class(output=output, **config)

    def __getitem__(self, key):
        return self.__data[key]
