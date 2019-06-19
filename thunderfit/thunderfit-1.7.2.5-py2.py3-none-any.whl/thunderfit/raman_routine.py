import logging
from os import rename
from os.path import join

from . import parsing
from . import peak_finding
from . import peak_fitting
from . import thundobj
from . import utilities as utili
from .background import background_removal as bg_remove


def main():
    """
    script to run analysis on a single raman spectra. may need updating to be more like map_scan
    :return:
    """

    args = parsing.parse_user_args()

    arguments = parsing.using_user_args(args)

    # save a plot of the figure and the thunder object
    file_name = arguments['datapath']
    log_filename = utili.setup_logger(file_name)

    logging.info('creating thunder obj')
    thunder = thundobj.main(arguments)  # create a Thunder object

    # clip data
    if arguments.get('clip_data', False):
        logging.info('clipping data')
        clip_left, clip_right = utili.clip_data(
            getattr(
                thunder, 'x_data'), getattr(
                thunder, 'y_data'), arguments.get(
                'clips', None))
        thunder.x_data, thunder.y_data = thunder.x_data[clip_left:
                                                        clip_right], thunder.y_data[clip_left:clip_right]

    # subtract background
    logging.info('setting and subtracting bg')
    thunder.background, thunder.y_data_bg_rm, _ = bg_remove.background_finder(
        thunder.x_data, thunder.y_data, thunder.background, thunder.scarf_params)
    # determine the background
    # normalise data
    if args.normalise:
        logging.info('normalising data')
        thunder.y_data_bg_rm, thunder.background, thunder.y_data_norm = \
            utili.normalise_all(thunder.y_data_bg_rm, thunder.background, thunder.y_data)

    # find the peaks
    if arguments.get('find_peaks', False):
        logging.info('setting peak info')
        thunder.no_peaks, thunder.peak_info_dict, _ = peak_finding.find_peak_details(
            thunder.x_data, thunder.y_data_bg_rm)  # find peaks/use them if supplied
    # find the bounds
    if arguments.get('find_bounds', False):
        logging.info('finding bounds via user guided routine')
        thunder.bounds = peak_finding.make_bounds(
            thunder.x_data,
            thunder.y_data,
            thunder.no_peaks,
            thunder.peak_info_dict)  # make bounds

    # fit the peaks
    logging.info('fitting peaks')
    thunder.specs, thunder.model, thunder.peak_params, thunder.peaks = peak_fitting.fit_peaks(
        thunder.x_data, thunder.y_data_bg_rm, thunder.peak_info_dict, thunder.bounds, thunder.method, thunder.tol)  # fit peaks

    # save stats etc as object
    logging.info('setting stats etc')
    thunder.chi_sq = thunder.peaks.chisqr  # set the stats from the fits
    reduced_chi_sq = thunder.peaks.redchi
    thunder.free_params = round(thunder.chi_sq / reduced_chi_sq)

    # plot and generate a fit report
    logging.info('plotting and genertaing fit reports')
    thunder.plot_all()  # plot the data in full and save as an object
    thunder.gen_fit_report()  # generate a fit report

    # create a directory to save everything in
    file_name, dirname = parsing.make_user_files(arguments, file_name=None)

    # save everything
    logging.info('saving plots, reports and thund obj')
    utili.save_plot(thunder.plot, path=dirname, figname=f"{file_name}.svg")
    utili.save_thunder(thunder, path=dirname, filename=f"thundobject.d")
    utili.save_fit_report(
        thunder.fit_report,
        path=dirname,
        filename=f"report.json")

    # move the log file in with all the rest of it
    log_filename_ = str(join(dirname, f'{file_name}.log'))
    # use os.rename to move the log file to the final destination
    rename(log_filename, log_filename_)
