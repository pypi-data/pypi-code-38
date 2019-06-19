"""thunderfit.__main__: executed when thunderfit directory is called as script."""
"""from .thundobj import main
import utilities as utili

import argparse
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
import time
import os


parser = argparse.ArgumentParser(
    description='fit peaks and background to the given data given a set of parameter'
)
parser.add_argument('--param_file_path', type=str, default='./params.txt',
                    help='input filepath to param file, if you want to use it')
parser.add_argument('--x_label', type=str, default='x_axis',
                    help='the label for independent variables')
parser.add_argument('--y_label', type=str, default='y_axis',
                    help='the label for dependent variables')
parser.add_argument('--e_label', type=str, default='y_error',
                    help='the label for uncertainties in y')
parser.add_argument('--x_ind', type=int, default=0,
                    help='the column in data which is the independent data')
parser.add_argument('--y_ind', type=int, default=1,
                    help='the column in data which is the dependent data')
parser.add_argument('--e_ind', type=Union[int, None], default=None,
                    help='the column in data which is the independent data uncertainties')
parser.add_argument('--datapath', type=str, default='./data.txt',
                    help='relative path to the datafile from where python script is called')
parser.add_argument('--user_params', type=Dict, default={'yfit': None, 'background': None, 'peak_types': [],
                        'peak_centres': [], 'peak_widths':[], 'peak_amps': [], 'chisq': None, 'free_params': None,
                                                      'p_value':None, 'tightness':None},
                    help='the fit data as specified in the Thunder __init__')
args = parser.parse_args()  # this allows us to now use them all

if args.param_file_path: # if there is a params file then use it
    LOGGER.info('Using params file')
    arguments = utili.parse_param_file(args.param_file_path) # parse it
else:
    print('not using params file')
    arguments = utili.parse_args(args) # else use argparse but put in dictionary form

curr_time = time.localtime(time.time())
dirname = utili.make_dir(f'analysed_{curr_time}')  # make a dict for the processed data to be saved in

thunder = main(arguments)

# save a plot of the figure and the thunder object
dataname = os.path.basename(arguments['datapath'])
utili.save_plot(thunder.plot, path=dirname, figname=f"{dataname}.svg")
utili.save_thunder(thunder, path=dirname, filename=f"{dataname}.p")
utili.save_fit_report(thunder.fit_data, path=dirname, filename=f"{dataname}_report.json")"""