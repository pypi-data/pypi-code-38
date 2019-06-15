#!/bin/python 

import ete3

import optparse


def Execute(options):
    print("Drawing Tree for %s" % options.InputFile)
    t = ete3.Tree(options.InputFile)
    ts = ete3.TreeStyle()
    ts.show_branch_length = True
    t.render(options.OutputFile, h=500, tree_style=ts)


if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option('-i', dest="InputFile")
    parser.add_option('-o', dest="OutputFile")

    options, args = parser.parse_args()

    if not options.InputFile:
        print("No file specified.")
        exit(1)

    Execute(options)
