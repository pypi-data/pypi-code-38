from __future__ import absolute_import, division, print_function

import argparse
import sys

import dials_data
import dials_data.datasets
import dials_data.download
import yaml


def cli_get(cmd_args):
    parser = argparse.ArgumentParser(
        description="Download datasets", prog="dials.data get"
    )
    parser.add_argument("dataset", nargs="*")
    parser.add_argument(
        "--create-hashinfo",
        action="store_true",
        help="generate file integrity information for specified datasets in the current directory",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="machine readable output"
    )
    parser.add_argument(
        "--verify", action="store_true", help="verify integrity of downloaded dataset"
    )
    args = parser.parse_args(cmd_args)
    if args.verify and args.create_hashinfo:
        sys.exit("Parameter --create-hashinfo can not be used with --verify")
    if not args.dataset:
        parser.print_help()
        sys.exit(0)

    unknown_data = set(args.dataset) - set(dials_data.datasets.definition)
    if unknown_data:
        sys.exit("Unknown dataset: {}".format(", ".join(unknown_data)))

    repository = dials_data.datasets.repository_location()
    if not args.quiet:
        print("Repository location: {repo.strpath}\n".format(repo=repository))

    for ds in args.dataset:
        if not args.quiet:
            print("Downloading dataset {}".format(ds))
        hashinfo = dials_data.download.fetch_dataset(
            ds, ignore_hashinfo=args.create_hashinfo, verify=args.verify
        )
        if args.create_hashinfo:
            if not args.quiet:
                print("Writing file integrity information to {}.yml".format(ds))
            with open("{}.yml".format(ds), "w") as fh:
                yaml.dump(hashinfo, fh, default_flow_style=False)
        if args.quiet:
            print(repository.join(ds).strpath)
        else:
            print("Dataset {} stored in {}".format(ds, repository.join(ds).strpath))


def cli_list(cmd_args):
    parser = argparse.ArgumentParser(
        description="Show dataset information", prog="dials.data list"
    )
    parser.add_argument(
        "--missing-hashinfo",
        action="store_true",
        help="only list datasets without file integrity information",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="machine readable output"
    )
    args = parser.parse_args(cmd_args)
    if args.missing_hashinfo:
        ds_list = dials_data.datasets.fileinfo_dirty
    else:
        ds_list = dials_data.datasets.definition
    dials_data.datasets.list_known_definitions(ds_list, quiet=args.quiet)


def main():
    if dials_data.__commit__:
        version = dials_data.__version__ + "-g" + dials_data.__commit__[:7]
    else:
        version = dials_data.__version__ + "-dev"
    parser = argparse.ArgumentParser(
        usage="dials.data <command> [<args>]",
        description="""DIALS regression data manager v{version}

The most commonly used commands are:
   list     List available datasets
   get      Download datasets
""".format(
            version=version
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("subcommand", help=argparse.SUPPRESS)
    # parse_args defaults to [1:] for args, but need to
    # exclude the rest of the args too, or validation will fail
    parameters = sys.argv[1:2]
    if not parameters:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args(parameters)
    subcommand = globals().get("cli_" + args.subcommand)
    if subcommand:
        return subcommand(sys.argv[2:])
    parser.print_help()
    print()
    sys.exit("Unrecognized command: {}".format(args.subcommand))
