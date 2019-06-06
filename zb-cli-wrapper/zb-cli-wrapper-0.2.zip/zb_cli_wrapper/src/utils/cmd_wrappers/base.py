#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import yaml


class CommandParserError(Exception):
    pass


class CommandWrapper(object):
    """ This class implements a common parent for CLI command wrappers.

        Args:
            cli_getter: a reference to the function that returns CLI object instance.
            dev: a reference to a device that uses this command wrapper. Useful to access device logger

        Note:
            The CLI object changes between test cases, but the board object does not,
            thus the getter function has to be used to reference the current CLI
            instance while sending commands/receiving responses.

        The CLI:
            CLI is any object, that implements the following method:
                def write_command(self, command, wait_for_success=True, timeout=1.0)

            Which returns a list of strings, representing command responses.


        Usage:
            In order to extend a board object, that implements CLI interface,
            a simple cli property getter has to be implemented in every CLI device class:
                def get_cli(self):
                    return self.cli

            Afterwards, a command wrapper should be added to the board object
            as its new property e.g.:
                self.test = NewTestCommandsWrapper(cli_getter)

            That way it is possible to access command groups with more intuitive way,
            avoiding multiple class inheritance e.g.:
                board.test.start()
                board.test.configure.length(100)

        Reasoning:
            The class, that implements a command parsing logic, is not
            an instance of a board and does not need access to all of its internal
            properties to work correctly. Because of that, it is better to attach
            command parser as a property with methods, than using multi level
            inheritance.
            Complex methods, that require sending and parsing multiple commands
            should be implemented differently, using command wrappers as primitives.
    """
    def __init__(self, cli_getter, dev=None):
        self.cli_getter = cli_getter
        if dev is not None:
            self.dev = dev

    @property
    def cli(self):
        """ CLI communicator. Initializes on first usage. Make sure that this property is not called in constructor.
        """
        return self.cli_getter()

    def get_cli(self):
        """ Returns current CLI object instance.
        """
        return self.cli

    def clear_buffer(self):
        """ Writes a new line character and reads all input lines in order to get
            clean input for further CLI commands.
        """
        self.cli.clear()

    @staticmethod
    def _parse_values(results_dict):
        """ Iterates through all keys and converts:
               - values with units into (value, 'unit') tuples
               - true/false into actual bool variables

            For example:
                "123.456ms" -> (123.456, 'ms')
                "12,34 %" -> (12.34, '%')
                "true" -> True
        """
        value_unit_re = re.compile(r'^\s*([0-9,\.,\,]+)\s*([^0-9]+)\s*$')
        true_re = re.compile(r'^\s*true\s+$', flags=re.IGNORECASE)
        false_re = re.compile(r'^\s*false\s+$', flags=re.IGNORECASE)
        results = {}
        for key, value in results_dict.items():
            if isinstance(value, dict):
                results[key] = CommandWrapper._parse_values(value)
            elif re.match(value_unit_re, str(value)):
                value_unit = re.match(value_unit_re, value).groups()
                results[key] = (float(value_unit[0]), value_unit[1])
            elif re.match(true_re, str(value)):
                results[key] = True
            elif re.match(false_re, str(value)):
                results[key] = False
            else:
                results[key] = (value)

        return results

    @staticmethod
    def _parse_yaml_results(responses, parse_values=True):
        """ Parses command results presented in YAML format.

            Params:
                responses: list of lines with CLI response
                parse_units: if True, when applicable the 'results' values are
                    being parsed. See _parse_values to see how the parsing is done.

            Returns:
                results (dict): keys are the same as inside received YAML
        """
        results_yaml = ''

        # Check if there are any responses to parse.
        if responses is None:
            return None

        # Treat every line with ':' character as a valid YAML input line.
        for response in responses:
            if response.find(':') == -1:
                continue
            # TODO: remove the .replace(...) once CLI returns whitespaces instead of tabs
            results_yaml += '\n' + response.replace('\t', '  ')

        # Parse YAML string into dictionary.
        try:
            results_dict = yaml.full_load(results_yaml)
        except yaml.scanner.ScannerError as e:
            raise CommandParserError("Cannot results as YAML:\n{}".format(results_yaml)) from e

        if parse_values:
            # Convert values with unit into tuples, return.
            return CommandWrapper._parse_values(results_dict)
        else:
            return results_dict
