""" Quick and dirty wrapper for argparse, with the intent to be less verbose

Meant to be used like this::

    import argp
    s1 = argp.sub("check", do_check)
    s2 = argp.sub("sign", do_sign, help="Sign the delivery")

    s2.arg("signature", metavar="SIGNATURE")

    argp.parse()
"""

import argparse, sys

# yes, 'p' will contain the parser

p = None
subparsers = None

def init(parser = None):
    """ module needs to be initialized by 'init'.

    Can be called with parser to use a pre-built parser, otherwise
    a simple default parser is created
    """

    global p,subparsers
    if parser is None:
        p = argparse.ArgumentParser()
    else:
        p = parser

    arg = p.add_argument

    subparsers = p.add_subparsers()

def parse_list(l):
    parsed = p.parse_args(l)
    if "func" in parsed:
        parsed.func(parsed)
    else:
        p.print_usage()
    return parsed


def parse():
    """ Call this after declaring your arguments
    """
    return parse_list(sys.argv[1:])


def sub(name, func,**kwarg):
    """ Add subparser

    """
    sp = subparsers.add_parser(name, **kwarg)
    sp.set_defaults(func=func)
    sp.arg = sp.add_argument
    return sp
