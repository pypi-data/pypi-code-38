import os, sys

import numpy as np

class DiscreteWorld(object):
    def __init__(self, height, width):
        self.agents = []
        self.landmarks = []

        self.dim_p = 2 # position dimensionality
        self.dim_color = 3 # color dimensionality

        self.h = height
        self.w = width
        self.map = np.zeros((height, width))

    def gen_wall(self, prob=0, seed=10):
        if prob == 0:
            return
        np.random.seed(seed)

        for i in range(self.h):
            for j in range(self.w):
                if i == 0 or i == self.h-1 or j == 0 or j == self.w - 1:
                    self.map[i][j] = -1
                    continue
                wall_prob = np.random.rand()
                if wall_prob < prob:
                    self.map[i][j] = -1

    def step(self):
        raise NotImplementedError

class Agent(object):
    def __init__(self):
        self.predator = True
        self.health = None
        self.property = None
        self.pos = None
        self.random = False
        self.size = None
        self.id = None
        self.dead = False
        self.original_health = None
        self.crossover=False
        self.speed = None # how many cells the agent can moves
        self.hunt_square = None
        self.max_reward = 0
        self.birth_time = None
        self.age = 0

