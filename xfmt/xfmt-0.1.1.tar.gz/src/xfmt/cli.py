#!/usr/bin/env python3
"""
Functions that are expected to be invoked only from the cli, directly or indirectly.
"""
import contextlib
import logging
import os
import sys
from datetime import datetime

import black  # type: ignore
import click
import colorama  # type: ignore
from xfmt import misc

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def _exit_codes():
    try:
        yield
    except Exception as e:  # pylint: disable=W0703
        logger.critical(e)
        exit(1)
    exit(0)


@contextlib.contextmanager
def _exit_indicator():
    # Leave at least two blank spaces at the end for symmetry
    num_repetition = (black.DEFAULT_LINE_LENGTH - 2) // 3
    try:
        yield
    except Exception:
        print("  ⛈" * num_repetition, file=sys.stderr)
        raise
    print("  ☀️" * num_repetition, file=sys.stderr)


def _pprint_diff(diff):
    for line in diff.split("\n"):
        if line.startswith(" ") or line == "":
            print(line)
        elif line.startswith("---"):
            print(colorama.Style.BRIGHT + line + colorama.Style.RESET_ALL)
        elif line.startswith("+++"):
            print(colorama.Style.BRIGHT + line + colorama.Style.RESET_ALL)
        elif line.startswith("@@"):
            print(colorama.Fore.CYAN + line + colorama.Fore.RESET)
        elif line.startswith("+"):
            print(colorama.Fore.GREEN + line + colorama.Fore.RESET)
        elif line.startswith("-"):
            print(colorama.Fore.RED + line + colorama.Fore.RESET)
        else:
            logger.debug(">>>%s<<<", line)
            raise RuntimeError("Unrecognized diff format")


class _DriverFilter(logging.Filter):  # pylint: disable=R0903
    """
    A filter dedicated to curbing the excessive verbosity of `lib2to3.pgen2.driver`
    and, more importantly, `black.blib2to3.pgen2.driver`.
    """

    def filter(self, record: logging.LogRecord):
        if record.module == "driver":
            return False
        return True


def _init_logging():
    handler = logging.FileHandler("main.log")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)8s] %(name)s %(filename)s:%(lineno)d %(message)s"
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    root_logger.addFilter(_DriverFilter())


@click.command()
@click.argument("tops", type=click.STRING, nargs=-1, required=True)
@click.option("--fix", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
def main(tops, fix, debug):
    """Recursively check formatting of files under path
    """
    with _exit_codes():
        if debug:
            _init_logging()
        logger.info("Logging initialized at %s", datetime.now().isoformat())
        formatters = misc.get_formatters()
        paths = set()
        for top in tops:
            if os.path.isfile(top):
                paths.add(top)
            else:
                paths.update(os.path.join(top, path) for path in misc.collect(top))
        for path in paths:
            logger.info("Checking %s", path)
            try:
                feedback = misc.check(path, formatters, fix)
                for chunk in feedback:
                    _pprint_diff(chunk)
            except LookupError as e:
                logger.debug(e)


if __name__ == "__main__":
    main()  # pylint: disable=E1120
