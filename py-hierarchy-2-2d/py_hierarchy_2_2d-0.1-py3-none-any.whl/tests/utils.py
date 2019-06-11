#!/usr/bin/env python

from tabulate import tabulate
from subprocess import getoutput
from pprint import pprint as pp
from os import path


def my_tabulate(l, no_print=False):
    "This function isn't really important or on the critical path; I just wanted to print dictionaries nicely."
    if isinstance(l, list):
        r = tabulate(l, headers="keys")
    elif isinstance(l, dict):
        r = tabulate([l], headers="keys")
    elif isinstance(l, type(None)):
        r = ""
    else:
        t = type(l)
        raise ValueError("Need a dict or list; got a %s" % t)
    if no_print:
        return r
    else:
        print("")
        print(r)
        print("")
        return None


def my_print_interesting_things(cur, nex):
    print("\n----\nCur is:")
    mt(cur)
    print("----\nNex is:")
    mt(nex)
    print("")


def my_pprint_one_at_a_time(l, print_fn=pp):
    # nl = f'\n{"*" * 80}\n'
    n = "*" * 80
    nl = "\n%s\n" % n
    for x in l:
        print_fn(x)
        input("%sPress Enter to continue...%s" % (nl, nl))
    return None


def get_project_dir():
    """Python makes it difficult to yeld our project root... not sure how this
    will work as a python site package; it probably won't work in serverless as
    git might not be on the path. For testing only?"""
    return path.abspath(getoutput("git rev-parse --show-toplevel"))


def slurp(f):
    with open(f, mode="r") as fi:
        return fi.read()
