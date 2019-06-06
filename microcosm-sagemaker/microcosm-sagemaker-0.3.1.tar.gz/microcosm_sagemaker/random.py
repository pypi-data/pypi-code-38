from random import seed

from microcosm.api import defaults

from microcosm_sagemaker.decorators import training_initializer


@defaults(
    seed=42,
)
@training_initializer()
class Random:
    def __init__(self, graph):
        self.seed = graph.config.random.seed

    def init(self):
        seed(self.seed)
