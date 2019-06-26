'''
sensor.py

Cedrick Argueta
cdrckrgt@stanford.edu

sensor stuff
'''
import numpy as np
from scipy.stats import norm
from PyFEBOL import util

class Sensor(object):
    def __init__(self):
        raise Exception("please instantiate a specific sensor, this is just a base class!")
    
    def observe(self):
        raise Exception("please instantiate a specific sensor, this is just a base class!")

class BearingOnlySensor(Sensor):
    def __init__(self, sigma):
        self.sigma = sigma # std dev for noise in observations

    def observe(self, theta, pose):
        truth = util.getTrueBearing(theta, pose)
        noise = self.sigma * np.random.randn()
        return (truth + noise) % 360.
 
    def prob(self, theta, pose, obs):
        bearing = util.getTrueBearing(theta, pose)
        obsDiff = util.fit180(obs - bearing)
        return norm.pdf(obsDiff, 0, self.sigma)

class FOVSensor(Sensor):
    # requires headings to be input if you want something good...
    def __init__(self, alpha, cone_width, blind_distance):
        self.alpha = alpha
        self.cone_width = cone_width
        self.a1 = self.cone_width / 2.
        self.a2 = 180. - self.a1
        self.blind_distance = blind_distance

    def _getProb(self, bearing):
        if bearing < self.a1:
            return 1.0 - self.alpha
        elif bearing < self.a2:
            return 0.5
        else:
            return self.alpha

    def observe(self, theta, pose):
        truth = util.getTrueBearing(pose, theta)
        rel_bearing = np.absolute(util.fit180(pose[2] - truth))

        if type(rel_bearing) == np.ndarray:
            prob_in_view = np.vectorize(self._getProb)(rel_bearing)
            distance = util.getDistance2(pose, theta)
            prob_in_view[np.where(distance > self.blind_distance ** 2)] = 0.5
            obs = np.where(np.random.randn(len(rel_bearing)) < prob_in_view, 0, 1)
            return obs
        else:
            prob_in_view = self._getProb(rel_bearing)
            distance = util.getDistance2(pose, theta)
            if distance > self.blind_distance ** 2:
                prob_in_view = 0.5
            obs = 0 if np.random.randn() < prob_in_view else 1
            return obs

    def prob(self, theta, pose, obs):
        truth = util.getTrueBearing(pose, theta)
        rel_bearing = np.absolute(util.fit180(pose[2] - truth))

        if type(rel_bearing) == np.ndarray:
            prob_in_view = np.vectorize(self._getProb)(rel_bearing)
            distance = util.getDistance2(pose, theta)
            prob_in_view[np.where(distance > self.blind_distance ** 2)] = 0.5
            prob = np.where(obs == 1, prob_in_view, 1.0 - prob_in_view)
            return prob
        else:
            prob_in_view = self._getProb(rel_bearing)
            distance = util.getDistance2(pose, theta)
            if distance > self.blind_distance ** 2:
                prob_in_view = 0.5
            if obs == 1:
                return prob_in_view
            else:
                return 1.0 - prob_in_view

        
