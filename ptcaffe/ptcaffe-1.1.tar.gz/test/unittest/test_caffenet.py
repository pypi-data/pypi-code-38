import unittest
import os

class TestCaffeNet(unittest.TestCase):
    def test_SetPhase(self):
        print('TestCaffeNet: set phase')
        from ptcaffe.caffenet import CaffeNet
        net = CaffeNet('./demos/mnist/deploy.prototxt', phase = 'TRAIN')
        net.set_phase('TEST')
        self.assertTrue(net.phase == 'TEST')
        net.train()
        self.assertTrue(net.phase == 'TRAIN')
        
