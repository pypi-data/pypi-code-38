#!/usr/bin/env python

"""Console script for refchooser."""

from __future__ import print_function
from __future__ import absolute_import

import argparse
import logging
import sys

from refchooser import refchooser
from refchooser.__init__ import __version__

# Ignore flake8 errors in this module
# flake8: noqa


def parse_arguments(system_args):
    """Parse command line arguments.

    Parameters
    ----------
    system_args : list
        List of command line arguments, usually sys.argv[1:].

    Returns
    -------
    Namespace
        Command line arguments are stored as attributes of a Namespace.
    """
    def non_negative_int(value):
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("Must be a number >= 0")
        if ivalue < 0:
            raise argparse.ArgumentTypeError("Must be >= 0")
        return ivalue

    def positive_int(value):
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("Must be a number greater than 0")
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("Must be greater than 0")
        return ivalue

    description = """Tools to help choosing a reference assembly."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--version", action="version", version="%(prog)s version " + __version__)
    subparsers = parser.add_subparsers(dest="subparser_name", help=None, metavar="subcommand")
    subparsers.required = True

    formatter_class = argparse.ArgumentDefaultsHelpFormatter

    help_str = "Create mash sketches for all the assemblies in a directory."
    description = help_str + " This is a necessary setp before selecting the minimum mash distance assembly."
    subparser = subparsers.add_parser("sketch", formatter_class=formatter_class, description=description, help=help_str)
    subparser.add_argument(             dest="assemblies",    type=str,              metavar="ASSEMBLIES",             help="Directory containing assemblies, or a file containing paths to assemblies.")
    subparser.add_argument(             dest="sketch_dir",    type=str,              metavar="SKETCH-DIR",             help="Directory where sketches will be stored.")
    subparser.add_argument("--size",    dest="sketch_size",   type=positive_int,     metavar="INT",     default=10000, help="Sketch size. Each sketch will have at most this many non-redundant min-hashes.")
    subparser.add_argument("--threads", dest="threads",       type=positive_int,     metavar="INT",         default=1, help="Number of CPU threads to use.")
    subparser.set_defaults(func=sketch_command)

    help_str = "Choose an assembly from a collection with minimum mash distance to all others."
    description = help_str + " You must create sketches of the assemblies before running this command."
    subparser = subparsers.add_parser("distance", formatter_class=formatter_class, description=description, help=help_str)
    subparser.add_argument(             dest="sketches",      type=str,              metavar="SKETCHES",               help="Directory containing sketches, or a file containing paths to sketches.")
    subparser.add_argument("--top",     dest="top_n",         type=positive_int,     metavar="TOP-N",      default=10, help="Print the best n candidate references.")
    subparser.add_argument("--threads", dest="threads",       type=positive_int,     metavar="INT",         default=1, help="Number of CPU threads to use.")
    subparser.set_defaults(func=distance_command)

    help_str = "Print a matrix of mash distances between all pairs of assemblies and write to a file."
    description = help_str + " You must create sketches of the assemblies before running this command."
    subparser = subparsers.add_parser("matrix", formatter_class=formatter_class, description=description, help=help_str)
    subparser.add_argument(             dest="sketches",      type=str,              metavar="SKETCHES",               help="Directory containing sketches, or a file containing paths to sketches.")
    subparser.add_argument(             dest="output_path",   type=str,              metavar="OUTPUT",                 help="Path to tab-separated output file.")
    subparser.add_argument("--threads", dest="threads",       type=positive_int,     metavar="INT",         default=1, help="Number of CPU threads to use.")
    subparser.set_defaults(func=matrix_command)

    help_str = "Choose an assembly from a collection with minimum number of contigs."
    description = help_str
    subparser = subparsers.add_parser("contigs", formatter_class=formatter_class, description=description, help=help_str)
    subparser.add_argument(           dest="assemblies",    type=str,              metavar="ASSEMBLIES",             help="Directory containing assemblies, or a file containing paths to assemblies.")
    subparser.add_argument("--top",   dest="top_n",         type=positive_int,     metavar="TOP-N",      default=10, help="Print the best n candidate references.")
    subparser.set_defaults(func=contigs_command)

    args = parser.parse_args(system_args)
    return args


def sketch_command(args):
    """Create mash sketches for all the assemblies in a directory."

    Parameters
    ----------
    args : Namespace
        Command line arguments stored as attributes of a Namespace, usually
        parsed from sys.argv
    """
    refchooser.sketch(args.assemblies, args.sketch_dir, args.sketch_size, args.threads)


def distance_command(args):
    """Choose an assembly from a list with minimum distance to all others.

    Parameters
    ----------
    args : Namespace
        Command line arguments stored as attributes of a Namespace, usually
        parsed from sys.argv
    """
    refchooser.choose_by_distance(args.sketches, args.top_n, args.threads)


def matrix_command(args):
    """Print a matrix of mash distances between all pairs of assemblies and write to a file.

    Parameters
    ----------
    args : Namespace
        Command line arguments stored as attributes of a Namespace, usually
        parsed from sys.argv
    """
    refchooser.distance_matrix(args.sketches, args.output_path, args.threads)


def contigs_command(args):
    """Choose an assembly from a collection with minimum number of contigs.

    Parameters
    ----------
    args : Namespace
        Command line arguments stored as attributes of a Namespace, usually
        parsed from sys.argv
    """
    refchooser.choose_by_contigs(args.assemblies, args.top_n)


def run_command_from_args(args):
    """Run a subcommand with previously parsed arguments in an argparse namespace.

    This function is intended to be used for unit testing.

    Parameters
    ----------
    args : Namespace
        Command line arguments are stored as attributes of a Namespace.
        The args are obtained by calling parse_argument_list().

    Returns
    -------
    Returns 0 on success if it completes with no exceptions.
    """
    return args.func(args)  # this executes the function previously associated with the subparser with set_defaults


def run_from_line(line):
    """Run a command with a command line.

    This function is intended to be used for unit testing.

    Parameters
    ----------
    line : str
        Command line.

    Returns
    -------
    Returns 0 on success if it completes with no exceptions.
    """
    argv = line.split()
    args = parse_arguments(argv)
    return args.func(args)  # this executes the function previously associated with the subparser with set_defaults


def main():
    """This is the main function which is turned into an executable
    console script by the setuptools entry_points.  See setup.py.

    To run this function as a script, first install the package:
        $ python setup.py develop
        or
        $ pip install --user refchooser

    Parameters
    ----------
    This function must not take any parameters

    Returns
    -------
    The return value is passed to sys.exit().
    """
    enable_log_timestamps = False
    if enable_log_timestamps:
        logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
    args = parse_arguments(sys.argv[1:])
    return args.func(args)  # this executes the function previously associated with the subparser with set_defaults


# This snippet lets you run the cli without installing the entrypoint.
if __name__ == "__main__":
    sys.exit(main())
