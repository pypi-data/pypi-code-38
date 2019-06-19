import logging
from ast import literal_eval
from os.path import basename
from os import rename
from os.path import join, abspath

from . import map_scan_tools
from . import multi_obj
from . import parsing
from . import utilities as utili


def main():
    """
    the script to run a mapscan analysis for a user based on a parameters file or manually passed args
    :return:
    """

    args = parsing.parse_user_args()

    arguments = parsing.using_user_args(args)

    try:  # a user can pass in a list of filenames or just one
        file_name = basename(literal_eval(arguments['datapath'])[0])
        log_name = file_name
    except (SyntaxError, ValueError):  # assume its just a string and not a list passed
        file_name = arguments['datapath']
        log_name = arguments['datapath']
        arguments['datapath'] = [
            f"{arguments['datapath']}",
        ]  # as this is what multiobj needs

    # setup logger
    log_filename = utili.setup_logger(log_name.split('.')[0]) # don't name it with the .txt

    logging.info('creating multi_obj object')
    bag = multi_obj.main(arguments)  # create a Thunder object

    # get the first thunder object
    bag.first = next(iter((bag.thunder_bag.keys())))

    if (arguments.get('clip_data', False) and not arguments.get('clips', False)) \
            or arguments.get('bg_first_only', False) \
            or arguments.get('peakf_first_only',False) \
            or arguments.get('bounds_first_only', False):  # then we want the user to decide which thunder object to use
        logging.info('choosing spectrum for data')
        # choose which spectrum to base everything off of if user wants to use
        # one spectra to
        bag.choose_spectrum()
        # choose parameters
        logging.info(
            f'using spectra {bag.first} as spectra to set any user variables from')

    # clip the data if weird edges
    if arguments.get('clip_data', False):
        logging.info('clipping data')
        bag.clip_data(arguments.get('clips', False))

    # cosmic ray removal goes here
    if arguments.get('smoothing', False):
        logging.info('smoothing data')
        bag.smoother()

    # remove background
    if arguments.get('bg_first_only', False):
        logging.info(
            'determining background conditions for all based on user guided for first')
        bag.bg_param_setter()
    logging.info('removing background from data for all thunder objects')
    bag.remove_backgrounds()

    # normalisation
    if arguments.get('normalise', False):
        logging.info('normalising data using svn normalisation')
        bag.normalise_data()
        # then shift the values up since normalisation may create negative
        # values
        for thund in bag.thunder_bag.values():
            thund.y_data_bg_rm = thund.y_data_bg_rm - min(thund.y_data_bg_rm)

    # find peaks
    if arguments.get('find_peaks', False):
        logging.info('setting peak information for all thunder objects')
        print("Warning: Finding peaks automatically will overwirte and peak_info_dict supplied")
        logging.info(
            'running user guided routine to determine peak information')
        bag.find_peaks()
    elif arguments.get('adj_params', False):
        logging.info('setting peak information for all thunder objects')
        bag.peaks_adj_params()

    # find bounds
    if arguments.get('find_bounds', False):
        logging.info('finding bounds via user guided routine')
        bag.bound_setter()
    else:
        logging.info(
            "setting all bounds to either user supplied or preset: {'amplitude': False, 'center': False, 'sigma': False}")
        # should really do this in the thunderobj # also don't set as these
        # presets!
        bounds = arguments.get('bounds', {})
        bag.bound_setter(bounds)

    # fit peaks
    logging.info('fitting peaks for all')
    bag.fit_peaks()

    # fit params dictionary
    # store all the peak parameters in a dictionary, so the keys are e.g. sigma, center, amplitude, and the values are
    # dictionaries with keys as the run number with values as lists of values for all the peaks for that run
    # this will for now assume the same types of peak for all fits!
    logging.info('making fit parameters dictionary')
    bag.make_fit_params()

    # fetch stats etc
    logging.info('making stats dictionary')
    bag.get_fit_stats()

    # make directory to save everything in
    file_name, dirname = parsing.make_user_files(arguments, file_name)

    # plot map scan
    logging.info('plotting map scans')
    bag.make_map_matrices()  # make the mapscan arrays
    map_scan_tools.plot_map_scan(
                                getattr( bag,'fit_params'),
                                bag.map_matrices,
                                bag.X_coords,
                                bag.Y_coords,
                                dirname,
                                arguments.get('map_all_params', False)
                                )

    # save a histograms
    if arguments.get('make_hists', False):
        logging.info('creating and saving histograms')
        bag.histograms(bag.map_matrices, path=f'{dirname}', keys=arguments.get('hist_keys', None))


    # save individual plots for each of the failed fits
    logging.info('saving failed fit plots')
    bag.save_failed_plots(dirname)

    # save a gif of every single plot
    if arguments.get('make_gif', False):
        logging.info('saving all plots as gif')
        utili.gif_maker(bag.thunder_bag, f'{dirname}/all_data.gif')

    # save all plots
    if arguments.get('save_all_plots', False):
        logging.info('saving all plots individually')
        bag.save_all_plots(dirname)

    # put here some code for cluster analysis and pca
    logging.info('not currently doing cluster analysis or pca')
    ##########################################################################

    # save the bag object and it reports
    logging.info('saving fit reports on stats and fitting parameters')
    utili.save_fit_report(
                        getattr(bag,'stats'),
                        path=dirname,
                        filename=f"report.json")
    utili.save_fit_report(
                        getattr(bag, 'fit_params'),
                        path=dirname,
                        filename=f"peak_info.json")
    logging.info('saving thunderbag object')
    utili.save_thunder(bag, path=dirname, filename=f"bag_object.d")

    utili.save_fit_report(
                        arguments,
                        path=dirname,
                        filename=f"inpargs.json")

    # move the log file in with all the rest of it
    log_filename_ = str(join(dirname, f'log.log'))
    # use os.rename to move the log file to the final destination
    logging.getLogger().handlers[0].close()
    rename(log_filename, log_filename_)

