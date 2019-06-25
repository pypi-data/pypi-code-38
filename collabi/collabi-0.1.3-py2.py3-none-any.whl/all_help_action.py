"""Provides logic for recursively descending all argparse help actions to show usage for subparsers.
"""
from argparse import _HelpAction, _SubParsersAction

class AllHelpAction(_HelpAction):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        print
        formats = []
        self._get_subparser_formats(formats, parser._actions)
        for fmt in formats:
            print '-'*70
            print fmt
        parser.exit()

    def _get_subparser_formats(self, formats, actions, indent=0):
        for action in actions:
            if isinstance(action, _SubParsersAction):
                for choice, subparser in action.choices.items():
                    formats.append(subparser.format_help())
                    self._get_subparser_formats(formats, subparser._actions)
