import bisect
import json
import math
from pathlib import Path
from typing import Optional

import jsonschema

from .configs import LineChainConfig, Line


class LineChain:
    with open(str(Path(__file__).parent / 'schema' / 'line_chain_config.json')) as f:
        schema = json.load(f)

    def __init__(self, config: LineChainConfig):
        self.lines = sorted(config.items, key=lambda x: x.ratio)
        self.ratios = [scheduler.ratio for scheduler in self.lines]
        if self.ratios[-1] != 1.0:
            self.lines.append(Line({
                'mode': 'fixed',
                'ratio': 1.0,
                'target': self.lines[-1].target
            }))
            self.ratios.append(1.0)

        previous: Optional[Line] = None
        for line in self.lines:
            if line.mode == 'fixed':
                line.start = line.target
            elif line.start is None:
                line.start = previous.target
            previous = line

    @staticmethod
    def mode_fixed(_: float):
        return 1.0

    @staticmethod
    def mode_linear(r: float):
        return r

    @staticmethod
    def mode_cosine(r: float):
        return (1.0 - math.cos(r * math.pi)) / 2

    def at(self, ratio: float) -> float:
        assert 0.0 <= ratio <= 1.0
        index = bisect.bisect_left(self.ratios, ratio)
        current = self.lines[index]

        previous_ratio = 0.0 if index == 0 else self.lines[index - 1].ratio
        r = (ratio - previous_ratio) / (current.ratio - previous_ratio)
        r = eval(f'self.mode_{current.mode}')(r)

        return current.start + (current.target - current.start) * r

    def __getitem__(self, ratio: float):
        return self.at(ratio)

    def __repr__(self):
        return '\n'.join([
            f'{self.__class__.__name__} (',
            *[
                f' {item.ratio * 100: 6.1f}%, {item.mode} from {item.start} to {item.target},'
                for item in self.lines
            ],
            f')'
        ])

    @classmethod
    def factory(cls, config: list):
        jsonschema.validate(config, cls.schema)
        return cls(config=LineChainConfig(config))


factory = LineChain.factory
