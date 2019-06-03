"""Subcommand2

Usage:
  {cli} (action1|action2|action3) --target <target>... [-v|--verbose]
  {cli} (-h | --help)

Options:
  --target <target>...              Targets
  -v --verbose                      Verbose
  -h --help                         Show this screen.
"""
from owlmixin import OwlMixin, TList


class Args(OwlMixin):
    action1: bool
    action2: bool
    action3: bool
    target: TList[str]
    verbose: bool


def run(args: Args):
    print(args.to_yaml())

