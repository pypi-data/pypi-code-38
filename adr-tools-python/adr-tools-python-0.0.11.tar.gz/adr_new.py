#!/usr/bin/env python3
# https://stackoverflow.com/questions/5709616/whats-the-difference-between-these-two-python-shebangs

import os
# add argument parser
import argparse
import adr_func
import sys
# Prerequisite: adr-init has had to have run.

# comment from original Bash version:

# usage: adr new [-s SUPERCEDED] [-l TARGET:LINK:REVERSE-LINK] TITLE_TEXT...
##
# Creates a new, numbered ADR.  The TITLE_TEXT arguments are concatenated to
# form the title of the new ADR.  The ADR is opened for editing in the
# editor specified by the VISUAL or EDITOR environment variable (VISUAL is
# preferred; EDITOR is used if VISUAL is not set).  After editing, the
# file name of the ADR is output to stdout, so the command can be used in
# scripts.
##
# If the ADR directory contains a file `templates/template.md`, this is used as
# the template for the new ADR.  Otherwise a default template is used that
# follows the style described by Michael Nygard in this article:
##
# http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions
##
# Options:
##
# -s SUPERCEDED   A reference (number or partial filename) of a previous
# decision that the new decision supercedes. A Markdown link
# to the superceded ADR is inserted into the Status section.
# The status of the superceded ADR is changed to record that
# it has been superceded by the new ADR.
##
# -l TARGET:LINK:REVERSE-LINK
# Links the new ADR to a previous ADR.
# TARGET is a reference (number or partial filename) of a
# previous decision.
# LINK is the description of the link created in the new ADR.
# REVERSE-LINK is the description of the link created in the
# existing ADR that will refer to the new ADR.
##
# Multiple -s and -l options can be given, so that the new ADR can supercede
# or link to multiple existing ADRs.
##
# E.g. to create a new ADR with the title "Use MySQL Database":
##
# adr new Use MySQL Database
##
# E.g. to create a new ADR that supercedes ADR 12:
##
# adr new -s 12 Use PostgreSQL Database
##
# E.g. to create a new ADR that supercedes ADRs 3 and 4, and amends ADR 5:
##
# adr new -s 3 -s 4 -l "5:Amends:Amended by" Use Riak CRDTs to cope with scale
##


if __name__ == "__main__":
    main(args)


def main(args=None):

    parser = argparse.ArgumentParser(description='Creates a new, numbered ADR. The TITLE_TEXT arguments are concatenated to form the title of the new ADR')

    parser.add_argument('title_adr', metavar='title of ADR',  nargs='+', help='Title of the ADR')

    # -s is option with 1 argument (nargs = 1)
    parser.add_argument('-s', dest='superseded', nargs=1, action='append', help='A reference (number or partial filename) of a previous decision that the new decision supercedes')

    # -l is option with 1 argument
    parser.add_argument('-l', dest='linkadr', nargs=1,  help='TARGET:LINK:REVERSE-LINK, Links the new ADR to a previous ADR.  TARGET is a reference (number or partial filename) of a previous decision. LINK is the description of the link created in the new ADR. REVERSE-LINK is the description of the link created in the existing ADR that will refer to the new ADR.')

    # -v is option to set verbose mode
    parser.add_argument( '--verbose', '-v', help='increase verbosity, display debug messages', action='store_true')


    args = parser.parse_args()
    if args.verbose:
        adr_func.set_adr_verbosity(True)
    config = adr_func.adr_config()
    new_adr = adr_func.adr_new(config, os.getcwd(),  args.title_adr, args.superseded, args.linkadr)
