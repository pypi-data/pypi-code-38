from __future__ import division
import datetime, sys, time

from chainer.training import extension
from chainer.training.extensions import util
from chainer.training import trigger


class JupyterProgressBar(extension.Extension):

	def __init__(self, training_length=None, update_interval=100,
				 bar_length=50):
		self._training_length = training_length
		self._status_template = None
		self._update_interval = update_interval
		self._bar_length = bar_length
		self._recent_timing = []

		self.progress = None
		self.start = None
		if self._training_length is not None:
			self.init_bar()


	def init_bar(self):
		from ipywidgets import IntProgress, HTML, VBox
		from IPython.display import display
		size = self._training_length[0]
		self.total_progress = IntProgress(min=0, max=self._bar_length, value=0)
		self.epoch_progress = IntProgress(min=0, max=self._bar_length, value=0)

		self.total_progress.bar_style = 'info'
		self.epoch_progress.bar_style = 'info'

		self.progress_label = HTML()
		self.eta_label = HTML()

		box = VBox(children=[
			self.eta_label,
			self.total_progress,
			self.epoch_progress,
			self.progress_label,
		])
		display(box)


	def __call__(self, trainer):
		# initialize some attributes at the first call
		if self._training_length is None:
			t = trainer.stop_trigger
			if not isinstance(t, trigger.IntervalTrigger):
				raise TypeError(
					'cannot retrieve the training length from %s' % type(t))
			self._training_length = t.period, t.unit
			self.init_bar()

		if self._status_template is None:
			self._status_template = " | ".join([
				'{0.iteration:10} iter',
				'{0.epoch} epoch / %s %ss' % self._training_length,
				'Training time: {1}'
			])

		length, unit = self._training_length

		iteration = trainer.updater.iteration

		# print the progress bar
		if iteration % self._update_interval != 0: return

		epoch = trainer.updater.epoch_detail
		self._recent_timing = self._recent_timing
		now = time.time()

		self._recent_timing.append((iteration, epoch, now))

		if unit == 'iteration':
			rate = iteration / length
		else:
			rate = epoch / length
		epoch_rate = epoch - int(epoch)

		self.total_progress.value = int(rate * self._bar_length)
		self.epoch_progress.value = int(epoch_rate * self._bar_length)
		self.progress_label.value = " | ".join([
			"This epoch: {: 6.2%}".format(epoch_rate),
			"total: {: 6.2%}".format(rate),
		])

		old_t, old_e, old_sec = self._recent_timing[0]
		span = now - old_sec

		if span != 0:
			speed_t = (iteration - old_t) / span
			speed_e = (epoch - old_e) / span
		else:
			speed_t = float('inf')
			speed_e = float('inf')

		if unit == 'iteration':
			ETA_total = (length - iteration) / speed_t
		else:
			ETA_total = (length - epoch) / speed_e

		ETA_epoch = (1 - epoch_rate) / speed_e

		self.eta_label.value = "<br>".join([
			self._status_template.format(
				trainer.updater,
				0 if self.start is None else datetime.timedelta(seconds=now - self.start)
			),
			"Time per iter: {} and epoch: {}".format(
				datetime.timedelta(seconds=1 / speed_t),
				datetime.timedelta(seconds=int(1/speed_e))
			),
			"Epoch ready in: {} and training in: {}".format(
				datetime.timedelta(seconds=int(ETA_epoch)),
				datetime.timedelta(seconds=int(ETA_total))
			)
		])


		if len(self._recent_timing) > 100:
			self._recent_timing.pop(0)

	def initialize(self, trainer):
		self.start = time.time()

	def finalize(self):
		if hasattr(self, "total_progress"):
			self.total_progress.bar_style = 'success'
		if hasattr(self, "epoch_progress"):
			self.epoch_progress.bar_style = 'success'
