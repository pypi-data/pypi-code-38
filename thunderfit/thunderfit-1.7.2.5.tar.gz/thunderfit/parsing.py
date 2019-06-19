import logging
from argparse import ArgumentParser
from os.path import basename
from time import strftime
from typing import Union, Dict, List

from numpy import array

from . import utilities as utili


def str_or_none(value):
    """
    a type function to check if a value cN be either a string or nonr
    :param value:
    :return:
    """
    try:
        return str(value)
    except BaseException:
        return None


def str_or_arr(value):
    """
    an incomplete function to do type checking for string or np array..needs to try array(value)!
    :param value:
    :return:
    """
    try:
        return str(value)
    except BaseException:
        return array(value)  # does this work?


def parse_user_args():
    """
    a function to parse user arguments using argparse
    :return:
    """
    logging.debug('parsing command line args')

    parser = ArgumentParser(
        description='fit peaks and background to the given data given a set of parameter')
    parser.add_argument(
        '--param_file_path',
        type=str_or_none,
        default=None,
        help='input filepath to param file, if you want to use it')
    parser.add_argument(
        '--datapath',
        type=str_or_none,
        default=None,
        help='relative path to the datafile from where python script is called')
    parser.add_argument(
        '--x_ind',
        type=str_or_none,
        default=None,
        help='the column in data which is the independent data')
    parser.add_argument('--y_ind', type=str_or_none, default=None,
                        help='the column in data which is the dependent data')
    parser.add_argument('--e_ind',
                        type=Union[int,
                                   None],
                        default=None,
                        help='NOT IMPLEMENTED YET. the column in data which is the independent data uncertainties')
    parser.add_argument(
        '--no_peaks',
        type=int,
        default=None,
        help='the number of peaks you would like fitted. If you have specified bounds or peak infomation'
        '\n e.g. centres then please make sure this is the same length as that list')
    parser.add_argument(
        '--background',
        type=str_or_arr,
        default="SCARF",
        help="The stype of background you'd like to fit. 'SCARF' is a rolling ball solgay_filter "
        "background subtraction. \n 'OLD' uses a soon-to-be not implemented numerical method"
        "which doesn't work too well. \n 'no' specifies that you would like no background fitted."
        "NOT IMPLEMENTED YET: An np array of background can also be passed by passing the path to "
        "the file, but please note that it must be the same length as the datafile (once rows "
        "containing nan values have been removed).")
    parser.add_argument('--scarf_params',
                        type=Union[None,
                                   Dict],
                        default=None,
                        help='a dictionary (or None) of parameters for scarf algorithm. If none an interactive routine'
                        'will be used. if the dictionary is specified it should be of the form: \n'
                        '{"rad":70, "b":90, "window_length":51, "poly_order":3}'
                        '\n where window length must be odd and greater than poly_order, and all must be integers')
    parser.add_argument('--peak_info_dict',
                        type=Union[None,
                                   List],
                        default=None,
                        help='a dictionary of peak information'
                        't')
    parser.add_argument('--bounds',
                        type=Union[None,
                                   Dict],
                        default=None,
                        help='a dictionary of the bounds for peak values. if none passed then will be auto-generated.'
                        '\n of the form: {"centers":[(365, 390), (283,285)],"widths":[(2, 3), (1, 4)],'
                        '"amps":[(2, 3), (1, 4)]}'
                        '\n the list elements correspond to the peaks supplied earlier, the tuple elements'
                        'correspond to the low and high bounds on that specific value')
    parser.add_argument(
        '--normalise',
        type=bool,
        default=False,
        help='bool, True or False for should I normalise data or not')
    parser.add_argument('--mapscan', type=bool, default=False,
                        help='bool, True or False is this a mapscan?')
    parser.add_argument('--method', type=str, default='leastsq',
                        help='which minimisation algorithm to use')
    parser.add_argument('--tol', type=float, default=0.0000001,
                        help='tolerance when fitting')
    parser.add_argument(
        '--amp_bounds',
        type=bool,
        default=False,
        help='whether to create bounds for the amplitude or not')

    args = parser.parse_args()  # this allows us to now use them all

    return args


def using_user_args(args):
    """
    user args parsed depending on params file has been passed. if it hasn't then parse command line input,
    if it has then parse that file instead
    :param args: command line input
    :return:
    """
    logging.debug('parsing user args')
    if args.param_file_path:  # if there is a params file then use it
        # logging.warning('Using params file and ignoring all other user inputs from command line')
        arguments = utili.parse_param_file(args.param_file_path)  # parse it
        if args.datapath:
            arguments['datapath'] = args.datapath
    else:
        print('not using params file')
        # else use argparse but put in dictionary form
        arguments = utili.parse_args(args)

    return arguments


def make_user_files(arguments, file_name=None):
    """
    make a directory to store all the user files in. name it with the file_name being analysed and the current time.
    :param arguments: user args. actually only need the datapath element so will change in future
    :param file_name: filename to save should actually be the only argument and basename should maybe be a bool option
    :return: filename used and the dirname created
    """
    logging.debug('making file to store data inside')
    # name directory with the current time
    curr_time = strftime('%d_%m_%Y__%H;%M')
    if not file_name:
        file_name = basename(arguments['datapath'])
    file_name = file_name.split('.')[0]  # the name of the file
    # make a dict for the processed data to be saved in)
    dirname = utili.make_dir(f'{file_name}_analysed_{curr_time}')

    return file_name, dirname
