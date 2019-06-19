#!/usr/bin/env python3
import sys

import argparse

from uccaapp.api import ServerAccessor

desc = """Download categories from one UCCA-App server and upload to another UCCA-App server"""


def add_arguments(argparser):
    argparser.add_argument("category-ids", nargs="+", type=int, help="IDs of tasks to export and import")
    argparser.add_argument("--server-address-orig", required=True, help="UCCA-App origin server")
    argparser.add_argument("--email-orig", help="UCCA-App origin email")
    argparser.add_argument("--password-orig", help="UCCA-App origin password")
    argparser.add_argument("--server-address-target", required=True, help="UCCA-App target server")
    argparser.add_argument("--email-target", help="UCCA-App target email")
    argparser.add_argument("--password-target", help="UCCA-App target password")
    argparser.add_argument("-v", "--verbose", action="store_true", help="detailed output")


def main(args):
    server_accessor_origin = ServerAccessor(server_address=args.server_address_orig,
                                            email=args.email_orig, password=args.password_orig,
                                            verbose=args.verbose)
    server_accessor_target = ServerAccessor(server_address=args.server_address_target,
                                            email=args.email_target, password=args.password_target,
                                            verbose=args.verbose)
    for category_id in args.category_ids:
        category_out = server_accessor_origin.get_category(category_id)
        server_accessor_target.create_category(**category_out)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    add_arguments(argument_parser)
    main(argument_parser.parse_args())
    sys.exit(0)
