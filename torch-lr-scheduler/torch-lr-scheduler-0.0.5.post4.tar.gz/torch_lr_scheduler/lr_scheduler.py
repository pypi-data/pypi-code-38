import json
from pathlib import Path

import jsonschema
import line_chain
import torch.optim

from .configs import LrSchedulerConfig


class LrScheduler:
    with open(str(Path(__file__).parent / 'schema' / 'lr_scheduler_config.json')) as f:
        schema = json.load(f)

    def __init__(self, config: LrSchedulerConfig):
        self.chain = line_chain.factory(config=config.line_chain)
        self.learning_rate_scale = config.learning_rate_scale
        self.lr = self.chain.at(0.0) * self.learning_rate_scale

    def update(self, optimizer: torch.optim.Optimizer, ratio: float):
        self.lr = self.chain.at(ratio) * self.learning_rate_scale
        for param_group in optimizer.param_groups:
            param_group['lr'] = self.lr

    def __repr__(self):
        return f'{self.__class__.__name__} (learning_rate_scale: {self.learning_rate_scale:.1f}) with {self.chain}'

    @classmethod
    def factory(cls, config: dict):
        jsonschema.validate(config, cls.schema)
        return cls(config=LrSchedulerConfig(config))


factory = LrScheduler.factory
