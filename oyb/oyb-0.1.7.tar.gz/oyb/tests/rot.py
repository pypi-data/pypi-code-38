"""
"""

import numpy
import unittest
from math import pi
from oyb import rot

def norm(v):
    return v.dot(v)**0.5
    
class VectorRotation(unittest.TestCase):
    def test_x(self):
        v = rot.x(0.5 * pi).dot(numpy.array([0,0,1]))
        self.assertTrue(norm(v - numpy.array([0,-1,0])) < 1e-8)
        
    def test_y(self):
        v = rot.y(0.5 * pi).dot(numpy.array([0,0,1]))
        self.assertTrue(norm(v - numpy.array([1,0,0])) < 1e-8)
        
    def test_z(self):
        v = rot.z(0.5 * pi).dot(numpy.array([1,0,0]))
        self.assertTrue(norm(v - numpy.array([0,1,0])) < 1e-8)

class FrameTransformation(unittest.TestCase):
    def test_X(self):
        v = rot.X(0.5 * pi).dot(numpy.array([0,0,1]))
        self.assertTrue(norm(v - numpy.array([0,1,0])) < 1e-8)
        
    def test_Y(self):
        v = rot.Y(0.5 * pi).dot(numpy.array([0,0,1]))
        self.assertTrue(norm(v - numpy.array([-1,0,0])) < 1e-8)
        
    def test_Z(self):
        v = rot.Z(0.5 * pi).dot(numpy.array([1,0,0]))
        self.assertTrue(norm(v - numpy.array([0,-1,0])) < 1e-8)
        
class TransformationSequence(unittest.TestCase):
    def test_example4p7(self):
        O = rot.Z(40 * pi / 180)
        i = rot.X(30 * pi / 180)
        w = rot.Z(60 * pi / 180)
        wiO_act = w.dot(i).dot(O)
        wiO_ref = numpy.array([
            [-0.099068, 0.89593, 0.43301],
            [-0.94175, -0.22496, 0.25],
            [0.32139, -0.38302, 0.86603]])
        dWIO = (wiO_ref - wiO_act).reshape((9,))
        self.assertTrue(dWIO.dot(dWIO)**0.5 < 1e-4)
        
class SphericalFrame(unittest.TestCase):
    def test_xyz1sph(self):
        xyz = numpy.array([-5.368e6, -1.784e6, 3.691e6])
        sph = rot.xyz2sph(xyz)
        self.assertTrue(abs(sph[0] - 198.4 * pi / 180) / sph[0] < 1e-3)
        self.assertTrue(abs(sph[1] - 33.12 * pi / 180) / sph[1] < 1e-3)
        self.assertTrue(abs(sph[2] - 6.754e6) / sph[2] < 1e-3)
        
if __name__ == '__main__':
    unittest.main()
