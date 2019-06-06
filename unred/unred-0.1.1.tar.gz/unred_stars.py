#!/usr/bin/env python3

from importlib import import_module
from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from unred.unred import *


argparser = ArgumentParser(
    prog='unred_stars.py',
    description='>> Script unreddens stars on the color-color plane <<',
    epilog='Copyright (c) 2018 Przemysław Bruś',
    formatter_class=RawTextHelpFormatter
)
argparser.add_argument(
    'stars_list',
    help=dedent('''\
    The name of a file which must contain columns with data:
    id x_color y_color x_err_color y_err_color
    ------------------------------------------
    int float float float float

    ''')
)
argparser.add_argument(
    'unred_sequence',
    help=dedent('''\
    The name of a file which must contain columns with data:
    x_color y_color
    ---------------
    float float

    The data must be sorted by INCREASING TEMPERATURE

    ''')
)
argparser.add_argument(
    'line_slope',
    help=dedent('''\
    A reddening line slope defined as E(y_color)/E(x_color)
    Example: E(U-B)/E(B-V) = 0.72

    '''),
    type=float
)
argparser.add_argument(
    'extinction_ratio',
    help=dedent('''\
    A ratio of total to selective extinction
    defined as A/E(x_color)
    Example: Av/E(B-V) = 3.1
    '''),
    type=float
)
argparser.add_argument(
    '--min',
    help=dedent('''\
    for each star print only the minimum value of extinction
    '''),
    action='store_true'
)
argparser.add_argument(
    '--max',
    help=dedent('''\
    for each star print only the maximum value of extinction
    '''),
    action='store_true'
)
argparser.add_argument(
    '-v',
    '--version',
    action='version',
    version=dedent('''\
    %(prog)s
    * Version: ''' + import_module('unred').__version__ + '''
    * Licensed under the MIT license:
    * http://opensource.org/licenses/MIT
    * ''' + argparser.epilog)
)

args = argparser.parse_args()
if args.min and args.max:
    print(argparser.prog + ": choose only one option: --min or --max")
    exit(1)

stars = args.stars_list
unred_sequence = args.unred_sequence
line_slope = args.line_slope
extinction_ratio = args.extinction_ratio
points = read_reddened_stars(stars)
model = read_unreddened_sequence(unred_sequence)
results = extinction(points, model, line_slope, extinction_ratio)

if args.min:
    results = select_extinction(results)
elif args.max:
    results = select_extinction(results, "max")

print_extinction(results)
