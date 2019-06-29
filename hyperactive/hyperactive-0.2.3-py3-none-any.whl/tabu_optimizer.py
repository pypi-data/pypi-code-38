# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import tqdm

from .base import BaseOptimizer


class Tabu_Optimizer(BaseOptimizer):
    def __init__(
        self,
        search_config,
        n_iter,
        metric="accuracy",
        tabu_memory=None,
        n_jobs=1,
        cv=5,
        verbosity=1,
        random_state=None,
        warm_start=False,
    ):
        super().__init__(
            search_config,
            n_iter,
            metric,
            tabu_memory,
            n_jobs,
            cv,
            verbosity,
            random_state,
            warm_start,
        )
        self._search = self._start_evolution_strategy_optimizer

    def _start_tabu_optimizer(self, nth_process):
        self._set_random_seed(nth_process)
        n_steps = int(self.n_iter / self.n_jobs)

        for i in tqdm.tqdm(range(n_steps), position=nth_process, leave=False):
            pass
