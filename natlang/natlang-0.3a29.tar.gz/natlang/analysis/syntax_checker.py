# run with python2 and python3 separately, to check whether the data is valid
# python2/3 syntax
from __future__ import absolute_import
from __future__ import print_function
import ast
import argparse


def check_syntax(code):
    try:
        ast.parse(code)
    except SyntaxError:
        valid = False
    else:
        valid = True
    return valid


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check syntax of python code')
    parser.add_argument('file')
    args = parser.parse_args()

    results = []
    with open(args.file) as f:
        for line in f:
            code = eval(line)
            valid = check_syntax(code)
            results.append(valid)

    print(repr(results))
