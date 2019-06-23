#!/usr/bin/env python

#   Copyright (c) 2017-2019 Atrio, Inc.
#   All rights reserved.

"""Alfredo Command Line Interface

Usage:
    alfredo login [-i <input>]
    alfredo logout
    alfredo ruote [-C|-R|-U|-D|-X] [-i <input>] [-o <output>] <path>...
    alfredo virgo [-C|-R|-U|-D|-X] [-i <input>] [-o <output>] <path>...

Options:

    Operations:

        -C  --create    Create.
        -R  --retrieve  Retrieve (default operation).
        -X  --replace   Replace.
        -U  --update    Update.
        -D  --delete    Delete.

    Input:

        -i <input> --input <input>
                        <input> is a valid JSON or YAML string with the object to be sent to the operation.
                        If not given, and input required, it is fetched from <stdin>.

    Output:

        -o <output> --output <output>
                        <output> is a dot-separated list of attributes to navigate from a list or object.
                        You can use numbers to select items of an array. Negative numbers allowed.
                        You can use commas to get several attributes
                        Examples:
                            alfredo ruote apps -o name
                            alfredo ruote jobs -o id,name,queue
                            alfredo ruote apps -o 0
                            alfredo ruote jobs id:723 -o output_files

    Others:

        -h --help       Show this screen.
        -V --version    Show version.

    Examples:

        Register a new user

            alfredo ruote users -C -i "{password: '****', email: alice@example.com}"

        Get a token

            alfredo ruote sso token_by_email -C -i "{password: '****', email: alice@example.com}"

        Login (and store the token for future usage)

            alfredo login -i "{password: '****', email: alice@example.com}"

        Get the current user info

            alfredo ruote users me

        Change the first name of the current user

            alfredo ruote users me -U -i "first_name: Bob"

        Get the details of a user by id

            alfredo ruote users id:343

        Get the list of clusters

            alfredo ruote clusters

        Create a cluster given a name

            alfredo ruote clusters -C -i "name: example cluster"

        Get the list of queues

            alfredo ruote queues

        Create a queue

            alfredo ruote queues -C -i "{cluster: 383, name: q}"

        List the user files

            alfredo ruote files

        Upload a file from a local path

            alfredo ruote files -C -i "file: /home/alice/test.txt"

        Delete a file by id

            alfredo ruote files id:51 -D

        Create an app

            alfredo ruote apps -C -i "{container_checksum: 00000000000, name: app, container_url: http://app.example.com/}"

        Create a job

             alfredo ruote jobs -C -i '{name: job, queue: 12, app: 243}'

"""

import datetime
import os.path
import re
import sys

import ruamel.yaml as yaml
from docopt import docopt, DocoptExit
from requests.exceptions import ConnectionError
from ruamel.yaml.parser import ParserError

import alfredo


def represent_unicode(self, data):
    return self.represent_str(data.encode('utf-8'))


if sys.version_info < (3,):
    yaml.representer.Representer.add_representer(unicode, represent_unicode)


class Command(object):
    def __init__(self, arguments):
        self._arguments = arguments

    @property
    def token_file(self):
        return '.token'

    def is_logged_in(self):
        return os.path.isfile(self.token_file)

    @property
    def token(self):
        if self.is_logged_in():
            return open(self.token_file, 'r').read()
        return None

    @property
    def input(self):
        if self._arguments['--input']:
            return self.input_from(self._arguments['--input'])

        try:
            if sys.stdin.isatty():
                sys.stdout.write("Enter input:                \n")
        except ValueError:
            return {}

        return self.input_from(sys.stdin.read())

    @staticmethod
    def input_from(input_str):
        try:
            input_value = yaml.safe_load(input_str)
            if not isinstance(input_value, dict):
                sys.stderr.write("Parser error: Expected dict.\n")
                exit(CLI.INPUT_ERROR)
            return input_value or {}
        except ParserError as e:
            sys.stderr.write("Parser error: {0}\n".format(e))
            exit(CLI.INPUT_ERROR)

    def run(self):
        raise NotImplementedError()


class LoginCommand(Command):
    def run(self):
        response = alfredo.ruote().sso.token_by_email.create(**self.input)
        if response.ok:
            with open(self.token_file, 'w') as f:
                f.write(response.token)
        else:
            sys.stdout.write(str(response))
            sys.stdout.flush()
        return response.exit_code


class LogoutCommand(Command):
    def run(self):
        if self.is_logged_in():
            os.remove(self.token_file)
            return CLI.SUCCESS
        return CLI.INPUT_ERROR


class AlfredoCommand(Command):
    def run(self):
        response = self.get_response()
        self.print_response(response)
        return response.exit_code

    def get_response(self):
        target = self.get_target()

        if self._arguments['-C']:
            sys.stderr.write("Creating...\r")
            response = target.create(**self.input)
        elif self._arguments['-U']:
            sys.stderr.write("Updating...\r")
            response = target.update(**self.input)
        elif self._arguments['-X']:
            sys.stderr.write("Replacing...\r")
            response = target.replace(**self.input)
        elif self._arguments['-D']:
            sys.stderr.write("Deleting...\r")
            response = target.delete()
        else:
            sys.stderr.write("Retrieving...\r")
            response = target.retrieve()

        sys.stderr.write("                              \r")
        return response

    def get_initial_target(self):
        raise NotImplementedError()

    def get_target(self):
        target = self.get_initial_target()
        for p in self._arguments['<path>']:
            try:
                call = re.search('([^:]+):(.+)', p)
                if call:
                    try:
                        target = getattr(target, call.group(1))(call.group(2))
                    except AttributeError:
                        target = getattr(target, p)
                else:
                    target = getattr(target, p)
            except AttributeError:
                sys.stderr.write("                    \r")
                sys.stderr.write("Unknown path {path!r}\n".format(path='/'.join(self._arguments['<path>'])))
                exit(1)
        return target

    def print_response(self, response):
        if hasattr(response, 'stream') and hasattr(response.stream, '__call__'):
            response.stream(sys.stdout)
        elif self._arguments['--output']:
            self.print_output_attrs(response)
        else:
            sys.stdout.write(str(response))
            sys.stdout.flush()

    def print_output_attrs(self, response):
        result = response.native()
        attr_list = self._arguments['--output'].split(',')
        result = self.pluck(result, attr_list=attr_list)
        sys.stdout.write(yaml.dump(result, default_flow_style=False))
        sys.stdout.flush()

    def pluck(self, dict_or_list, attr_list):
        if not attr_list:
            return dict_or_list

        if isinstance(dict_or_list, list):
            return self.pluck_list(dict_or_list, attr_list)
        else:
            return self.pluck_dict(dict_or_list, attr_list)

    def pluck_list(self, target_list, attr_list):
        if len(attr_list) == 1 and re.search('^[0-9]+$', attr_list[0]):
            return target_list[int(attr_list[0])]
        else:
            return [self.pluck(item, attr_list) for item in target_list]

    def pluck_dict(self, target_dict, attr_list):
        if len(attr_list) == 1:
            return self.pluck_dict_dot(target_dict, attr_list[0].split('.'))
        elif len(attr_list) > 1:
            return {key.strip(): self.pluck(target_dict, [key]) for key in attr_list if key != ''}

    def pluck_dict_dot(self, target_dict, attr_dot_list):
        if len(attr_dot_list) > 1:
            return self.pluck_dict_dot(target_dict[attr_dot_list[0].strip()], attr_dot_list[1:])
        elif len(attr_dot_list) == 1:
            return target_dict[attr_dot_list[0].strip()]
        else:
            return target_dict


class RuoteCommand(AlfredoCommand):
    def get_initial_target(self):
        return alfredo.ruote(token=self.token)


class VirgoCommand(AlfredoCommand):
    def get_initial_target(self):
        return alfredo.virgo()


class CLI(object):

    SUCCESS = 0
    UNKNOWN_ERROR = 1
    COMMAND_LINE_ERROR = 2
    INPUT_ERROR = 3
    HTTP_UPSTREAM_CLIENT_ERROR = 4
    HTTP_UPSTREAM_SERVER_ERROR = 5
    CONNECTION_ERROR = 6

    commands = {
        'login': LoginCommand,
        'logout': LogoutCommand,
        'ruote': RuoteCommand,
        'virgo': VirgoCommand,
    }

    @staticmethod
    def run(doc, version):
        try:
            arguments = docopt(doc=doc, version=version)
        except DocoptExit as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            exit(CLI.COMMAND_LINE_ERROR)

        for command_name in CLI.commands.keys():
            if arguments[command_name]:
                try:
                    exit_code = CLI.commands[command_name](arguments).run()
                    if sys.argv[0].endswith('alfredo'):
                        CLI.cleanup()
                    exit(int(exit_code))
                except ConnectionError as e:
                    sys.stderr.write(repr(sys.exc_info()))
                    sys.stderr.write('\n')
                    sys.stderr.write(str(e))
                    sys.stderr.write('\n')
                    exit(CLI.CONNECTION_ERROR)
                except IOError as e:
                    sys.stderr.write(repr(sys.exc_info()))
                    sys.stderr.write('\n')
                    sys.stderr.write(str(e))
                    sys.stderr.write('\n')
                    exit(e.errno or CLI.UNKNOWN_ERROR)
                except Exception as e:
                    if not sys.argv[0].endswith('alfredo'):
                        raise
                    with open('.alfredo-errors.log', 'a') as f:
                        f.write("ERROR {0}\n{1!r}-{1!s}\n{1!s}\n".format(datetime.datetime.utcnow(), e, sys.exc_info()))
                    sys.stderr.write("Unknown error              \n")
                    exit(CLI.UNKNOWN_ERROR)

    @staticmethod
    def cleanup(*args):
        CLI.safe_call(sys.stderr.flush)
        CLI.safe_call(sys.stderr.close)

        CLI.safe_call(sys.stdout.flush)
        CLI.safe_call(sys.stdout.close)

    @staticmethod
    def safe_call(callable):
        try:
            callable()
        except:
            pass


def main():
    if sys.argv[0].endswith('alfredo'):
        sys.excepthook = CLI.cleanup
    CLI.run(__doc__, alfredo.__version__)


if __name__ == '__main__':
    main()
