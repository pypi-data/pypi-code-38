""" Application entry point.

    python -m tasklog  ...

"""

import sys
from tasklog.cli import maincli

def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    try:
        exitCode = maincli(argv)
        sys.exit(exitCode)
    except:
        raise

if __name__ == "__main__":
    raise SystemExit(main(None))
