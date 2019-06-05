#!/usr/bin/env python3
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

"""Code to build Mercurial WiX installer."""

import argparse
import os
import pathlib
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--name',
                        help='Application name',
                        default='Mercurial')
    parser.add_argument('--python',
                        help='Path to Python executable to use',
                        required=True)
    parser.add_argument('--sign-sn',
                        help='Subject name (or fragment thereof) of certificate '
                             'to use for signing')
    parser.add_argument('--sign-cert',
                        help='Path to certificate to use for signing')
    parser.add_argument('--sign-password',
                        help='Password for signing certificate')
    parser.add_argument('--sign-timestamp-url',
                        help='URL of timestamp server to use for signing')
    parser.add_argument('--version',
                        help='Version string to use')
    parser.add_argument('--extra-packages-script',
                        help=('Script to execute to include extra packages in '
                              'py2exe binary.'))
    parser.add_argument('--extra-wxs',
                        help='CSV of path_to_wxs_file=working_dir_for_wxs_file')
    parser.add_argument('--extra-features',
                        help=('CSV of extra feature names to include '
                              'in the installer from the extra wxs files'))

    args = parser.parse_args()

    here = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
    source_dir = here.parent.parent.parent

    sys.path.insert(0, str(source_dir / 'contrib' / 'packaging'))

    from hgpackaging.wix import (
        build_installer,
        build_signed_installer,
    )

    fn = build_installer
    kwargs = {
        'source_dir': source_dir,
        'python_exe': pathlib.Path(args.python),
        'version': args.version,
    }

    if not os.path.isabs(args.python):
        raise Exception('--python arg must be an absolute path')

    if args.extra_packages_script:
        kwargs['extra_packages_script'] = args.extra_packages_script
    if args.extra_wxs:
        kwargs['extra_wxs'] = dict(
            thing.split("=") for thing in args.extra_wxs.split(','))
    if args.extra_features:
        kwargs['extra_features'] = args.extra_features.split(',')

    if args.sign_sn or args.sign_cert:
        fn = build_signed_installer
        kwargs['name'] = args.name
        kwargs['subject_name'] = args.sign_sn
        kwargs['cert_path'] = args.sign_cert
        kwargs['cert_password'] = args.sign_password
        kwargs['timestamp_url'] = args.sign_timestamp_url

    fn(**kwargs)
