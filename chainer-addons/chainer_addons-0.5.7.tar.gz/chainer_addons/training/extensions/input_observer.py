import numpy as np, chainer
import os, re
from os.path import isdir, join
from chainer.training import extension
from collections import defaultdict
from chainer import training

class InputObserver(extension.Extension):
	def __init__(self, output, match_regex=None, gather_trigger=(1, "iteration"), write_out_trigger=(1, "epoch")):
		super(InputObserver, self).__init__()
		self.output = output
		self.match_regex = match_regex
		self.gather_trigger = training.trigger.get_trigger(gather_trigger)
		self.write_out_trigger = training.trigger.get_trigger(write_out_trigger)

		if not isdir(output):
			os.makedirs(output)

		self.inputs = defaultdict(list)

	def __call__(self, trainer):
		self.gather(trainer)
		self.write_out(trainer)

	def matches(self, key):
		return self.match_regex is None or \
			re.search(self.match_regex, key) is not None

	def gather(self, trainer):
		if not self.gather_trigger(trainer): return
		updater = trainer.updater
		model = updater.get_optimizer('main').target
		for child in model.children():
			for name, link in child.namedlinks(skipself=True):
				if not hasattr(link, "inputs"): continue
				key = "{}/{}".format(child.name, name)
				if not self.matches(key): continue
				inputs = chainer.cuda.to_cpu(link.inputs[0].data)
				self.inputs[key].append(inputs.astype(np.float16))

	def write_out(self, trainer):
		if not self.write_out_trigger(trainer): return
		updater = trainer.updater
		epoch = updater.epoch
		iteration = updater.iteration
		fname = join(self.output, "{}_{}".format(epoch, iteration))
		inputs = {key: np.vstack(values) for key, values in self.inputs.items()}
		self.inputs.clear()
		np.savez(fname, **inputs)

