# =============================================================================
# Copyright [2018] [Miguel Alex Cantu]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================

import argparse

parser = argparse.ArgumentParser(
    usage = '%(prog)s',
    description = "A tool that performs a lookup on serveral verse references"
)

parser.add_argument(
    '-f',
    '--file',
    help = 'The file containing a line seperated list of verse references',
    required = False
)

parser.add_argument(
    '-v',
    '--verses',
    help = 'A comma delimited string listed the verse references to lookup',
    required = False
)

parser.add_argument(
    '-r',
    '--references-first',
    action = 'store_true',
    required = False
)

def get_parser():
    return parser
