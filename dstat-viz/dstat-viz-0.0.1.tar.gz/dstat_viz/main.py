import argparse
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd


def main():
    parser = argparse.ArgumentParser('dstat visualizer')
    parser.add_argument('--csv', type=str, default=None,
                        help='Input CSV file')
    parser.add_argument('--out', type=str, default=None,
                        help='Output file name')
    parser.add_argument('cmd', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.csv and args.cmd:
        print('--csv and command execution cannot passed with.')
        parser.print_usage()
        sys.exit(1)

    outfile = args.out
    if outfile is None:
        pid = os.getpid()
        outfile = 'dstat-{}.png'.format(pid)

    if args.csv:
        df = pd.read_csv(args.csv, skiprows=5, header=1, parse_dates=True)
    else:
        # TODO: spawn a child process from args.cmd along with
        # ``dstat`` command and record the resource usage, to plot.
        df = None

    assert df is not None
    df.drop([7373,7374,7375,7376],inplace=True)
    df.drop([7405,7406,7407,7408],inplace=True)
    #df.dropna(inplace=True)
    #print(df.used)
    df['used'] = pd.to_numeric(df['used'])
    #df.set_index('time', inplace=True)
    print(df.dtypes)

    # plot the dataframe
    assert 'used' in df.columns
    plt.title('Memory usage')
    plt.ylabel('bytes')
    plt.xlabel('tick')
    plt.plot(df.used)
    plt.savefig(outfile)

    print('Graphs saved to', outfile, 'possibly')
