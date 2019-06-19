import matplotlib.pyplot as plt
import logging

import matplotlib
from numpy import ndarray, sqrt, array, min, float64
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from scipy.signal import savgol_filter

matplotlib.use('TkAgg')


def rcf(A, rad):
    """
    Rolling circle filter (RCF) routine as described by James et al.: https://doi.org/10.1366%2F12-06766
    :param A: np matrix of data
    :param r: radius of circle to filter with
    :return: L, a numpy array of length len(A) which is the locus of the RCF
    """
    if isinstance(A, DataFrame) or isinstance(A, Series):
        A = A.values  # convert to numpy array
    elif not isinstance(A, ndarray):
        raise TypeError("Incorrect format passed for A")

    assert isinstance(rad, int) and abs(
        rad) == rad, "rad needs to be a positive integer"
    assert len(A.shape) == 1, "A needs to be a single column"

    RC = semi_circle_array(rad)
    n = len(A)

    if len(RC) >= n:
        print('something has gone wrong')
        raise RuntimeError(
            "The data has less points than the selected radius!")

    A_sub, RC_sub = generate_sub_matrices(A, rad, RC, n)

    D = generate_diff_matrix(A_sub, RC_sub)

    return D


def semi_circle_array(rad):
    """Generate an array of length 2r+1 with values corresponding to points on a semi circle"""
    RC = array([sqrt(rad ** 2 - (i - rad) ** 2) for i in range(2 * rad + 1)])
    return RC


def generate_sub_matrices(A, rad, RC, n):
    """
    Generate the sub matrices used in RCF routine
    :param A: Data matrix, length n
    :param rad: radius of RCF filter
    :param RC: np array of length 2r+1 with
    :param n: integer describing length of A
    :return: A_sub, RC_sub, lists of same dimensions, sampled according to paper: https://doi.org/10.1366%2F12-06766
    """
    ni = n
    A_sub = []
    RC_sub = []

    for i in range(len(A)):  # vectorise this when you can be bothered
        if i < (rad + 1):
            a_sub = A[:(i + rad + 1)]
            rc_sub = RC[(rad - i):(2 * rad + 1)]
            A_sub.append(a_sub)
            RC_sub.append(rc_sub)

        elif (rad + 1) <= i <= (n - (rad + 1)):
            a_sub = A[(i - rad):(i + rad + 1)]
            rc_sub = RC
            A_sub.append(a_sub)
            RC_sub.append(rc_sub)

        elif i > (n - (rad + 1)):
            a_sub = A[(i - rad):(n + 1)]
            rc_sub = RC[:(rad + (n - i))]
            A_sub.append(a_sub)
            RC_sub.append(rc_sub)

        else:
            print('something has gone wrong')
            raise RuntimeError("Something has gone wrong and I don't know why")

    return A_sub, RC_sub


def generate_diff_matrix(A_sub, RC_sub):
    """
    Generate a difference matrix, which will be len(A_sub)=len(RC_sub). Each element will be the minimum of matrix
    formed by the difference of AC_sub_i and RC_sub_i at each i (element).
    :param A_sub: List of np arrays
    :param RC_sub: List of np arrays
    :return: D, Difference matrix of shape (len(A_sub),), elements as described above
    """
    D = []
    for i in range(len(A_sub)):
        diff = A_sub[i] - RC_sub[i]
        D.append(min(diff))

    D = array(D)
    return D


def smooth(L, window_length, polyorder):
    """
    Savgol filter applied to data
    :param L: the data to be smoothed
    :param window_length: positive odd integer
    :param polyorder: must be less than window length
    :return:
    """

    return savgol_filter(L, window_length, polyorder, mode='mirror')


def user_guided_scarf(
        x_data,
        bg,
        data_bg_rm_y,
        params=[],
        rad=70,
        window_length=51,
        poly_order=3,
        L_sg=0):
    while True:
        # rcf step
        while True:
            try:
                D = rcf(data_bg_rm_y, rad)
                fig, ax = plt.subplots()
                ax.plot(x_data, D)
                ax.plot(x_data, data_bg_rm_y)
                print(
                    f"SCARF background removal requires user input. Please look at the following bg with rad={rad}")
                plt.show(block=True)
                ans = input(
                    "If you are happy with the plot, type y. if not then please type a new rad")
                if ans == 'y':
                    break
                else:
                    try:
                        rad = int(ans)
                    except ValueError:
                        print("You entered an incorrect answer! Trying again...")
            except RuntimeError:
                print(
                    f"Please enter a smaller radius, the radius must be less than half the number of data points:"
                    f" {len(data_bg_rm_y)//2}")
                rad = 70

        # then apply SG filter to D
        while True:
            try:
                L_sg = smooth(D, window_length, poly_order)
                fig, ax = plt.subplots()
                ax.plot(x_data, L_sg)
                ax.plot(x_data, data_bg_rm_y)
                print(
                    f"Please look at the following bg with Sg filter parameters (window length, polynomial order): "
                    f"{window_length}, {poly_order}")
                plt.show(block=True)
            except ValueError as e:
                print(
                    "Incorrect values for window_length and poly_order have been entered. Poly order must be less "
                    "than window length and window length must be odd")
            ans = input(
                "please enter y if you are happy with these values, or enter two integers with a space "
                "for window_length and poly_order")
            if ans == 'y':
                L = L_sg
                break
            else:
                try:
                    ans = ans.split(' ')
                    if len(ans) != 2:
                        raise ValueError(
                            "The tuple was more than two elements long")
                    window_length = int(ans[0])
                    poly_order = int(ans[1])
                except ValueError:
                    print("You entered an incorrect answer! Trying again...")

        # get the bg shift up automatically
        # whats the smallest difference between D and b? shift it up by that
        b = min(data_bg_rm_y - L)
        L = L + b

        # final question before exiting
        fig, ax = plt.subplots()
        ax.plot(x_data, L)
        ax.plot(x_data, data_bg_rm_y)
        ax.plot(x_data, data_bg_rm_y - L, 'b--')
        print(f"Please look at the following bg with selected parameters")
        plt.show(block=True)
        ans = input(
            "Are you happy with this bg? If yes, type y, else type n. n will restart the fitting. \n"
            "Typing repeat will add an additional bg subtraction to this one ")
        if ans == 'y':
            bg += L
            data_bg_rm_y -= L
            params.append({'rad': rad,
                           'b': b,
                           'window_length': window_length,
                           'poly_order': poly_order})
            break
        elif ans == 'n':
            pass
        elif ans == 'repeat':
            bg += L
            data_bg_rm_y -= L  # remove the bg found here from the original data and go again
            print(
                "apply two bg removal steps, this will mean the background just specified will be removed "
                "from the data")
            params.append({'rad': rad,
                           'b': b,
                           'window_length': window_length,
                           'poly_order': poly_order})
        else:
            print(
                "You entered an incorrect answer! Trying whole fitting routine again...")
    return data_bg_rm_y, bg, params


def scarf_from_dict(y_data, bg, data_bg_rm_y, scarf_params, params):
    rad, window_length, poly_order = \
        scarf_params['rad'], scarf_params['window_length'], scarf_params['poly_order']
    D = rcf(data_bg_rm_y, rad)
    L = smooth(D, window_length, poly_order)
    try:
        b = scarf_params['b']  # if passed then use it
    except KeyError:  # otherwise find it
        # whats the smallest difference between D and b? shift it up by that
        b = min(y_data - L)
    L = L + b
    bg += L
    data_bg_rm_y -= L
    params.append({'rad': rad,
                   'b': b,
                   'window_length': window_length,
                   'poly_order': poly_order})

    return data_bg_rm_y, bg, params


def perform_scarf(x_data, y_data, scarf_params=False):
    """
    Routine to perform the scarf background subtraction. decides whether to run a user guided routine or anything else
    depending on the input for scarf_params
    :param x_data: the x data as an np array
    :param y_data: the y data as an np array
    :param scarf_params: can be one of bool, dict or list of dicts.
    :return:
    """
    logging.debug('performing scarf bg subtraction')

    bg = array([0 for _ in y_data], dtype=float64)  # initialise
    data_bg_rm_y = y_data.copy()
    params = []

    if isinstance(scarf_params, bool) and not scarf_params:
        logging.debug('setting scarf parameters via user guided method')
        data_bg_rm_y, bg, params = user_guided_scarf(x_data, bg, data_bg_rm_y)

    elif isinstance(scarf_params, bool):
        # the user has passed True! recall this function and change it to false
        logging.warning(
            'scarf has been passed the True bool value for scarf params. This is invalid, assuming you meant '
            'False as no parameters were specified.')
        data_bg_rm_y, bg, params_ = perform_scarf(
            x_data, data_bg_rm_y, scarf_params=False)
        params += params_  # params_ is a list of one dictionary
        return data_bg_rm_y, bg, params

    elif isinstance(scarf_params, dict):
        logging.debug('using scarf params: {scarf_params}')
        data_bg_rm_y, bg, params = scarf_from_dict(
            y_data, bg, data_bg_rm_y, scarf_params, params)

    elif isinstance(scarf_params, list):
        logging.debug(f'using scarf params: {scarf_params}')
        # the user wants multiple runs. call the function for each set of
        # params, passing the new y data each time
        for param_dict in scarf_params:
            data_bg_rm_y, bg_, params_ = perform_scarf(
                x_data, data_bg_rm_y, scarf_params=param_dict)
            bg += bg_
            params += params_  # params_ is a list of a dictionary so use += here

    else:
        logging.warning(
            'an unexpected parameter has been passed as a scarf value, running interactively.')
        data_bg_rm_y, bg, params_ = perform_scarf(
            x_data, data_bg_rm_y, scarf_params=False)
        params += params_
        return data_bg_rm_y, bg, params

    plt.close()
    logging.debug('scarf bg parameters are: {params}')
    return data_bg_rm_y, bg, params
