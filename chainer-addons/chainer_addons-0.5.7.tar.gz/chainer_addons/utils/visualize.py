#!/usr/bin/env python
if __name__ != '__main__': raise Exception("Do not import me!")

"""
Script for plotting loss and accuracy from chainer logs

usage:
	> python -m chainer_addon.utils.plot <logfile> [-k <key1> <key2> ... <keyn> ]
"""

import sys, argparse

parser = argparse.ArgumentParser(description = "Plot histograms of all parameters in given data")
parser.add_argument("data", nargs="+", type=str, help="data to visualize")
parser.add_argument("--pattern", type=str, help="pattern to sort out parameter names")
parser.add_argument("--n_bins", type=int, default=10, help="number of bins for the histograms")

from os.path import join, basename
from scipy.optimize import curve_fit
import simplejson as json, numpy as np, re
import matplotlib.pyplot as plt

def func(x, a, b, c):
	return a * np.exp(-b * x) + c

def non_zero(idxs, values):
	return list(zip(*[(idx, val) for idx, val in zip(idxs, values) if val != 0]))

def main(args):
	models = list(map(np.load, args.data))
	pattern_regex = None

	if args.pattern:
		pattern_regex = re.compile(args.pattern)

	# gather matching keys
	keys = []
	for key in models[0].keys():
		if pattern_regex is not None and not re.findall(pattern_regex, key): continue
		keys.append(key)

	if not keys:
		print("No parameters were selected!", file=sys.stderr)
		exit()

	keys.sort()

	cols = int(np.ceil(np.sqrt(len(keys))))
	rows = int(np.ceil(len(keys) / cols))
	fig = plt.figure()

	print("Plotting \n\t{}".format(", ".join(keys)))
	for i, key in enumerate(keys, 1):
		ax = fig.add_subplot(rows, cols, i)
		ax.set_title(key)
		ax.grid()

		for name, model in zip(args.data, models):
			param = model[key]
			histo, X = np.histogram(param, density=True, bins=args.n_bins)
			x = [(x2 + x1) / 2 for x1, x2 in zip(X[:-1], X[1:])]
			ax.plot(x, histo, label=name)
		ax.legend()

	plt.show()

main(parser.parse_args())


