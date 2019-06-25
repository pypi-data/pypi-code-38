# Test Case for PytorchCaffe: train
# 1. train mnist in single gpu
# 2. train mnist in gpus

import unittest
import os
from ptcaffe.trainers import Trainer
from ptcaffe.utils.logger import logger

class TestMnistBase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('test/log'):
            os.makedirs('test/log')

    def testCPU(self):
        print('MnistBasicTest: testCPU')
        logger.set_screen_off()
        logger.set_file('./test/log/test_mnist.log')
        old_dir = os.getenv('PWD')
        os.chdir('./demos/mnist')
        try:
            solver = 'solver.prototxt'
            weights = None
            gpu = None
            trainer = Trainer(solver, weights, gpu)
            trainer.max_iter = 1000
            trainer.run()
            best_vals = trainer.get_best_vals()
            self.assertTrue(best_vals is not None)
            best_val = best_vals['accuracy']
            self.assertTrue(best_val > 0.98)
        except Exception:
            self.assertTrue(False)
        finally:
            os.chdir(old_dir)

    def testGPU(self):
        return
        print('MnistBasicTest: testGPU')
        logger.set_screen_off()
        logger.set_file('./test/log/test_mnist.log')
        old_dir = os.getenv('PWD')
        os.chdir('./demos/mnist')
        try:
            solver = 'solver.prototxt'
            weights = None
            gpu = '1'
            trainer = Trainer(solver, weights, gpu)
            trainer.run()
            best_vals = trainer.get_best_vals()
            self.assertTrue(best_vals is not None)
            best_val = best_vals['accuracy']
            self.assertTrue(best_val > 0.991)
        except Exception:
            self.assertTrue(False)
        finally:
            os.chdir(old_dir)

    def testGPUs(self):
        return
        print('MnistBasicTest: testGPUs')
        logger.set_screen_off()
        logger.set_file('./test/log/test_mnist.log')
        old_dir = os.getenv('PWD')
        os.chdir('./demos/mnist')
        try:
            solver = 'solver.prototxt'
            weights = None
            gpu = '0,1'
            trainer = Trainer(solver, weights, gpu)
            trainer.run()
            best_vals = trainer.get_best_vals()
            self.assertTrue(best_vals is not None)
            best_val = best_vals['accuracy']
            self.assertTrue(best_val > 0.991)
        except Exception:
            self.assertTrue(False)
        finally:
            os.chdir(old_dir)

if __name__ == "__main__":
    unittest.main()
