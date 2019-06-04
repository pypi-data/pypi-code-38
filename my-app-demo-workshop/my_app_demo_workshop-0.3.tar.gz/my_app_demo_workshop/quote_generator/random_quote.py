from os.path import join
from random import choice
import json
from ..config import ROOT_PATH

QUOTES_PATH = join(ROOT_PATH, 'quote_generator', 'quotes.json')
with open(QUOTES_PATH, 'r') as fp:
    QUOTES = [f"{e['quote']} ({e['author']})" for e in json.load(fp)['quotes']]


def get_random_quote():
    """Return a random  quote"""

    return choice(QUOTES)


if __name__ == '__main__':
    print(get_random_quote())
