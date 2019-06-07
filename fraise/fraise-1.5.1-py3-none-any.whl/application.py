import argparse

from . import phrases


def get_args():
    parser = argparse.ArgumentParser(description="Generate memorable passphrases")
    parser.add_argument('--max-word-length',
                        default=8,
                        dest='max_word_length',
                        help="The maximum length of each word (default 8)",
                        type=int)
    parser.add_argument('--minimum-length',
                        default=16,
                        dest='minimum_length',
                        help="Minimum length of the phrase (default 16)",
                        type=int)
    parser.add_argument('--separator',
                        default=' ',
                        dest='separator',
                        help="What to put inbetween the words (default space)"
                        )
    parser.add_argument('--word-count',
                        default=4,
                        dest='word_count',
                        help="How many words to include in the phrase (default 4)",
                        type=int)
    parser.add_argument('--capitalized',
                        default=True,
                        dest='capitalized',
                        help="Capitalize the first letter of each word in the phrase",
                        action='store_true')
    return parser.parse_args()


def run():
    args = get_args()
    print(phrases.generate(
        max_word_length=args.max_word_length,
        minimum_length=args.minimum_length,
        separator=args.separator,
        word_count=args.word_count,
        capitalized=args.capitalized
    ))
