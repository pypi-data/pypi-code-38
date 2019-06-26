'''
searchdomain.py

Cedrick Argueta
cdrckrgt@stanford.edu

the area in which the drone moves
'''
import numpy as np

class SearchDomain(object):
    def __init__(self, length, policy=None, init=None):
        self.length = length
        if init: # fix position of target
            self.theta = init
        else:
            self.theta = (np.random.rand() * self.length, np.random.rand() * self.length)  # random RF source location
        self.policy = policy

    def moveTarget(self, nb_act_repeat=1):
        if self.policy is None:
            return
        for _ in range(nb_act_repeat):
            action = self.policy.action() # in the future, might be useful to include other information like seeker position, filter, etc.
            
            newX = self.theta[0] + action[0]
            newY = self.theta[1] + action[1]
            newX, newY = np.clip([newX, newY], 0, self.length)
            
            self.theta = newX, newY
        
 
    def getTheta(self):
        return self.theta


if __name__ == '__main__':
    sd = SearchDomain(100)
    print(sd.getTheta())
