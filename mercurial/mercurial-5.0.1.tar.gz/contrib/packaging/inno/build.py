#!/usr/bin/env python3
# build.py - Inno installer build script.
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# This script automates the building of the Inno MSI installer for Mercurial.

# no-check-code because Python 3 native.

import argparse
import os
import pathlib
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--python',
                        required=True,
                        help='path to python.exe to use')
    parser.add_argument('--iscc',
                        help='path to iscc.exe to use')
    parser.add_argument('--version',
                        help='Mercurial version string to use '
                             '(detected from __version__.py if not defined')

    args = parser.parse_args()

    if not os.path.isabs(args.python):
        raise Exception('--python arg must be an absolute path')

    if args.iscc:
        iscc = pathlib.Path(args.iscc)
    else:
        iscc = (pathlib.Path(os.environ['ProgramFiles(x86)']) / 'Inno Setup 5' /
            'ISCC.exe')

    here = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
    source_dir = here.parent.parent.parent
    build_dir = source_dir / 'build'

    sys.path.insert(0, str(source_dir / 'contrib' / 'packaging'))

    from hgpackaging.inno import build

    build(source_dir, build_dir, pathlib.Path(args.python), iscc,
          version=args.version)
