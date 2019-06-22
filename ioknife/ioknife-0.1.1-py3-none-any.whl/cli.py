import typing as t
import sys
import logging


def rest(*, n: int = 1, debug: bool) -> None:
    for i, line in zip(range(n), sys.stdin):
        sys.stderr.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)


def too(*, cmds: t.List[str], shell: bool, debug: bool) -> None:
    """Combine multiple commands' stream, keep all foreground and kill all in one Ctrl+C"""
    import shlex
    from ioknife.too import too as run_too

    commands = [shlex.split(cmd) for cmd in cmds]
    run_too(commands, debug=debug, shell=shell)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.print_usage = parser.print_help  # type: ignore
    parser.add_argument(
        "--logging",
        choices=list(logging._nameToLevel.keys()),
        default="INFO",
        dest="log_level",
    )
    parser.add_argument("--debug", action="store")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # rest
    fn = rest
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-n", required=False, default=1, type=int, help="(default: 1)")

    # too
    fn = too  # type: ignore
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--cmd", action="append", dest="cmds")
    sparser.add_argument("--shell", action="store_true")

    args = parser.parse_args()
    params = vars(args).copy()
    logging.basicConfig(level=getattr(logging, params.pop("log_level")))
    params.pop("subcommand")(**params)
