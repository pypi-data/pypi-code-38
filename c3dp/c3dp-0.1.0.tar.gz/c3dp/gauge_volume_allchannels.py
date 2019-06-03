import numpy as np
from shapely.geometry import Polygon
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import os
thisdir = os.path.dirname(__file__)


def span2angle(distance, distance_fr_sample, ):
    return (2 * (np.rad2deg(np.arctan(distance / (2 * distance_fr_sample)))))

def angle2span(Verticle_distance, angle):
    return(2*Verticle_distance*np.tan(np.deg2rad(angle/2)))


def make_cylindrical_surface(channel_start_from_sample_center,angle, height, length_misalignment_offset=0., height_misalignment_offset=0. ):

    r"""
     create a  cylinder which axis is along the vertical axis (z- axis)
    Parameters
    ----------
    channel_start_from_sample_center : float
        Longitudinal coordinate of the collimator (radius of the cylinder).
    height : float
        Height of the collimator channel ( height of the cylinder).
    angle : degree
        angular size of collimator channel ( curvature of the cylinder)
    length_misalignment_offset : float
        misalignment offset along the cylinder radius
    height_misalignment_offset : float
        misalignment offset along the cylinder axis

    Returns
    -------
    the list of the four points of the collimator channel's cylindrical opening

     """
    x=channel_start_from_sample_center+length_misalignment_offset

    return [[x, -(x*np.deg2rad(angle/2.)) , ((height / 2.)+height_misalignment_offset)],
            [x, (x*np.deg2rad(angle/2.)), ((height / 2.)+height_misalignment_offset) ],
            [x, (x*np.deg2rad(angle/2.)), ((-height / 2.)+height_misalignment_offset)],
            [x, -(x*np.deg2rad(angle/2.)), ((-height / 2.)+height_misalignment_offset)]]

def make_square(x, size,length_misalignment_offset=0., misalignment_offset=0.):
    r"""
     create a square  with the longitudinal coordinate and the height/width of the collimator  .

    Parameters
    ----------
    x : float
        Longitudinal coordinate of the collimator.
    size : float
        Height or width of the collimator (collimator is square).
    length_misalignment_offset : float
        misalignment offset along the cylinder radius
    misalignment_offset : float
        misalignment offset along the vertical  and transversal axis

    Returns
    -------
    the list of the four points of the collimator squared opening

     """
    return [ [x+length_misalignment_offset, ((-size/2)+misalignment_offset), ((size/2)+misalignment_offset)],
			 [x+length_misalignment_offset, ((size/2)+misalignment_offset), ((size/2)+misalignment_offset)],
             [x+length_misalignment_offset, ((size/2)+misalignment_offset), ((-size/2)+misalignment_offset)],
			 [x+length_misalignment_offset, ((-size/2)+misalignment_offset), ((-size/2)+misalignment_offset) ]]

def rotation_around_z_axis(vector_point, rotation_angle):
    r"""
       create a vector point after rotating a vector around z axis in 3D space anticlockwise

      Parameters
      ----------
     vector_point : list
        list of the three coordinates of a point

      rotation_angle : degree
          angle to rotate the vector.

      Returns
      -------
      the array of the rotated vector consisting of three coordinates of the vector

       """

    rotation_matrix=np.array([ [np.cos(np.deg2rad(rotation_angle)), -np.sin(np.deg2rad(rotation_angle)), 0 ], [ np.sin(np.deg2rad(rotation_angle)), np.cos(np.deg2rad(rotation_angle)), 0 ] ,
                             [0. ,0. ,1.] ])

    # vector_column=np.array(vector_point)[np.newaxis, :]

    vector_column = np.array(vector_point)


    rotated_vector=np.dot(rotation_matrix, vector_column)

    return (rotated_vector)


def rotation_around_y_axis(vector_point, rotation_angle):
    r"""
       create a vector point after rotating a vector around y axis in 3D space anticlockwise

      Parameters
      ----------
     vector_point : list
        list of the three coordinates of a point

      rotation_angle : degree
          angle to rotate the vector.

      Returns
      -------
      the array of the rotated vector consisting of three coordinates of the vector

       """

    rotation_matrix = np.array([[np.cos(np.deg2rad(rotation_angle)), 0, -np.sin(np.deg2rad(rotation_angle))],
                                [0., 1., 0.],
                                [np.sin(np.deg2rad(rotation_angle)), 0, np.cos(np.deg2rad(rotation_angle)) ]
                                ])

    vector_column = np.array(vector_point)[np.newaxis, :]

    rotated_vector = np.dot(rotation_matrix, vector_column)

    return (rotated_vector)

def rotation_around_x_axis(vector_point, rotation_angle):
    r"""
       create a vector point after rotating a vector around x axis in 3D space anticlockwise

      Parameters
      ----------
     vector_point : list
        list of the three coordinates of a point

      rotation_angle : degree
          angle to rotate the vector.

      Returns
      -------
      the array of the rotated vector consisting of three coordinates of the vector

       """

    rotation_matrix = np.array([[1., 0., 0.],

                                [0, np.cos(np.deg2rad(rotation_angle)),  -np.sin(np.deg2rad(rotation_angle)) ],

                                [0, np.sin(np.deg2rad(rotation_angle)), np.cos(np.deg2rad(rotation_angle))],

                                ])

    vector_column = np.array(vector_point)[np.newaxis, :]

    rotated_vector = np.dot(rotation_matrix, vector_column)

    return (rotated_vector)




def non_center_channels(channel_at_center):
    r"""
       create a square  with the longitudinal coordinate and the height/width of the collimator  .

      Parameters
      ----------
      x : float
          Longitudinal coordinate of the collimator.
      size : float
          Height or width of the collimator (collimator is square).
      Returns
      -------
      the list of the four points of the collimator squared opening

       """

    # rotation




def theta_phi(Collimator_square, sample_point):
    r"""
     Calculate the spherical coordinate( theta and phi) of the
     four points of the square collimator from the sample.

    Parameters
    ----------
    Collimator_square : list
        List of the four points of the collimator openning cross-section .
    sample_point : :class:`~numpy:numpy.ndarray`
        array of three coordinates of the sample (x,y,z).T

    Returns
    -------
    the tuple of theta, phi of the four points of the collimator squared opening
    where each element of the tuple is the array of theta/phi of four points of the
    collimator for a particular point of the sample

     """
    p1,p2,p3,p4=Collimator_square

    points = np.array([sample_point-p1, sample_point-p2, sample_point-p3, sample_point-p4])
    points=points.transpose(1,0,2) #shape: (pointsNum,4,3)

    theta = np.arctan2(points[:, :, 0],points[:, :, 1] )

    norm_x_y=np.sqrt(points[:, :, 0]**2+points[:, :, 1]**2)
    phi = np.arctan2(norm_x_y, points[:, :, 2])

    return theta, phi


def gauge_volume(square_theta_phy_sample, square_theta_phy_detector, sample_points_x_y):
    r"""
     Calculate the non-zero gauge volume for different positions of the sample.

    Parameters
    ----------
    square_theta_phy_sample : tuple
        the tuple of theta, phi of the four points of the collimator squared opening at
        sample side where each element of the tuple is the array of theta/phi of four points of the
        collimator for a particular point of the sample.
        e.g. (array([theta1, theta2, theta3, theta4]), array([phi1, phi2, phi3, phi4]))

     square_theta_phy_detector : tuple
        the tuple of theta, phi of the four points of the collimator squared opening at
        detector side where each element of the tuple is the array of theta/phi of four points of the
        collimator for a particular point of the sample.
        e.g. (array([theta1, theta2, theta3, theta4]), array([phi1, phi2, phi3, phi4]))

    sample_points_x_y : :class:`~numpy:numpy.ndarray`
        array of two coordinates of the sample (x,y)

    Returns
    -------
    the tuple of positions in the sample (array([y,z])) (where the gaauge volume is non-zero) , corresponding gauge volume (list)
    where the position of the sample is an array, i.e. (array([x,y]))

     """
    gauge_volume=[]

    sample_points_x_nonZero=[]
    sample_points_y_nonZero = []

    theta_phiS_arr = np.array(square_theta_phy_sample) #shape: (2, pointsNum, 4)
    theta_phiS =  theta_phiS_arr.transpose(2, 1, 0).transpose(1, 0, 2) #shape: (pointsNum, 4,2)
    theta_phiS_list = theta_phiS.tolist()
    theta_phiD_array = np.array(square_theta_phy_detector).transpose(2,1,0).transpose(1,0,2)
    theta_phiD_list=theta_phiD_array.tolist()
    for i in range(theta_phiS.shape[0]):

        s=Polygon(theta_phiS_list[i])
        d = Polygon(theta_phiD_list[i])

        if s.intersects(d):
            gauge_volume.append(s.intersection(d).area / d.area)
            sample_points_x_nonZero.append(sample_points_x_y[0, i])
            sample_points_y_nonZero.append(sample_points_x_y[1, i])


        # gauge_volume.append(s.intersection(d).area/d.area)
        # sample_points_x_nonZero.append(sample_points_x_y[0,i])
        # sample_points_y_nonZero.append(sample_points_x_y[1, i])
    return (np.array([sample_points_x_nonZero, sample_points_y_nonZero]), gauge_volume)


def making_plot(sample_points_x_y_nonZero, gauge_volume, y_upper_imit, y_lower_limit,
                sample_height=10, sample_width=5. ):
    r"""
     Saved the contour of the gauge volume in different positions of the sample in "Figure directory".

    Parameters
    ----------
    sample_points_x_y_nonZero : :class:`~numpy:numpy.ndarray`
        array of two coordinates of the sample (x,y) points where gauge volume is non-zero

    gauge_volume : list
        list of the non zero gauge volumes of different positions of the sample

    y_upper_imit : float
        the upper limit of Y-axis for the plotting view

    y_lower_imit : float
        the lower limit of Y-axis for the plotting view

     """
    if sample_points_x_y_nonZero.size==0:
        print "the array does not have a non zero gauge volume"


    else:

        xS, yS=sample_points_x_y_nonZero
        X,Y= np.meshgrid(xS,yS)

        gauge_volume=np.array(gauge_volume)

        Z = griddata((xS,yS), gauge_volume, (X,Y), method='nearest')

        plt.figure()
        # r=plt.contour( X, Y,Z)
        # plt.clabel(r, inline=1, fontsize=10)
        plt.pcolormesh(X, Y, Z, cmap = plt.get_cmap('rainbow'))
        plt.xlabel('points along sample width (mm)')
        plt.ylabel('points along sample height (mm)')
        plt.ylim(y_lower_limit,y_upper_imit)
        plt.colorbar()
        plt.axhline(y=-sample_height/2., color='r', linestyle='-')
        plt.axhline(y=sample_height/2., color='r', linestyle='-')
        plt.axvline(x=- sample_width/2., color='r', linestyle='-')
        plt.axvline(x= sample_width/2., color='r', linestyle='-')
        # plt.scatter(xS,yS ,marker = 'o', c = 'b', s = 5, zorder = 10)
        plt.savefig(os.path.join(thisdir, '../figures/{sample}.png'.format(sample='gauge_volume')))
        plt.show()







