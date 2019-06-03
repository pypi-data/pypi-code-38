"""Subcommand3

Usage:
  {cli}
  {cli} (-h | --help)

Options:
  -h --help                            Show this screen.
"""
from owlmixin import OwlMixin, TList


class Args(OwlMixin):
    # Requires at least one field
    help: any


def run(args: Args):
    print(args.to_yaml())
