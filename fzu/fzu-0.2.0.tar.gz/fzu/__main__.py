#!/usr/bin/env python
"""Fuzzy search unicode symbols (requires fzf installed)"""

from argparse import ArgumentParser
from subprocess import run, PIPE
from pathlib import Path
from zipfile import is_zipfile
import sys
from getpass import getuser
from tempfile import gettempdir
import unicodedata

from fzu.symbols import symbols

__version__ = '0.2.0'

tmp_dir: Path = Path(gettempdir()) / f'fzu-{getuser()}'
symbols_dir: Path = tmp_dir / 'symbols'


def has_fzf():
    try:
        out = run(['fzf', '--help'], capture_output=True)
        return out.returncode == 0
    except OSError:
        return False


def should_create_dir(exe):
    if not tmp_dir.exists():
        return True

    return Path(exe).stat().st_mtime > tmp_dir.stat().st_mtime


def create_symbols():
    symbols_dir.mkdir(parents=True, exist_ok=True)
    for sym in symbols:
        try:
            char = unicodedata.lookup(sym)
        except KeyError:
            # TODO: Warn
            continue

        with open(symbols_dir / sym, 'w') as out:
            out.write(char)


def main():
    parser = ArgumentParser(description=__doc__, prog='fzu')
    parser.add_argument(
        '--version', help='print version & exit', action='store_true',
        default=False)
    args = parser.parse_args()

    if args.version:
        print(__version__)
        raise SystemExit()

    exe = sys.argv[0]
    if should_create_dir(exe):
        create_symbols()

    if is_zipfile(exe):
        # FIXME
        ...

    if not has_fzf():
        raise SystemExit('error: fzf not found, please install it')

    out = run(['fzf', '--preview', 'cat {}'], cwd=symbols_dir, stdout=PIPE)
    if out.returncode != 0:
        raise SystemExit()

    name = out.stdout.decode('utf-8').strip()
    try:
        char = unicodedata.lookup(name)
    except KeyError:
        raise SystemExit(f'error: unknown name - {name!r}')

    print(char)


if __name__ == '__main__':
    main()
