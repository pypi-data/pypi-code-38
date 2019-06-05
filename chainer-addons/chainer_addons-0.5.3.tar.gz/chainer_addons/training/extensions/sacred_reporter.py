from chainer import reporter
from chainer.training import trigger as trigger_module
from chainer.training.extension import Extension

class SacredReport(Extension):
	def __init__(self, ex, keys=None, trigger=(1, "epoch")):
		super(SacredReport, self).__init__()
		self.ex = ex
		self._keys = keys
		self._trigger = trigger_module.get_trigger(trigger)

		self._init_summary()

	def initialize(self, trainer):
		pass

	def __call__(self, trainer):
		if self.ex is None:
			return

		obs = trainer.observation
		keys = self._keys

		if keys is None:
			self._summary.add(obs)
		else:
			self._summary.add({k: obs[k] for k in keys if k in obs})

		if not self._trigger(trainer):
			return

		stats = self._summary.compute_mean()
		epoch = trainer.updater.epoch
		for name in stats:
			self.ex.log_scalar(name, float(stats[name]), step=epoch)

		self._init_summary()

	def _init_summary(self):
		self._summary = reporter.DictSummary()
