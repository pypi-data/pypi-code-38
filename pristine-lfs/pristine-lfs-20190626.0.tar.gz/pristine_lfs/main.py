#############################################################################
# pristine-lfs
#
# store pristine tarballs in Git LFS
#
# Copyright (C) 2019 Collabora Ltd
# Andrej Shadura <andrew.shadura@collabora.co.uk>

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License version 2
# text for more details.

# You should have received a copy of the GNU General Public
# License along with this package; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA
#############################################################################

from gettext import gettext as _
import os
import sys
from . import util
from .util import *
import logging
import argparse
import sh

def find_branch(branch: str) -> str:
    if check_branch(branch) is None:
        remote_branches = find_remote_branches(branch)
        if remote_branches:
            commit, branch = remote_branches[0]
        else:
            raise util.Abort(_('No branch {branch} found, not even among remote branches').format(branch=branch))
    return branch

def do_commit(args: argparse.Namespace):
    if check_branch(args.branch) is None:
        if find_remote_branches(args.branch):
            track_remote_branch(args.branch)
        else:
            reset_index()
    commit_lfs_file(args.tarball, args.branch)

def do_checkout(args: argparse.Namespace):
    branch = find_branch(args.branch)
    checkout_lfs_file(branch, args.tarball, args.outdir)

def do_list(args: argparse.Namespace):
    branch = find_branch(args.branch)
    for f in list_lfs_files(branch):
        print(f)

def main():
    prog = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(description=_('store pristine tarballs in Git LFS'), prog=prog)
    parser.add_argument('-v', '--verbose', action='count', help=_('be more verbose'))
    parser.add_argument('--debug', action='store_const', const=2, dest='verbose', help=_('be debuggingly verbose'))
    parser.set_defaults(verbose=0)
    subparsers = parser.add_subparsers(required=True)

    parser_commit = subparsers.add_parser('commit', help=_('commit a tarball'))
    parser_commit.add_argument('-m', '--message', default=None, help=_('commit message'))
    parser_commit.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_commit.add_argument('tarball', type=argparse.FileType('rb'), help=_('tarball to commit'))
    parser_commit.add_argument('upstream', nargs='?', default=None, help=_('ignored'))
    parser_commit.set_defaults(func=do_commit)

    parser_checkout = subparsers.add_parser('checkout', help=_('checkout a tarball'))
    parser_checkout.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_checkout.add_argument('tarball', help=_('tarball to check out'))
    parser_checkout.add_argument('outdir', nargs='?', default='.', help=_('output directory for the tarball'))
    parser_checkout.set_defaults(func=do_checkout)

    parser_list = subparsers.add_parser('list', help=_('list tarballs stored in the repository'))
    parser_list.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_list.set_defaults(func=do_list)

    args = parser.parse_args()

    logging.basicConfig(format='{levelname[0]}: {message!s}', style='{', level=(logging.WARNING - 10 * args.verbose))

    try:
        args.func(args)
    except sh.ErrorReturnCode as e:
        print(_('Failed to run %s:') % e.full_cmd, file=sys.stderr)
        print(e.stderr.decode(sh.DEFAULT_ENCODING, "replace"), file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt as e:
        print(file=sys.stderr)
        print(_('about: Interrupted by user'), file=sys.stderr)
        sys.exit(1)
    except util.Abort as e:
        print(_("abort: %s\n") % e, file=sys.stderr)
        sys.exit(1)
