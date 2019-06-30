from abc import ABCMeta, abstractmethod
import collections
import copy
import operator
import torch
import random
from typing import Tuple


class BaseSwarm(metaclass=ABCMeta):

    def __init__(self):
        self.swarm = None
        self.agents = []
        self.social_best_position = None
        self.social_best_score = float('inf')

    @abstractmethod
    def train(self, *args, **kwargs):
        pass

    def initialize(self,
                   data: torch.Tensor,
                   ) -> None:
        for agent in self.agents:
            agent.initialize(data)
        self.social_best_position = self.agents[0].centroids

    def run_feedback(self,
                     agent,
                     score: float,
                     ) -> None:
        if self.social_best_score > score:
            self.social_best_position = copy.deepcopy(agent.centroids)
            self.social_best_score = score

    def populate(self,
                 agent,
                 n_agents: int,
                 ) -> None:
        self.agents.append(agent)
        for _ in range(n_agents - 1):
            clone = copy.deepcopy(agent)
            self.agents.append(clone)

    def predict(self,
                data: torch.Tensor,
                ) -> Tuple[list, float]:
        agent = self.agents[0]
        labels, score = agent.run(data=data)
        return labels, score

    @staticmethod
    def print_scores(episode: int,
                     scores: list,
                     all_scores: list,
                     scores_window: collections.deque,
                     ):

        avg_score = torch.stack(scores).mean()
        scores_window.append(avg_score)
        all_scores.append(avg_score)
        scores_window_mean = torch.stack(list(scores_window)).mean()

        print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean), end="")
        if episode % 20 == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean))


class PSOSwarm(BaseSwarm):

    def __init__(self):
        BaseSwarm.__init__(self)

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:
        all_scores = []
        scores_window = collections.deque(maxlen=10)

        self.initialize(data=data)

        for episode in range(1, episodes + 1):
            scores = []

            for agent in self.agents:
                agent.train_feedback(self.social_best_position)
                _, score = agent.run(data)
                self.run_feedback(agent=agent, score=score)
                scores.append(score)

            self.print_scores(episode=episode, scores=scores, all_scores=all_scores, scores_window=scores_window)

        self.agents.sort(key=operator.attrgetter('personal_best_score'))


class CSSwarm(BaseSwarm):

    def __init__(self,
                 expose: float,
                 discoverability: float,
                 ):
        BaseSwarm.__init__(self)
        self.expose = expose
        self.discoverability = discoverability

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:

        all_scores = []
        scores_window = collections.deque(maxlen=10)

        self.initialize(data=data)

        for episode in range(1, episodes + 1):
            scores = []

            for agent in self.agents:
                agent.train_feedback(self.social_best_position)
                _, score = agent.run(data)
                self.run_feedback(agent=agent, score=score)
                scores.append(score)

            self.print_scores(episode=episode, scores=scores, all_scores=all_scores, scores_window=scores_window)

            self.agents.sort(key=operator.attrgetter('score'))
            n_bad_agents = int(len(self.agents)*self.expose)
            for agent in self.agents[:n_bad_agents]:
                rand1 = torch.empty(1).uniform_(0, 1)
                rand2 = torch.empty(1).uniform_(0, 1)
                xa = random.choice(self.agents).centroids
                xb = random.choice(self.agents).centroids
                change = rand1 * (rand2 > self.discoverability)[0] * (xa - xb)
                agent.centroids += change


class GWOSwarm(BaseSwarm):

    def __init__(self):
        BaseSwarm.__init__(self)
        self.alpha = None
        self.beta = None
        self.delta = None

    def run_feedback(self,
                     agent,
                     score: float,
                     ) -> None:
        if score < self.alpha.personal_best_score:
            self.alpha = agent
        elif score < self.beta.personal_best_score:
            self.beta = agent
        elif score < self.delta.personal_best_score:
            self.delta = agent

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:
        all_scores = []
        scores_window = collections.deque(maxlen=10)

        self.initialize(data=data)
        self.alpha = self.agents[0]
        self.beta = self.agents[1]
        self.delta = self.agents[2]

        for episode in range(1, episodes + 1):
            scores = []

            a = 2 - 2 * episode / episodes

            for agent in set(self.agents) - {self.alpha}:
                _, score = agent.run(data)
                self.run_feedback(agent=agent, score=score)
                scores.append(score)

                agent.train_feedback(
                    a,
                    self.alpha.personal_best_position,
                    self.beta.personal_best_position,
                    self.delta.personal_best_position,
                )

            self.print_scores(episode=episode, scores=scores, all_scores=all_scores, scores_window=scores_window)

