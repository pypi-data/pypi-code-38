import sys
from auto_extract.extract_item import test_url


def main():
    from pprint import pprint
    pprint(test_url(sys.argv[1]))
