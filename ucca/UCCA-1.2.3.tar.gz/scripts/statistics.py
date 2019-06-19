#!/usr/bin/env python3

import argparse
from collections import Counter

import pandas as pd

from ucca import layer0, layer1
from ucca.ioutil import get_passages_with_progress_bar

desc = """Prints statistics on UCCA passages"""


def main(args):
    df = pd.DataFrame(index=args.directories, columns=["sentences", "tokens", "nodes", "discontinuous", "reentrant",
                                                       "implicit", "edges", "primary", "remote"])
    df.fillna(0, inplace=True)
    for i, directory in enumerate(args.directories):
        row = df.loc[directory]
        for passage in get_passages_with_progress_bar(directory, desc=directory):
            l1 = passage.layer(layer1.LAYER_ID)
            non_terminals = [n for n in l1.all if n not in l1.heads and len(n.get_terminals()) > 1]
            edges = {e for n in non_terminals for e in n}
            remote_counter = Counter(e.attrib.get("remote", False) for e in edges)
            row["sentences"] += 1
            row["tokens"] += len(passage.layer(layer0.LAYER_ID).all)
            row["nodes"] += len(non_terminals)
            row["discontinuous"] += sum(1 for n in non_terminals if n.discontiguous)
            row["reentrant"] += sum(1 for n in non_terminals if any(e.attrib.get("remote") for e in n.incoming))
            row["edges"] += len(edges)
            row["primary"] += remote_counter[False]
            row["remote"] += remote_counter[True]
            row["implicit"] += sum(1 for n in l1.all if n.attrib.get("implicit"))

    # Change to percentages
    df["discontinuous"] *= 100. / df["nodes"]
    df["reentrant"] *= 100. / df["nodes"]
    df["implicit"] *= 100. / df["nodes"]
    df["primary"] *= 100. / df["edges"]
    df["remote"] *= 100. / df["edges"]

    # Print
    if args.outfile:
        df.T.to_csv(args.outfile, float_format="%.2f", sep="&", line_terminator=" \\\\\n")
        print("Saved to " + args.outfile)
    else:
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print(df.T)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=desc)
    argparser.add_argument("directories", nargs="+", help="directories to process")
    argparser.add_argument("-o", "--outfile", help="output file for statistics")
    main(argparser.parse_args())
