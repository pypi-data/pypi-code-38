import re
import logging

from chainer.training import extension

from collections import defaultdict

class AlternateTrainable(extension.Extension):
	def __init__(self, trainable_groups, interval):
		super(AlternateTrainable, self).__init__()
		assert interval >= 1

		self.trainable_groups = trainable_groups
		self.interval = interval
		self.round_interval = interval * len(trainable_groups)

	@property
	def n_groups(self):
		return len(self.trainable_groups)

	def initialize(self, trainer):
		self.model = trainer.updater.get_optimizer("main").target

		group_regexes = [
			(i, re.compile(regex))
				for i, regex in enumerate(self.trainable_groups)
					if regex is not None]

		rest_group_idx = [i
			for i, regex in enumerate(self.trainable_groups)
				if regex is None]

		assert len(rest_group_idx), "There should be only one rest group!"
		rest_group_idx = rest_group_idx[0]

		grouped_params = defaultdict(list)

		for name, param in self.model.namedparams():
			idx = rest_group_idx
			for i, group_regex in group_regexes:
				# if we match a certain name, add corresponding param to the group
				if group_regex.search(name) is not None:
					idx = i
					break
			# else use the "rest" group for the remaining params
			grouped_params[idx].append(param)

		self.grouped_params = dict(grouped_params)

	def finalize(self):
		self.model = None

	def __call__(self, trainer):
		epoch = trainer.updater.epoch
		iteration = trainer.updater.iteration
		is_new = trainer.updater.is_new_epoch or (epoch == 0 and iteration == 1)
		if not is_new: return
		if epoch % self.interval != 0: return

		subinterval = epoch % self.round_interval
		group_idx = subinterval // self.interval

		assert self.model is not None
		logging.debug(f"Epoch: {epoch}, {subinterval}")

		self.enable_group(group_idx)

	def enable_group(self, group_idx):
		logging.debug(f"Enabling group #{group_idx}")
		self.model.disable_update()
		for param in self.grouped_params[group_idx]:
			rule = param.update_rule
			if rule is not None:
				rule.enabled = True
