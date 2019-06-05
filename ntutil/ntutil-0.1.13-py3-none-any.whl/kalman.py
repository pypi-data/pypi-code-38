#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Kalman
------

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

def update(mean1, variance1, mean2, variance2):
    updated_mean = (variance2 * mean1 + variance1 * mean2) / (variance1 + variance2)
    updated_variance = 1 / (1 / variance1 + 1 / variance2)
    return (updated_mean, updated_variance)
    
def update_with_default_variance(mean1, variance1, mean2, variance2, default=0.01):
    variance1 = variance1 or default
    variance2 = variance2 or default
    return update(mean1, variance1, mean2, variance2)
    
def predict(mean1, variance1, mean2, variance2):
    predicted_mean = mean1 + mean2
    predicted_variance = variance1 + variance2
    return (predicted_mean, predicted_variance)
    
    
class Kalman(object):
    def __init__(self, mean, variance):
        self.mean = mean
        self.variance = variance
        
    def update(self, mean, variance):
        return update(self.mean, self.variance, mean, variance)
        
    def update_with_default_variance(self, mean, variance, default=0.01):
        return update_with_default_variance(self.mean, self.variance, mean, variance, default=default)
        
    def predict(self, mean, variance):
        return predict(self.mean, self.variance, mean, variance)
