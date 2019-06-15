from typing import Tuple, List

from utils import Number


class Particle:
    def __init__(self, mass: Number, position: List[Number], velocity: List[Number]):
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.is_alive = True

    def apply_force(self, force: Tuple[Number, Number]):
        for i in range(len(force)):
            self.velocity[i] += force[i] / self.mass

    def exist(self):
        for i in range(len(self.position)):
            self.position[i] += self.velocity[i]


class Law:
    def compute_force(self, particle: Particle, other_particle: Particle) -> Tuple[Number, Number]:
        raise NotImplementedError
