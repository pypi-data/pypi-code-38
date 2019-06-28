#!/usr/bin/env python3

import argparse
import locale

from .translate import Translator

default_locale = locale.getdefaultlocale()[0]
to_lang = default_locale.split('.')[0].lower().replace('_', '-')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--lang',
        nargs='?',
        default=to_lang,
        help='to lang'
    )
    parser.add_argument(
        '--text',
        help='text'
    )
    args = parser.parse_args()

    translator = Translator(to_lang=args.lang)
    translated = translator.translate(args.text)
    print(translated)
