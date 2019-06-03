import numpy as np

import unittest
from numpy.testing import assert_allclose
from c3dp import gauge_volume as gv


class TestGaugeVolume(object):
    def test_make_square(self):
        collimator_inner_radius=16.02
        collimator_openningSize_sample=3.
        Cs_square = gv.make_square(collimator_inner_radius, collimator_openningSize_sample)
        reference=[[16.02, -3./2, 3./2], [16.02, 3./2, 3./2], [16.02, 3./2, -3./2], [16.02, -3./2, -3./2]]
        assert_allclose(Cs_square, reference)

    def test_theta_phi(self):
        Cs_square = [[16.02, -3./2, 3./2], [16.02, 3./2, 3./2], [16.02, 3./2, -3./2], [16.02, -3./2, -3./2]] # four points in the square of collimator openning at sample side
        sample_points=np.array([(0.,3.), (0.,2.), (0.,5.)]).T  #two points of the sample (0,0,0) (3,2,5)

        reference_s=[[[1.66415709, 1.47743557, 1.47743557, 1.66415709],[1.8334054, 1.60917992, 1.60917992, 1.8334054]], # theta of four points of collimator openning at sample side
                                                                                                                        # from two points in sample
                   [[1.47783981, 1.47783981, 1.66375285, 1.66375285],[1.82479067, 1.83322074, 2.03353491, 2.02003486]]] # phi of four points of collimator openning at sample side
                                                                                                                        # from two points in sample

        theta_phiS = gv.theta_phi(Cs_square, sample_points)

        assert_allclose(theta_phiS, reference_s)

        Cd_square = [[396.02, -74.16/ 2, 74.16/ 2], [396.02, 74.16/ 2, 74.16/ 2], [396.02, 74.16/2, -74.16/ 2],
                     [396.02, -74.16/ 2, -74.16/ 2]] # four points in the square of collimator openning at detector side


        theta_phid = gv.theta_phi(Cd_square, sample_points)


        reference_d=[[[1.66415577, 1.47743688, 1.47743688, 1.66415577],[1.66990568, 1.48177469, 1.48177469, 1.66990568]],# theta of four points of collimator openning at detector side
                                                                                                                        # from two points in sample
                    [[1.4778411, 1.4778411, 1.66375155, 1.66375155],[1.48975045, 1.48967362, 1.67703915, 1.67693884]]]  # phi of four points of collimator openning at detector side
                                                                                                                        # from two points in sample

        assert_allclose(theta_phid, reference_d)




    def test_gauge_volume(self):

        theta_phiS= [[[1.66415709, 1.47743557, 1.47743557, 1.66415709],[1.8334054, 1.60917992, 1.60917992, 1.8334054]], # theta of four points of collimator openning at sample side
                                                                                                                        # from two points in sample
                   [[1.47783981, 1.47783981, 1.66375285, 1.66375285],[1.82479067, 1.83322074, 2.03353491, 2.02003486]]]  # phi of four points of collimator openning at sample side
                                                                                                                        # from two points in sample

        theta_phiD = [[[1.66415577, 1.47743688, 1.47743688, 1.66415577],[1.66990568, 1.48177469, 1.48177469, 1.66990568]],# theta of four points of collimator openning at detector side
                                                                                                                        # from two points in sample
                    [[1.4778411, 1.4778411, 1.66375155, 1.66375155],[1.48975045, 1.48967362, 1.67703915, 1.67693884]]]# phi of four points of collimator openning at detector side
                                                                                                                        # from two points in sample

        Syz = np.array([ (0.,2.), (0.,5.) ]) # (y,z) in sample for two points

        sample_pos, gauge_volume = gv.gauge_volume(theta_phiS, theta_phiD, Syz)

        reference_gauge_volume=[1] #non zero gauge volume
        reference_sample_pos=np.array([0,0]).reshape(2,1) #(y,z) for corresponding positon in sample for non_zero gauge volume

        assert_allclose(sample_pos, reference_sample_pos)
        assert_allclose(gauge_volume, reference_gauge_volume)


    def test_making_plot(self):
        sample_pos=np.array([ [0.,2.], [0.,5.] ])

        gauge_volume = [1, 0]

        gv.making_plot(sample_pos, gauge_volume, -2,2 )

    if __name__ == '__main__':
        unittest.main()













