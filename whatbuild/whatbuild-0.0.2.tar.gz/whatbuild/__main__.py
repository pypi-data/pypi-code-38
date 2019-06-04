from __future__ import print_function
import os
import sys
import json
import argparse
from .info import getinfo


parser = argparse.ArgumentParser()
parser.description = "Print basic system and git information out for the " \
                     "current directory"
parser.add_argument("--package", dest="package", type=str, default=None,
                    help="Specify a package name")
parser.add_argument("-o", dest="output", type=str, default=None,
                    help="Write the output to this file instead of STDOUT"
                    )


def info_v1(folder, package=None):
    info = getinfo(folder, package=package)
    return {
        "v1": info,
    }


def run(argv):
    opts = parser.parse_args(argv)
    data = json.dumps(
        info_v1(os.getcwd(), package=opts.package),
        indent=2)
    if opts.output:
        with open(opts.output, "w") as outfile:
            outfile.write(str(data))
    else:
        print(data)


if __name__ == "__main__":
    run(sys.argv[1:])
