# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""CLI module for fedfind."""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import logging
import sys

import fedfind.const
import fedfind.exceptions
import fedfind.helpers
import fedfind.release

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)

def _release(rel):
    """Validity check for release parameter - must be an integer or
    rawhide.
    """
    if rel.isdigit() or rel.lower() == 'rawhide':
        return rel
    else:
        raise ValueError("Release must be integer or Rawhide.")

def images(args):
    """images sub-command function. Gets an appropriate Release
    instance and runs an appropriate query, based on the provided
    args.
    """
    # pylint:disable=too-many-branches
    try:
        rel = fedfind.release.get_release(
            dist=args.dist, release=args.release, milestone=args.milestone, compose=args.compose,
            respin=args.respin, cid=args.composeid, label=args.label)
        logger.debug("Release instance: %s", rel)
        if isinstance(rel, fedfind.release.Pungi4Release):
            if not rel.status in fedfind.const.PUNGI_SUCCESS:
                sys.exit("Compose {0} failed, or not yet complete!".format(rel))
        logger.info("Finding images for: %s %s", rel.dist, rel.version)
    except fedfind.exceptions.CidMatchError as err:
        sys.exit("Compose ID {0} of discovered compose at {1} does not match specified compose ID "
                 "{2}! Please report a bug.".format(err.release.cid, err.release.location,
                                                    args.composeid))
    except fedfind.exceptions.UnsupportedComposeError as err:
        sys.exit("Compose is unsupported. {0}".format(str(err)))
    except ValueError as err:
        sys.exit("Invalid arguments. {0}".format(str(err)))
    if args.generic_url:
        print(rel.https_url_generic)
        sys.exit()
    imgs = rel.all_images

    # arch
    if args.arch:
        if 'i386' in args.arch and not 'i686' in args.arch:
            args.arch.append('i686')
        elif 'i686' in args.arch and not 'i386' in args.arch:
            args.arch.append('i386')
        imgs = [img for img in imgs if img['arch'].lower() in args.arch]

    # type
    if args.type:
        # we never use the 'netinst' type any more, so be nice and
        # replace it with 'boot'
        if 'netinst' in args.type:
            logger.warning('Type "netinst" will never match, since fedfind 3.1.0! Using type '
                           '"boot" instead.')
            args.type.remove('netinst')
            args.type.append('boot')
        imgs = [img for img in imgs if img['type'].lower() in args.type]

    # payload
    if args.payload:
        imgs = [img for img in imgs if img['subvariant'].lower() in args.payload]

    # search
    if args.search:
        imgs = [img for img in imgs if any(term in img['path'].lower() for term in args.search)]

    for img in imgs:
        logger.debug("Subvariant: %s Type: %s Arch: %s", img['subvariant'],
                     img['type'], img['arch'])
        print(img['url'])

def parse_args():
    """Parse arguments with argparse."""
    parser = argparse.ArgumentParser(description=(
        "Tool for finding Fedora stuff. Currently finds images, using the "
        "images sub-command. See the image help for more details."))
    parser.add_argument(
        '-l', '--loglevel', help="The level of log messages to show",
        choices=('debug', 'info', 'warning', 'error', 'critical'), default='info')
    # This is a workaround for a somewhat infamous argparse bug
    # in Python 3. See:
    # https://stackoverflow.com/questions/23349349/argparse-with-required-subparser
    # http://bugs.python.org/issue16308
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    parser_images = subparsers.add_parser(
        'images', description="Find Fedora images. You can specify --composeid, --release and "
        "--label (and --dist if necessary), or --release, --milestone, --compose and --respin (and "
        "--dist if necessary) to identify the release you wish to find images for: e.g. -r 24 -m "
        "Beta -c 1 -i 1, -r 24 -m Branched -c 20160319 -i 0, -r 24 -m Alpha, or -r 22. If the "
        "values supplied do not entirely define a release, fedfind will usually try to guess what "
        "you mean. The other parameters can be used to filter the results in various ways. For "
        "all of the query parameters, you can specify a single value or several separated by "
        "commas. If you specify several values, fedfind will find images that match *any* value. "
        "If you pass multiple query parameters, fedfind will only find images that pass the check "
        "for all of the parameters. Matching is exact (but not case-sensitive) for all parameters "
        "except --search, which will match any image where at least one of the search terms occurs "
        "somewhere in the image URL.")
    parser_images.add_argument(
        '-d', '--dist', help="The 'dist' to search for. For most composes, this will be 'Fedora', "
        "the default value. To find two-week Atomic nightly composes, use 'Fedora-Atomic'. For "
        "post-release nightly Docker composes, use 'Fedora-Docker'. For post-release nightly Cloud "
        "composes, use 'Fedora-Cloud'. For the unofficial post-release live respin composes, use "
        "'FedoraRespin'.",
        choices=['Fedora', 'Fedora-Atomic', 'Fedora-Docker', 'Fedora-Cloud', 'FedoraRespin',
                 'Fedora-Container', 'Fedora-IoT'],
        default='Fedora', metavar="Fedora, Fedora-Atomic...")
    parser_images.add_argument(
        '-r', '--release', help="The Fedora release to search",
        type=_release, required=False, metavar="1-99 or Rawhide")
    parser_images.add_argument(
        '-m', '--milestone', help="A milestone to search (e.g. Alpha or Beta). 'Final' and 'RC' "
        "are synonyms. 'Branched' and 'Rawhide' are the two nightly compose types for 'Fedora' "
        "composes, see the wiki for more details. 'Production' is for candidate composes on the "
        "compose server (kojipkgs) and identified by a date and respin, as opposed to the same "
        "composes synced to alt and identified by label.", choices=
        ['Alpha', 'Beta', 'Final', 'RC', 'Atomic', 'Docker', 'Cloud', 'Branched', 'Rawhide',
         'Production', 'Respin', 'Updates', 'Updates-testing'])
    parser_images.add_argument(
        '-c', '--compose', '--date', help="A compose or date to search, e.g. 1 or 20160314. You "
        "may also pass a compose and respin combined, e.g. 1.2", required=False,
        metavar="20150213, 1, 1.1")
    parser_images.add_argument('-i', '--respin', required=False, type=int,
                               help="The respin of the compose to search (an integer)")
    parser_images.add_argument(
        '--composeid', help="A compose ID to search for. This is an alternative to release/"
        "milestone/compose/respin(/dist) for identifying the compose you want. compose ID format "
        "is DIST-REL-YYYYMMDD(.T).N, where DIST is the 'dist' or 'shortname' (usually 'Fedora'), "
        "REL is e.g. Rawhide or 24, T is a type identifier - 'n' for nightly, 't' for test (not "
        "used by Fedora yet), or omitted for production - and N is the respin. e.g. "
        "Fedora-Rawhide-20160319.n.0 or Fedora-24-20160319.1")
    parser_images.add_argument(
        '-l', '--label', help="A compose label to search for. Only Pungi 4 production composes "
        "have labels. Label format is MILESTONE-C.R, where MILESTONE is e.g. Alpha or Beta, C is "
        "an integer compose number, and R is an integer respin number, e.g. Alpha-1.5. You should "
        "also pass --release to identify the release.")
    parser_images.add_argument(
        '-a', '--arch', help="Architecture(s) to search for", required=False,
        type=fedfind.helpers.comma_list, metavar="armhfp,x86_64...")
    parser_images.add_argument(
        '-t', '--type', help="Image type(s) to search for", required=False,
        metavar="boot,dvd,live...", type=fedfind.helpers.comma_list)
    parser_images.add_argument(
        '-p', '--payload', help="Image payload (subvariant) to search for", required=False,
        metavar="workstation,lxde...", type=fedfind.helpers.comma_list)
    parser_images.add_argument(
        '-s', '--search', help="String(s) to search for anywhere in image URL", required=False,
        type=fedfind.helpers.comma_list, metavar="TERM1,TERM2")
    parser_images.add_argument(
        '-g', '--generic-url', help="Just display the HTTPS URL for the 'generic' tree for the "
        "given release - the preferred source for PXE boot kernel/initramfs and so on.",
        required=False, action='store_true')
    parser_images.set_defaults(func=images)
    return parser.parse_args()

def run():
    """Read in arguments, set up logging and run sub-command
    function."""
    args = parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), logging.INFO)
    logging.basicConfig(level=loglevel)
    args.func(args)

def main():
    """Main loop."""
    try:
        run()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted, exiting...\n")
        sys.exit(1)

if __name__ == '__main__':
    main()

# vim: set textwidth=100 ts=8 et sw=4:
