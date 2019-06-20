"""
Script for plotting loss and accuracy from chainer logs

usage:
	> python -m chainer_addon.utils.plot <logfile> [-k <key1> <key2> ... <keyn> ]
"""

import sys, argparse

parser = argparse.ArgumentParser(description = "Plot loss and accuracy from chainer logs")
parser.add_argument("logfile", type=str, help="chainer log file to parse")
parser.add_argument("--key","-k", type=str, default=["main/accuracy", "main/loss"], nargs="+", help="key of the loss and accuracy values")
parser.add_argument("--val_key", default="validation", type=str, help="key of the validation runs")
parser.add_argument("--fit", action="store_true", help="plot fitted graphs")
parser.add_argument("--track_changes", action="store_true", help="track changes in the log file and update the graphs accordingly")
parser.add_argument("--clip", type=int, default=0, help="clip values above to the given value (do not clip if 0)")
parser.add_argument("--all_in_one", "-aio", action="store_true", help="plot all graphs in one")

from os.path import join, basename, dirname
from scipy.optimize import curve_fit
import simplejson as json, numpy as np
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from contextlib import contextmanager
from collections import defaultdict
import time

def func(x, a, b, c):
	return a * np.exp(-b * x) + c

def non_zero(idxs, values):
	return list(zip(*[(idx, val) for idx, val in zip(idxs, values) if val != 0]))



def update_graphs(args, data, validation_data, graphs):
	fig, ax = plt.figure(0), None
	fig.canvas.set_window_title(args.logfile)
	num_figs = len(data)
	if args.all_in_one:
		rows = cols = 1
	else:
		rows = np.ceil(np.sqrt(num_figs))
		cols = np.ceil(num_figs / rows)

	def extract_data(data):
		X, Y = map(np.array, zip(*data))
		if args.clip > 0:
			Y = np.minimum(Y, args.clip)
		return X, Y

	def set_line_data(line, X, Y, label):
		if (Y == 0).all(): return
		line.set_xdata(X)
		line.set_ydata(Y)
		line.set_label(label)

	for i, (key, values) in enumerate(data.items(), 1):
		if ax is None or not args.all_in_one:
			ax = fig.add_subplot(rows, cols, i)
			ax.set_title(key if not args.all_in_one else "graphs")

		assert None not in [fig, ax]

		X, Y = extract_data(values)
		if key in graphs:
			line = graphs[key]["line"]
			set_line_data(line, X, Y, key)

			if validation_data[key]:
				X, Y = extract_data(validation_data[key])
				line = graphs[key]["val_line"]
				set_line_data(line, X, Y, key + " val")

			ax = graphs[key]["axes"]
			ax.relim()
			ax.autoscale_view()
		else:
			graphs[key]["fignum"] = i
			graphs[key]["figure"] = fig
			graphs[key]["axes"] = ax
			if (Y != 0).any():
				graphs[key]["line"] = ax.plot(X, Y, label=key)[0]

			if args.fit:
				coefs = curve_fit(func, X, Y)[0]
				ax.plot(X, [func(x, *coefs) for x in X], "r--")

			if validation_data[key]:
				X, Y = extract_data(validation_data[key])
				graphs[key]["val_line"] = ax.plot(X, Y, label=key + " val")[0]

		ax.legend()
		ax.grid(True)


def read_logs(args, log_file):
	data = {key: [] for key in args.key}
	validation_data = {key: [] for key in args.key}
	for log in log_file:
		for key in args.key:
			data[key].append([int(log.get("epoch")), log.get(key, 0)])
			if key.startswith(args.val_key): continue
			val_key = "{}/{}".format(args.val_key, key)
			if val_key in log:
				validation_data[key].append([int(log.get("epoch")), log.get(val_key, 0)])

	return data, validation_data



@contextmanager
def track_change(args, callback):
	if not args.track_changes: yield; return
	path, fname = dirname(args.logfile), basename(args.logfile)

	class event_handler(FileSystemEventHandler):
		current_file = None
		def on_modified(self, event):
			if not isinstance(event, FileModifiedEvent): return
			if self.current_file == event.src_path: return
			if fname in event.src_path:
				print("Updating Graphs")
				callback()
				self.current_file = event.src_path

	obs = Observer()
	obs.schedule(event_handler(), path, recursive=False)
	obs.start()

	try:
		yield obs
	finally:
		obs.stop()
	obs.join(10)
	print()

def main(args):
	graphs = defaultdict(dict)
	def draw():
		log_file = json.load(open(args.logfile))#[:200]
		data, val_data = read_logs(args, log_file)
		update_graphs(args, data, val_data, graphs=graphs)
		plt.draw()

	with track_change(args, draw) as obs:
		if not args.track_changes:
			log_file = json.load(open(args.logfile))#[:200]
			data, val_data = read_logs(args, log_file)
			update_graphs(args, data, val_data, graphs=graphs)
			plt.show()
			return
		else:
			plt.ion()
			draw()

		try:
			while True:
				plt.pause(0.05)
				if not obs.is_alive(): break
		except KeyboardInterrupt:
			pass


main(parser.parse_args())


