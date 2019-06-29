# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import tqdm
import numpy as np

from .base import BaseOptimizer
from .base import BaseCandidate
from .search_space import SearchSpace


class EvolutionStrategy_Optimizer(BaseOptimizer):
    def __init__(
        self,
        search_config,
        n_iter,
        metric="accuracy",
        memory=None,
        n_jobs=1,
        cv=5,
        verbosity=1,
        random_state=None,
        warm_start=False,
        population=10,
        mutation_rate=0.5,
        crossover_rate=0.5,
    ):
        super().__init__(
            search_config,
            n_iter,
            metric,
            memory,
            n_jobs,
            cv,
            verbosity,
            random_state,
            warm_start,
        )
        self.population = population
        self.mutation_pop = int(population * mutation_rate)
        self.crossover_pop = int(population * crossover_rate)

        self.space = SearchSpace(warm_start, search_config)

    def _eval_all(self, X_train, y_train):
        for indiv in self.indiv_list:

            indiv.set_position(hyperpara_dict)
            indiv.eval(X_train, y_train)

    def _sort_indiv(self):
        scores = []

        for indiv in self.indiv_list:
            scores.append(indiv.score)

        scores = np.array(scores)
        index_best_scores = list(scores.argsort()[::-1])

        print("\nscores", scores, type(scores))
        print("\nindex_best_scores", index_best_scores, type(index_best_scores))
        print("\nself.indiv_list", self.indiv_list, type(self.indiv_list))

        indiv_list = np.array(self.indiv_list)
        self.indiv_list_sorted = indiv_list[index_best_scores]

        print(self.indiv_list_sorted)

    def _crossover(self, individual):
        pass

    def _mutate(self):
        for indiv in self.mutation_pop:
            pass

    def _search(self, nth_process, X_train, y_train):
        hyperpara_indices = self._init_search(nth_process, X_train, y_train)
        self._set_random_seed(nth_process)
        self.n_steps = self._set_n_steps(nth_process)

        hyperpara_dict = self.space.pos_dict2values_dict(hyperpara_indices)

        self.indiv_list = [Individual(self.model) for _ in range(self.population)]

        self._eval_all(X_train, y_train)
        self._sort_indiv()

        for indiv in self.indiv_list:
            indiv.set_position(hyperpara_dict)
            indiv.eval(X_train, y_train)

        for i in tqdm.tqdm(
            range(self.n_steps),
            desc=str(self.model_str),
            position=nth_process,
            leave=False,
        ):
            pass


class Individual(BaseCandidate):
    def __init__(self, model):
        super().__init__(model)

    def _mutate(self):
        pass
