#!/usr/bin/env python3
# https://stackoverflow.com/questions/5709616/whats-the-difference-between-these-two-python-shebangs

# add argument parser
import os
import argparse
import adr_func
import sys

## usage: adr init [DIRECTORY]
## 
## Initialises the directory of architecture decision records:
## 
##  * creates a subdirectory of the current working directory
##  * creates the first ADR in that subdirectory, recording the decision to
##    record architectural decisions with ADRs.
##
## If the DIRECTORY is not given, the ADRs are stored in the directory `doc/adr`.

def main(args=None):
    parser = argparse.ArgumentParser(description='Initializes directory with ADRs')
    # -v is option to set verbose mode
    parser.add_argument('--verbose','-v',help='increase verbosity, display debug messages', action='store_true')

    parser.add_argument('directory',  default='doc/adr/', nargs='?',
                        help='Directory for ADRs. Default: doc/adr')

    args = parser.parse_args()

    if args.verbose:
        #print('debug')
        adr_func.set_adr_verbosity(True)
    config = adr_func.adr_config()
    for adr in adr_func.adr_list(os.getcwd()):
        print(adr)

if __name__ == "__main__":
    main(args)