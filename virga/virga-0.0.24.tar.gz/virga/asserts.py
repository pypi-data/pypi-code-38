import argparse
import yaml
from yaml.parser import ParserError

from virga.common import VirgaException, get_provider_class


def parser() -> any:
    """
    Argument definition and parsing.

    :return: Arguments
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--provider', choices=['aws', ], required=True, help='provider')
    arg_parser.add_argument('-t', '--testfile', nargs='+', required=True, help='test file')
    arg_parser.add_argument('-d', '--definitions', help='custom definitions path')
    arg_parser.add_argument('-l', '--logfile', help='redirect the output to a log file')
    arg_parser.add_argument('-s', '--silent', help='do not output results', action='store_true', default=False)
    arg_parser.add_argument('-o', '--output', help='save the resource info into the specified directory')
    arg_parser.add_argument('--debug', help='show debug', action='store_true', default=False)
    return arg_parser.parse_args()


def read_testfile(testfile_paths: list) -> dict:
    """
    Read, parse and return the test configuration file.

    :param testfile_paths: Test configuration filename
    :return: Test structure
    """
    try:
        tests = {}
        for testfile_path in testfile_paths:
            with open(testfile_path) as testfile:
                tests.update(yaml.full_load(testfile))
        return tests
    except FileNotFoundError:
        raise VirgaException('Test file not found')
    except ParserError:
        raise VirgaException('Invalid test file')


def asserts():
    """
    The real deal.

    Calls the parser, reads the test file, gets the Provider instantiated, starts the procedure.
    """
    args = parser()
    tests = read_testfile(args.testfile)
    provider = get_provider_class(args)
    provider.set_tests(tests)
    provider.action()
