import numpy as np

# import unittest
# from numpy.testing import assert_allclose
from c3dp import gauge_volume as gv


sample_height=26. #mm
sample_width=4.16 #mm
collimator_openningSize_sample=3. # channel opening size
collimator_inner_radius=16.02
coll_length=380. #mm
collimator_outer_radius=coll_length+collimator_inner_radius
collimator_openningSize_detector=(collimator_outer_radius*collimator_openningSize_sample)/collimator_inner_radius

pointsNum=20
zS=np.linspace(-sample_height/2., sample_height/2., num=pointsNum) #sample_positions_z vertical
yS=np.linspace(-sample_width/2., sample_width/2., num=pointsNum) #saNoNsymmetric_Resolution_Test1mple_positions_y
xS=np.linspace(-sample_width/2., sample_width/2., num=pointsNum) #sample_positions_x

list_points=[]
for valX in  xS:
    for valY in yS:
        for valZ in zS:
            list_points.append([valX, valY, valZ])

# Sxy = np.array([xS, yS])
# Sxz = np.array([xS, zS])
Syz_linear = np.array([yS, zS])
S_linear = np.array([xS, yS, zS]).T
S=np.array(list_points)
Syz = np.array([S[:,1], S[:,2]])
# XS,YS,ZS=np.meshgrid(xS,yS,zS )




class TestGaugeVolume(object):
    # def test_make_square(self):
    #     collimator_inner_radius=16.02
    #     collimator_openningSize_sample=3.
    #     Cs_square = gv.make_square(collimator_inner_radius, collimator_openningSize_sample)
    #     reference=[[16.02, -3./2, 3./2], [16.02, 3./2, 3./2], [16.02, 3./2, -3./2], [16.02, -3./2, -3./2]]
    #     assert_allclose(Cs_square, reference)

    # def test_theta_phi(self):
    #     Cs_square = [[16.02, -3./2, 3./2], [16.02, 3./2, 3./2], [16.02, 3./2, -3./2], [16.02, -3./2, -3./2]]
    #     sample_points=np.array([(2.,3.), (1,2), (4,5)]).T
    #
    #     reference=[np.array[], []]
    #
    #     theta_phiS = gv.theta_phi(Cs_square, sample_points)


    #
    # def test_gauge_volume(self):
    #     Cs_square = gv.make_square(collimator_inner_radius, collimator_thickness_sample)
    #     Cd_square = gv.make_square(collimator_outer_radius, collimator_thickness_detector)
    #     sample_points = S
    #
    #     theta_phiS = gv.theta_phi(Cs_square, sample_points)
    #     theta_phiD = gv.theta_phi(Cd_square, S)
    #     sample_pos, gauge_volume = gv.gauge_volume(theta_phiS, theta_phiD, Syz)


    def test_gauge_volume(self):
        Cs_square = gv.make_square(collimator_inner_radius, collimator_openningSize_sample)
        Cd_square = gv.make_square(collimator_outer_radius, collimator_openningSize_detector)
        sample_points = S

        theta_phiS = gv.theta_phi(Cs_square, sample_points)
        theta_phiD = gv.theta_phi(Cd_square, sample_points)
        sample_pos, gauge_volume = gv.gauge_volume(theta_phiS, theta_phiD, Syz)
        gv.making_plot(sample_pos, gauge_volume )

    if __name__ == '__main__':
        test_gauge_volume()
        # unittest.main()













