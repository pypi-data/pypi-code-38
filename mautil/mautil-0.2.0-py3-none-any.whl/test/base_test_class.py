import unittest
import numpy as np

class Test(unittest.TestCase):
    seed=9527
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self._rs = np.random.RandomState(self.seed)

