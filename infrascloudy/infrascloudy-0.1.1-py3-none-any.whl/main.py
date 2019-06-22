#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""
import sys
from docopt import docopt
from kubernetes import config

from infrascloudy import metadata
from infrascloudy.dump import dump
from infrascloudy.render import render
from infrascloudy.templates import find
from infrascloudy.values import resolve


def main(argv):
    """infrascloudy: Kubernetes tools

    Usage:
      infrascloudy apply [-v] [-f <FILE>]... [-s <key=value>]... <TEMPLATES_DIR>
      infrascloudy delete [-v] [-f <FILE>]... [-s <key=value>]... <TEMPLATES_DIR>
      infrascloudy render [-v] [-f <FILE>]... [-s <key=value>]... <TEMPLATES_DIR>
      infrascloudy (-h | --help)
      infrascloudy --version

    Options:
      -h --help                     Show this screen.
      -v --verbose                  Dump debug info to stderr.
      --version                     Show version.
      -s KEY=VALUE --set KEY=VALUE  Set values on the command line (accepts multiple options or separate values with commas: Ex: -s key1=val1,key2=val2).
      -f FILE --file FILE           Specify values in a YAML file (accepts multiple options).

    Notes:
      Resolution of values: --set overrides values in --file by merging. The last value wins.
    """
    arguments = docopt(str(main.__doc__), version=metadata.version)
    config.load_kube_config()

    try:
        templates = find(arguments["<TEMPLATES_DIR>"])
    except ValueError as e:
        print(e)
        exit(1)
        raise

    try:
        context = resolve(arguments["--set"], arguments["--file"])
    except ValueError as e:
        print(e)
        exit(1)
        raise

    rendering = render(context, templates)
    output = dump(rendering)
    if arguments['render']:
        print(output)

    if arguments["apply"]:
        print("Not implemented yet. Use kuku render ... | kubectl apply -f-")
        exit(1)

    if arguments["delete"]:
        print("Not implemented yet. Use kuku render ... | kubectl delete -f-")
        exit(1)

    if arguments["--verbose"]:
        print(output, file=sys.stderr)

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
