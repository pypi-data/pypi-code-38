#!/usr/bin/env python

import argparse
import os
import sys


from pyberdrola.pyberdrola import PyBerdrola
from pyberdrola.utils import JSONUtils
from pyberdrola import __version__


def get_auth_info():
    """
    Request for user and password variables to be able to login
    """
    try:
        user = os.environ["IBUSER"]
        password = os.environ["IBPASS"]
    except KeyError:
        print("You must to configure `IBUSER` and `IBPASS` to continue")
        sys.exit(-1)
    return (user, password)


def parser():
    parser = argparse.ArgumentParser(argument_default=argparse.HelpFormatter)

    parser.add_argument("command", help="Command to run",
                        choices=["last", "all"])
    parser.add_argument("--version", action="version", version=__version__)

    return parser


def main():
    auth = get_auth_info()

    args = parser().parse_args()

    pyb = PyBerdrola(*auth)
    pyb.login()
    pyb.data()

    if args.command == "last":
        JSONUtils.pprint(pyb.last_invoice())
    elif args.command == "all":
        for invoce in pyb.all_invoices()["facturas"]:
            print("{}\t{}\t{}".format(
                invoce["fecha"], invoce["consumo"], invoce["importe"]))


if __name__ == "__main__":
    main()
