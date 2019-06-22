import typing as t
import sys
import contextlib
import logging


def rest(*, n: int = 1, debug: bool) -> None:
    """first n lines, write to stderr, rest, write to stdout"""
    for i, line in zip(range(n), sys.stdin):
        sys.stderr.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)


def too(*, cmds: t.List[str], shell: bool, dump_context: bool, debug: bool) -> None:
    """combine multiple commands' stream, keep all foreground and kill all in one Ctrl+C"""
    import shlex
    from ioknife.too import too as run_too

    if cmds:
        commands = [shlex.split(cmd) for cmd in cmds]
    else:
        commands = [
            shlex.split(line.rstrip())
            for line in sys.stdin
            if line.strip() and not line.startswith("#")
        ]

    if dump_context:
        for cmd in commands:
            print(cmd)
        sys.exit(0)
    run_too(commands, debug=debug, shell=shell)


def grepo(pattern: str, filename: t.Optional[str] = None, *, debug: bool) -> None:
    """grep -o <pattern> and write matched line to stderr"""

    # TODO: optimization (use native grep command, or rg or ag)
    import re

    rx = re.compile(pattern)

    with contextlib.ExitStack() as s:
        rf = sys.stdin
        if filename is not None:
            rf = s.enter_context(open(filename))
        for line in rf:
            m = rx.search(line)
            if m is not None:
                print(f"\x1b[90mmatched: {line.rstrip()}\x1b[0m", file=sys.stderr)
                print(m.group(0))
                sys.stderr.flush()
                sys.stdout.flush()


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

    # grepo
    fn = grepo  # type: ignore
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("pattern")
    sparser.add_argument("filename", nargs="?")

    # too
    fn = too  # type: ignore
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--cmd", action="append", dest="cmds")
    sparser.add_argument("--shell", action="store_true")
    sparser.add_argument("--dump-context", action="store_true")

    args = parser.parse_args()
    params = vars(args).copy()
    logging.basicConfig(level=getattr(logging, params.pop("log_level")))
    params.pop("subcommand")(**params)
