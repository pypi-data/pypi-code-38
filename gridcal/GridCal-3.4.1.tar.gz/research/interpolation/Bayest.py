__author__ = 'Santiago Peñate Vera'

from numba import double, int16, boolean, vectorize, complex128
import numpy as np
from numba.decorators import jit
from itertools import product
from matplotlib import pyplot as plt

np.set_printoptions(linewidth=200)


# @jit(argtypes=[double, double], target='cpu')
# @vectorize(['double(double, double)'], target='cpu')
def fast_normal(x, s):
    """
    Function that returns the area of the two tails of the Normal law with the mean equal to zero
    x: point
    s: standard deviation

    returns: 1 - probability of x.
    """
    #    if x > (8*s):
    #        qx = 0.0
    #
    #    else:
    xm = 0
    # define coefficients B[i)
    B = np.array([1.330274429, -1.821255978, 1.781477937, -0.356563782, 0.319381530])
    pp = 0.2316419
    y = (x - xm) / s  # reduced variable
    zy = np.exp(-y * y / 2.0) / 2.506628275
    # fx = zy / s;
    # calculate qx by Horner's method
    t = 1.0 / (1.0 + pp * y)
    po = 0.0
    for Bi in B:
        po = po * t + Bi
    po *= t
    qx = zy * po  # 1-probability = tail
    # *px = 1.0 - *qx; #probability

    return 2 * qx  # twice the tail


def euclidean_distance_nd(point1, point2, dim):
    """
    Euclidean distance in N dimensions
    @param point1: Array of coordinates of the Point P
    @param point2: Array of coordinates of the point S (must agree the dimensions of P)
    @param dim: number of dimensions (provided for speed)
    @return: Euclidean distance between the points P and S
    """
    sum_ = 0
    for i in range(dim):
        sum_ += np.power(point1[i] - point2[i], dim)

    d = np.power(sum_, 1.0 / dim)
    return d


# @jit(argtypes=[double[:], double[:], double[:], double[:], double[:]], target='cpu')
def create_distance_matrix(sigma, measured_points, new_points):
    """
    Calculates the probability given the measured points and the
    new points and a certain standard deviation of the normal
    law used (sigma)
    @param sigma: standard deviation (parameter of choice) after 6sigma, the distance is zero
    @param measured_points: 2D array containing the measured points coordinates (row: point index, col: dimension index)
    @param new_points: 2D array containing the new points coordinates (row: point index, col: dimension index)

    @return: Distance matrix (rows: measured point index, cols: new point index)
    """

    new_num, dim_new = np.shape(new_points)
    measured_num, dim = np.shape(measured_points)

    assert dim_new == dim

    d_matrix = np.empty((measured_num, new_num), dtype=type(measured_points[0, 0]))
    for i, j in product(range(measured_num), range(new_num)):
        d = euclidean_distance_nd(measured_points[i, :], new_points[j, :], dim)
        d_matrix[i, j] = fast_normal(d, sigma)

    return d_matrix, measured_num, new_num


# @jit(argtypes=[double[:, :], double[:], int16, int16], target='cpu')
def interpolate_(d_matrix, measured_values, measured_num, new_num):
    """
    Compute the particles irradiation level and weight based on the probabilistic
    smoothing of the sensor measurements.
    @param d_matrix: Distance matrix
    @param measured_values: 2D array containing the values of the measured points
    @param measured_num: number of measured values -> number of columns of d_matrix
    @param new_num: number of new values -> number of rows of d_matrix

    @return:
    """

    values_num, dim_vals = np.shape(measured_values)

    assert values_num == measured_num

    interpolated_values = np.empty((new_num, dim_vals), dtype=type(measured_values[0, 0]))
    for i in range(new_num):
        # sum_d = 0.0
        # sum_d_val = 0.0
        # for j in range(measured_num):
        #     sum_d += d_matrix[j, i]
        #     sum_d_val += measured_values[j, :] * d_matrix[j, i]
        sum_d = np.sum(d_matrix[:, i])
        sum_d_val = np.dot(measured_values.transpose(), d_matrix[:, i])

        if sum_d != 0:
            interpolated_values[i, :] = sum_d_val / sum_d
        else:
            interpolated_values[i, :] = 0

    return interpolated_values


def interpolate(measured_points, new_points, measured_values, sigma_):
    """
    Interpolation using the bayesian estimation technique
    @param measured_points: 2D array containing the measured points coordinates (row: point index, col: dimension index)
    @param new_points: 2D array containing the new points coordinates (row: point index, col: dimension index)
    @param measured_values: 2D array containing the values of the measured points
    @param sigma_: per unit standard deviation to consider
    @return: Interpolated points as 2D array (row: point index, col: dimension index)
    """

    # compute the value of sigma
    dim = len(measured_points.transpose())
    p_min = [np.min(measured_points[:, i]) for i in range(dim)]
    p_max = [np.max(measured_points[:, i]) for i in range(dim)]
    sigma = euclidean_distance_nd(p_min, p_max, dim) * sigma_

    # create the distance matrix
    d_mat, measured_num, new_num = create_distance_matrix(sigma, measured_points, new_points)

    # interpolate the new points
    new_values = interpolate_(d_mat, measured_values, measured_num, new_num)

    return new_values

if __name__ == '__main__':
    print('Test')
    res = np.load('Bus6_stochastic_voltages.npz')

    V = res['V']
    S = res['S']

    # pick the first Power point to interpolate (because we know that the solution is V[0, :])
    Snew = np.array([S[0, :]])

    # interpolate
    Vnew = interpolate(S, Snew, V, 0.01)

    # compute the difference
    diff = Vnew[0, :] - V[0, :]

    print('Error: ', max(abs(diff)))

    ####################################################################################################################
    # Again with a new point
    ####################################################################################################################
    dim = len(S.transpose())
    p_min = np.array([np.min(S[:, i]) for i in range(dim)])
    p_max = np.array([np.max(S[:, i]) for i in range(dim)])

    Snew = list()
    rnd = np.random.random_sample(100).transpose()
    for r in rnd:
        Snew.append(p_min + (p_max - p_min) * r)
    Snew = np.array(Snew)

    Vnew = interpolate(S, Snew, V, 0.1)

    Vnew.sort(axis=0)  # no need to sort
    print('|V|\n', abs(Vnew))

    # plt.plot(abs(Vnew))
    # plt.show()