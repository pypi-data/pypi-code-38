from abc import ABCMeta, abstractmethod
from collections import deque
import copy
import operator
import torch
import random


class BaseSwarm(metaclass=ABCMeta):

    def __init__(self):
        self.swarm = None
        self.agents = []

    @abstractmethod
    def train(self, *args, **kwargs):
        pass

    def populate(self, agent, n_agents):
        self.agents.append(agent)
        for i in range(n_agents - 1):
            clone = copy.deepcopy(agent)
            self.agents.append(clone)

    def predict(self, data):
        agent = self.agents[0]
        labels, score = agent.run(data=data)
        return labels, score


class PSOSwarm(BaseSwarm):

    def __init__(self):
        BaseSwarm.__init__(self)
        self.social_best_position = None
        self.social_best_score = float('inf')

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:
        all_scores = []
        scores_window = deque(maxlen=10)

        for agent in self.agents:
            agent.initialize(data)

        self.social_best_position = self.agents[0].centroids

        for episode in range(0, episodes):
            episode += 1
            scores = []
            for agent in self.agents:
                agent.train_feedback(self.social_best_position)
                _, score = agent.run(data)

                if self.social_best_score > score:
                    self.social_best_position = copy.deepcopy(agent.centroids)
                    self.social_best_score = score

                scores.append(score)

            avg_score = torch.stack(scores).mean()
            scores_window.append(avg_score)
            all_scores.append(avg_score)
            scores_window_mean = torch.stack(list(scores_window)).mean()

            print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean), end="")
            if episode % 20 == 0:
                print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean))

        self.agents.sort(key=operator.attrgetter('personal_best_score'))


class CSSwarm(BaseSwarm):

    def __init__(self,
                 expose: float,
                 discoverability: float,
                 ):
        BaseSwarm.__init__(self)
        self.expose = expose
        self.discoverability = discoverability
        self.social_best_position = None
        self.social_best_score = float('inf')

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:
        all_scores = []
        scores_window = deque(maxlen=10)

        for agent in self.agents:
            agent.initialize(data)

        self.social_best_position = self.agents[0].centroids

        for episode in range(0, episodes):
            episode += 1
            scores = []

            for agent in self.agents:
                agent.train_feedback(self.social_best_position)
                _, score = agent.run(data)

                if self.social_best_score > score:
                    self.social_best_position = copy.deepcopy(agent.centroids)
                    self.social_best_score = score

                scores.append(score)

            avg_score = torch.stack(scores).mean()
            scores_window.append(avg_score)
            all_scores.append(avg_score)
            scores_window_mean = torch.stack(list(scores_window)).mean()

            print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean), end="")
            if episode % 20 == 0:
                print('\rEpisode {}\tAverage Score: {:.2f}'.format(episode, scores_window_mean))

            self.agents.sort(key=operator.attrgetter('score'))
            n_bad_agents = int(len(self.agents)*self.expose)
            for agent in self.agents[:n_bad_agents]:
                rand1 = torch.empty(1).uniform_(0, 1)
                rand2 = torch.empty(1).uniform_(0, 1)
                xa = random.choice(self.agents).centroids
                xb = random.choice(self.agents).centroids
                change = rand1 * (rand2 > self.discoverability)[0] * (xa - xb)
                agent.centroids += change


class WSSwarm(BaseSwarm):

    def __init__(self,
                 enemy_probability: float,
                 ):
        BaseSwarm.__init__(self)
        self.social_best_position = 0
        self.social_best_score = float('inf')

    def train(self,
              data: torch.Tensor,
              episodes: int,
              ) -> None:
        all_scores = []
        scores_window = deque(maxlen=10)

        for agent in self.agents:
            agent.initialize(data)

        for episode in range(0, episodes):
            episode += 1
            scores = []

            for agent in self.agents:
                _, score = agent.run(data)

                if self.social_best_score > score:
                    self.social_best_position = copy.deepcopy(agent.centroids)
                    self.social_best_score = score


