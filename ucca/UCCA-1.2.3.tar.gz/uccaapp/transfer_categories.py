#!/usr/bin/env python3
import argparse
from ucca.convert import from_json
from uccaapp.api import ServerAccessor

desc = """Download task from UCCA-App and convert to a passage in standard format"""



def add_arguments(argparser):
    argparser.add_argument("category_ids", nargs="+", type=int, help="IDs of tasks to export and import")
    argparser.add_argument("--server-address-orig", help="UCCA-App origin server")
    argparser.add_argument("--email-orig", help="UCCA-App origin email")
    argparser.add_argument("--password-orig", help="UCCA-App origin password")
    argparser.add_argument("--server-address-target", help="UCCA-App target server")
    argparser.add_argument("--email-target", help="UCCA-App target email")
    argparser.add_argument("--password-target", help="UCCA-App target password")


def main(args):
    server_accessor_origin = ServerAccessor(server_address=args.server_address_orig,
                                            email=args.email_orig, password=args.password_orig,auth_token=None,verbose=True)
    server_accessor_target = ServerAccessor(server_address=args.server_address_target,
                                            email=args.email_target, password=args.password_target,auth_token=None,verbose=True)
    for category_id in args.category_ids:
        #try:
        category_out = server_accessor_origin.get_category(category_id)
        server_accessor_target.create_category(**category_out)
        #except:
        #    sys.stderr.write('failed writing category with ID='+str(category_id))
        #    continue





if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    add_arguments(argument_parser)
    main(argument_parser.parse_args())
