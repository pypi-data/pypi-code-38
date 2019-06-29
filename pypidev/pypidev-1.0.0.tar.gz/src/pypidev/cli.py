import argparse
from .core import Hello

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', help='target name.', required=True)
    return parser.parse_args()


def main():
    args = read_args()
    hello = Hello(args.n)
    print(hello.get())
