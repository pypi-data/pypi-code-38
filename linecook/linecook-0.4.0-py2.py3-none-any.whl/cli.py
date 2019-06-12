#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
`linecook` cli to prepare lines of text for easy consumption.

"""
from __future__ import print_function, unicode_literals

import argparse
import sys

from termcolor import colored
from toolz.functoolz import compose

from . import config


def build_parser():
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument(
        'recipe', default='default', nargs='?',
        help="Collection of text transformations used to process text",
    )
    parser.add_argument(
        'text_stream', default=sys.stdin, nargs='?',
        type=argparse.FileType('r'),
        help="Text stream that will be transformed using the given recipe.",
    )
    parser.add_argument(
        '-t', '--text',
        help="Text that will be transformed using the given recipe. "
             "When given, this will override processing using `text_stream`. "
             "Unlike `text_stream`, this plays nicely with `pdb`.",
    )
    parser.add_argument(
        '-l', '--list-recipes', action='store_true',
        help="List all available recipes",
    )
    return parser


def print_available_recipes(linecook_config):
    print("Available recipes:")
    for recipe_name in linecook_config.recipes.keys():
        print('- {}'.format(recipe_name))


def recipe_not_found_msg(recipe_name):
    msg = "Recipe not found: {}".format(recipe_name)
    return colored(msg, color='red')


def run(args):
    linecook_config = config.load_config()

    if args.list_recipes:
        print_available_recipes(linecook_config)
        return

    if args.recipe not in linecook_config.recipes:
        print(recipe_not_found_msg(args.recipe))
        print_available_recipes(linecook_config)
        return

    recipe = linecook_config.recipes[args.recipe]
    # Reverse recipe since we want transforms earlier in the list applied
    # first, but `toolz.functoolz.compose` runs it in the opposite direction.
    process_text = compose(*reversed(recipe))

    if args.text:
        print(process_text(args.text))
        return

    try:
        # FIXME: Workaround for Python 2 buffering bug.
        #        See comments of https://stackoverflow.com/a/7608205/260303
        for line in iter(args.text_stream.readline, ''):
            sys.stdout.write(process_text(line))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


def main():
    parser = build_parser()
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
