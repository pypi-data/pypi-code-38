from drone import Drone
from sensor import BearingOnlySensor, FOVSensor
from searchdomain import SearchDomain
from filter import ParticleFilter, DiscreteFilter
from policy import MeanPolicy, RandomPolicy, ConstantVelocityPolicy
from cost import EntropyDistanceCostModel, MaxEigenvalDistanceCostModel
from util import getDistance2

import numpy as np

m = SearchDomain(200.0, policy=ConstantVelocityPolicy(1.0, -0.5))

# s = FOVSensor(0.1, 120., 25)
s = BearingOnlySensor(10.0)

d = Drone(25, 25, 60, 2.0, s, m)
print("drone pose: ", d.getPose())

f = ParticleFilter(m, 64, s, d.maxStep, 10000)
# f = DiscreteFilter(m, 25, s)

# p = MeanPolicy(d.maxStep, 36) 
p = ConstantVelocityPolicy()

# c = EntropyDistanceCostModel(lambda_=0.1, threshold=15.0)
c = MaxEigenvalDistanceCostModel(lambda_=0.1, threshold=15.0)
cost = 0

num_steps = 0

# a problem: what happens when all actions take you away from the mean, and the
# policy chooses the mean? you just keep choosing that forever?

while getDistance2(d.getPose(), m.getTheta()) > 5 and num_steps < 100:
    num_steps += 1

    # observe
    obs = s.observe(m.getTheta(), d.getPose())
    print("sample obs: ", obs)
    print("theta: ", m.getTheta())

    # update filter belief
    f.update(d.getPose(), obs)
    print('entropy: ', f.entropy())
    print('max prob: ', f.maxProbBucket())
    # print('x: ', f.x_particles)
    # print('dx: ', f.dx_particles)
    # print('y: ', f.y_particles)
    # print('dy: ', f.dy_particles)

    # calculate action
    a = p.action()

    # act
    d.act(a)
    m.moveTarget()

    curr_cost = c.getCost(m, d, f, a)
    print('cost: ', curr_cost)
    cost += curr_cost

    # confirm that it's moved
    print("drone pose, after movement: ", d.getPose())

print("total cost was: ", cost)
print("total steps was: ", num_steps)
