from abc import ABCMeta, abstractmethod
import copy
import torch
from .distributions import levy
from typing import Tuple


class BaseAgent(metaclass=ABCMeta):

    def __init__(self,
                 n_clusters: int,
                 ):
        self.n_clusters = n_clusters
        self.centroids = None

    @abstractmethod
    def train_feedback(self, *args, **kwargs):
        pass

    @abstractmethod
    def run_feedback(self, *args, **kwargs):
        pass

    def initialize(self,
                   data: torch.Tensor,
                   ) -> None:
        indexes = torch.randint(0, data.shape[0], (self.n_clusters,))
        self.centroids = copy.deepcopy(data[indexes])

    def run(self,
            data: torch.Tensor,
            ) -> Tuple[torch.Tensor, float]:
        """
        Calculate Euclidean distance between data and centroids
        """
        distances = []
        for centroid in self.centroids:
            distance = torch.pow(data - centroid, 2).sum(1)
            distances.append(distance)
        distances = torch.stack(distances, dim=1)
        prediction = torch.argmin(distances, dim=1)

        score = 0.0
        for i, centroid in enumerate(self.centroids):
            indexes = (prediction == i).nonzero()
            score += torch.pow(data[indexes] - centroid, 2).sum()

        self.run_feedback(score)

        return prediction, score


class PSOAgent(BaseAgent):

    def __init__(self,
                 n_clusters: int,
                 social_coefficient: float,
                 personal_coefficient: float,
                 inertia: float,
                 ):
        BaseAgent.__init__(self, n_clusters, )
        self.social_coefficient = social_coefficient
        self.personal_coefficient = personal_coefficient
        self.inertia = inertia
        self.velocity = None
        self.personal_best_position = 0
        self.personal_best_score = float('inf')

    def run_feedback(self,
                     score: float,
                     ) -> None:
        if score < self.personal_best_score:
            self.personal_best_position = copy.deepcopy(self.centroids)
            self.personal_best_score = score

    def train_feedback(self,
                       social_best_position: torch.Tensor,
                       ) -> None:
        inertia = self.inertia * self.velocity
        personal = self.personal_coefficient * torch.empty((self.velocity.shape[0], self.velocity.shape[1])).uniform_(0, 1) * (self.personal_best_position - self.centroids)
        social = self.social_coefficient * torch.empty((self.velocity.shape[0], self.velocity.shape[1])).uniform_(0, 1) * (social_best_position - self.centroids)
        self.velocity = inertia + personal + social
        self.centroids += self.velocity

    def initialize(self,
                   data: torch.Tensor,
                   ) -> None:
        indexes = torch.randint(0, data.shape[0], (self.n_clusters, ))
        self.centroids = copy.deepcopy(data[indexes])
        features = data.shape[1]
        self.velocity = torch.empty((self.n_clusters, features)).uniform_(-1, 1)


class CSAgent(BaseAgent):

    def __init__(self,
                 n_clusters: int,
                 levy_alpha: int,
                 ):
        BaseAgent.__init__(self, n_clusters, )
        self.levy_alpha = levy_alpha
        self.score = float('inf')

    def run_feedback(self,
                     score: float,
                     ) -> None:
        if score < self.score:
            self.score = score

    def train_feedback(self,
                       social_best_position: torch.Tensor,
                       ) -> None:
        change = 2 * levy(self.centroids.shape, alpha=self.levy_alpha) * (social_best_position - self.centroids)
        self.centroids += change


class WSAgent(BaseAgent):

    def __init__(self,
                 n_clusters: int,
                 radius: float,
                 step_size: float,
                 velocity_factor: float,
                 ):
        BaseAgent.__init__(self, n_clusters, )
        self.radius = radius
        self.step_size = step_size
        self.velocity_factor = velocity_factor
        self.personal_best_position = 0
        self.personal_best_score = float('inf')

    def run_feedback(self,
                     score: float,
                     ) -> None:
        if score < self.personal_best_score:
            self.personal_best_position = copy.deepcopy(self.centroids)
            self.personal_best_score = score

    def train_feedback(self,
                       social_best_position: torch.Tensor,
                       ) -> None:
        pass





