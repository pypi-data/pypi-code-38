#!/usr/bin/env python
#
# simple script to be used in hooks
#
# put something like this in the repo .hg/hgrc:
#
#     [hooks]
#     changegroup = python "$TESTDIR/printenv.py" <hookname> [exit] [output]
#
#   - <hookname> is a mandatory argument (e.g. "changegroup")
#   - [exit] is the exit code of the hook (default: 0)
#   - [output] is the name of the output file (default: use sys.stdout)
#              the file will be opened in append mode.
#
from __future__ import absolute_import
import argparse
import os
import sys

try:
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)
except ImportError:
    pass

parser = argparse.ArgumentParser()
parser.add_argument("name", help="the hook name, used for display")
parser.add_argument(
    "exitcode",
    nargs="?",
    default=0,
    type=int,
    help="the exit code for the hook",
)
parser.add_argument(
    "out", nargs="?", default=None, help="where to write the output"
)
parser.add_argument(
    "--line",
    action="store_true",
    help="print environment variables one per line instead of on a single line",
)
args = parser.parse_args()

if args.out is None:
    out = sys.stdout
    out = getattr(out, "buffer", out)
else:
    out = open(args.out, "ab")

# variables with empty values may not exist on all platforms, filter
# them now for portability sake.
env = [(k, v) for k, v in os.environ.items()
       if k.startswith("HG_") and v]
env.sort()

out.write(b"%s hook: " % args.name.encode('ascii'))
if os.name == 'nt':
    filter = lambda x: x.replace('\\', '/')
else:
    filter = lambda x: x

vars = [b"%s=%s" % (k.encode('ascii'), filter(v).encode('ascii'))
        for k, v in env]

# Print variables on out
if not args.line:
    out.write(b" ".join(vars))
else:
    for var in vars:
        out.write(var)
        out.write(b"\n")

out.write(b"\n")
out.close()

sys.exit(args.exitcode)
