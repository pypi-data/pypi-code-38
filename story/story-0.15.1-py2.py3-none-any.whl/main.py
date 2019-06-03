# -*- coding: utf-8 -*-
import sys

try:
    # Allow keyboard interrupts of CLI import.
    from .cli import cli

    # Import commands for CLI.

    from .commands import *  # noqa

except KeyboardInterrupt:
    print('Aborted!')
    sys.exit(1)

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
