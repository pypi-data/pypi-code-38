# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse
import getpass
import sys
import textwrap

import qumulo.lib.util as util

try:
    # use argcomplete if available
    import argcomplete
except ImportError:
    argcomplete = None

class Subcommand(object):
    @staticmethod
    def options(parser):
        pass

class HelpCommand(Subcommand):
    NAME = 'help'
    DESCRIPTION = 'QQ documentation'

    @staticmethod
    def options(parser):
        pass

MAX_EDIT_DISTANCE_CHOICES = 5

class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    '''
    Custom subcommand help formatter that suppresses hidden subcommands from
    help.
    '''
    def _format_action(self, action):
        '''
        Override _format_action, which is called during parser.format_help() to
        format a single (sub)command. This implementation simply returns no
        information (empty string) for actions (i.e. (sub)commands) that have
        been suppressed.  The default behavior being overridden simply prints
        "== SUPPRESSED ==" for the action.
        '''
        parts = super(SubcommandHelpFormatter, self)._format_action(action)
        if action.help == argparse.SUPPRESS:
            return ''
        return parts

class HelpfulSubparserChoicesWrapper(object):
    '''
    A wrapper around the subparser choices that provides more helpful
    suggestions on the CLI for flubbed commands. Also allows you to type
    partial parts of the command if you can't remember the full thing.

    You can still --help and | grep to find a subcommand, but hopefully this
    will make the error message on a snafu'd subcommand be less unhelpful.
    '''

    def __init__(self, choices, num_choices):
        """
        @p choices is an iterable of string choices for an argparse action
        @p num_choices is the number of suggestions to display when we fall
           back to using edit distance as a proxy for closeness
        """
        self._real_choices = choices
        self._last_contains_check = None
        self._num_choices = num_choices

    def __contains__(self, arg):
        # When argparse is validating the subparser sub-command, it checks
        # if choices contains the argument. We can remember this to know
        # what the user typed in
        self._last_contains_check = arg
        return arg in self._real_choices

    def __iter__(self):
        # No contains was called, just act like the default.
        if self._last_contains_check is None:
            return iter(self._real_choices)

        # Find all choices that contain the last_contains_check as a substring
        # This allows the user to type partial matches to sub-commands
        choices = []
        remaining = []
        for choice in sorted(self._real_choices):
            if self._last_contains_check in choice:
                choices.append(choice)
            else:
                remaining.append(choice)

        # In the event that the user flubbed the sub-command and we have no
        # suggestions based on substring matches, use edit distance to give the
        # user helpful-ish suggestions
        if not choices:
            edit_distances = []
            for choice in remaining:
                dist = util.edit_distance(choice, self._last_contains_check)
                edit_distances.append((dist, choice))
            edit_distances.sort(key=lambda x: x[0])
            choices.extend(
                x[1] for x in edit_distances[:self._num_choices])
        return iter(choices)

    def keys(self):
        '''
        N.B. argcomplete will call keys() on parser.choices to get options
        for auto-completion. This needs to be a pass-through to real_choices
        to support this use-case.
        '''
        return self._real_choices.keys()

def parse_subcommand(cls, subparsers):
    # Add a subparser for each subcommand
    subparser = subparsers.add_parser(
        cls.NAME, description=cls.DESCRIPTION, help=cls.DESCRIPTION)

    # Add options particular to the subcommand
    cls.options(subparser)

    # Set the subcommand class
    subparser.set_defaults(subcommand=cls)

    return subparser

def parse_help_options(cls, subparsers):
    '''
    help commands have their own subclass for which we need another subparser
    '''
    help_subparser = subparsers.add_parser(
        cls.NAME, description=cls.DESCRIPTION, help=cls.DESCRIPTION)
    help_subparsers = help_subparser.add_subparsers()
    help_subparsers.choices = HelpfulSubparserChoicesWrapper(
        help_subparsers.choices, MAX_EDIT_DISTANCE_CHOICES)
    for help_cls in sorted(
            HelpCommand.__subclasses__(), key=lambda help_cls: help_cls.NAME):
        parse_subcommand(help_cls, help_subparsers)

def parse_options(parser, argv):
    parser.formatter_class = SubcommandHelpFormatter
    subparsers = parser.add_subparsers(
        title="Qumulo Command Line Interface",
        description="Interact with the RESTful API by the command line",
        help="Action", metavar="")
    subparsers.choices = HelpfulSubparserChoicesWrapper(
        subparsers.choices, MAX_EDIT_DISTANCE_CHOICES)

    for cls in sorted(Subcommand.__subclasses__(), key=lambda cls: cls.NAME):
        if cls.NAME == 'help':
            parse_help_options(cls, subparsers)
        else:
            parse_subcommand(cls, subparsers)

    if argcomplete is not None:
        argcomplete.autocomplete(parser)
    return parser.parse_args(argv)

def read_password(user=None, prompt=None):
    if prompt is not None:
        return getpass.getpass(prompt)
    return getpass.getpass("Enter password for %s: " % user)

def ask(command, message):
    # Wrap long lines to make the CLI output more readable
    wrapped_message = '\n'.join(
        textwrap.fill(line) for line in message.splitlines())
    f = raw_input("%s (yes/no): " % wrapped_message)
    if f.lower() == 'no':
        print 'Cancelling the %s request' % command
        return False
    elif f.lower() != 'yes':
        raise ValueError("Please enter 'yes' or 'no'")

    return True

def str_decode(arg):
    '''
    Custom argparse type for decoding based on stdin-specific encoding. If stdin
    does not provide an encoding (e.g. is a pipe), then default to utf-8 for
    the sake of doing something relatively sane.
    '''
    return unicode(arg, sys.stdin.encoding or 'utf-8')
