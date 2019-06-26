import argparse

from cbot_client.new_recipe import new_recipe


def run(*args):
    parser = argparse.ArgumentParser(description="", prog="cbot")
    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')
    subparsers.required = True

    add_parser = subparsers.add_parser('new', help='Add a new package version')
    add_parser.add_argument("index_path", help='Path to a clone of the cbot index repo')
    add_parser.add_argument("-n", "--name", help='Name of the package')
    add_parser.add_argument("-v", "--version", help='Version of the package')
    add_parser.add_argument("-f", "--folder", help='Folder where the recipe will be')
    add_parser.add_argument("-s", "--url", help='URL to a zip with the sources')

    args = parser.parse_args(*args)
    return new_recipe(args.index_path, args.name, args.version, args.folder, args.url)

