"""Subcommand1

Usage:
  {cli} <names>... [-f|--flag]
  {cli} (-h | --help)

Options:
  <names>...                           Names
  -f --flag                            Flag
  -h --help                            Show this screen.
"""
from owlmixin import OwlMixin, TList


class Args(OwlMixin):
    names: TList[str]
    flag: bool


def run(args: Args):
    print(args.to_yaml())

