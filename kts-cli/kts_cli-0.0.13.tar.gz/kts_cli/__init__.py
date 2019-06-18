import argparse
import sys
sys.path.insert(0, '.')


from .file_system import build_file_system, create_config
from .examples import download_example, VALID_EXAMPLES


def run():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand",
                                       title='subcommands',
                                       description='valid subcommands')
    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(func=build_file_system)
    example_parser = subparsers.add_parser('example')
    example_parser.add_argument('name', type=str, help=f'Name of example, one of {VALID_EXAMPLES}')
    example_parser.set_defaults(func=download_example)
    args = parser.parse_args(sys.argv[1:])
    args.func(args)
    # if args.subcommand == 'init':
    #     build_file_system()
    # elif args.subcommand == 'example':
    #
    # else:
    #     parser.print_help()
