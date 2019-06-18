""" Helper script to plot the progress of an MCMC run """
import argparse
import os

import pandas as pd

import bilby

parser = argparse.ArgumentParser("Bilby plot chain")
parser.add_argument('-c', '--chain-file', help='The chain.dat file to use')
parser.add_argument('-f', '--filename', default=None, help='The filename to save the plot to')
args = parser.parse_args()

df = pd.read_csv(args.chain_file, delim_whitespace=True)

keys = df.keys()[1:-2]
array = df.values[:, 1:-2]
nwalkers = df.walker.max() + 1
ndim = array.shape[1]
nsteps = array.shape[0] // nwalkers
array = array.reshape(nsteps, nwalkers, ndim)

if args.filename is None:
    filename = os.path.join(os.path.dirname(args.chain_file),
                            'chain_{}.png'.format(nsteps))
else:
    filename = args.filename

res = bilby.core.result.Result()
res.parameter_labels = keys
res.posterior = df
res.nburn = 0
res.walkers = array
bilby.core.utils.logger.info("Walker plot saved to {}".format(filename))
res.plot_walkers(filename=filename)
