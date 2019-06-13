#!/usr/bin/env python3
# https://stackoverflow.com/questions/5709616/whats-the-difference-between-these-two-python-shebangs



## usage: adr init [DIRECTORY]
## 
## Initialises the directory of architecture decision records:
## 
##  * creates a subdirectory of the current working directory
##  * creates the first ADR in that subdirectory, recording the decision to
##    record architectural decisions with ADRs.
##
## If the DIRECTORY is not given, the ADRs are stored in the directory `doc/adr`.
import os
# add argument parser
import argparse
import adr_func
import sys

def main(args = None):
    parser = argparse.ArgumentParser(description='Initializes directory with ADRs')
    parser.add_argument('directory',  default='doc/adr/', nargs='?',
                        help='Directory for ADRs. Default: doc/adr')
    # -v is option to set verbose mode
    parser.add_argument('--verbose','-v',help='increase verbosity, display debug messages', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        adr_func.set_adr_verbosity(True)
    config = adr_func.adr_config()
    adr_func.adr_init(config, os.getcwd() ,args.directory)

if __name__ == "__main__":
    main(args)