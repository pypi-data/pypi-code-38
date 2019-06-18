import sys
import logging


def rest(*, n: int = 1):
    for i, line in zip(range(n), sys.stdin):
        sys.stderr.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--log",
        choices=list(logging._nameToLevel.keys()),
        default="INFO",
        dest="log_level",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # rest
    fn = rest
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-n", required=False, default=1, type=int, help="(default: 1)")

    args = parser.parse_args()
    params = vars(args).copy()
    logging.basicConfig(level=getattr(logging, params.pop("log_level")))
    return params.pop("subcommand")(**params)
