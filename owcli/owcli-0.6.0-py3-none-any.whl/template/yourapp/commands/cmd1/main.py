"""Command1

Usage:
  {cli} <name> [-t <type>|--type <type>] [-v|-vv|-vvv]
  {cli} (-h | --help)

Options:
  <name>                        Name
  -t, --type <type>             Type
  -v                            Verbose (`-v` or `-vv` or `-vvv`)
  -h --help                     Show this screen.
"""
from owlmixin import OwlMixin, TOption


class Args(OwlMixin):
    name: str
    type: TOption[str]
    v: int


def run(args: Args):
    print(args.to_yaml())
