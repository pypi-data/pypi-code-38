import argparse

import sys

from virga.common import get_provider_class, VirgaException


def parser() -> any:
    """
    Argument definition and parsing.

    :return: Arguments
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--provider', required=True, help='provider')
    arg_parser.add_argument('-s', '--section', required=True, help='type of resource to exemplify')
    arg_parser.add_argument('-r', '--resource', required=True, help='resource id')
    arg_parser.add_argument('-d', '--definitions', help='definitions path')
    return arg_parser.parse_args()


def samples():
    """
    The other real deal.

    Calls the parser, gets the Provider instantiated, starts the procedure.
    """
    try:
        args = parser()
        provider = get_provider_class(args)
        return provider.sample(args.section, args.resource)
    except VirgaException as ex:
        sys.stderr.write(str(ex))
        sys.exit(1)
