import astropy.io.fits as fits
import os
import shutil
import datetime
import tempfile
import glob
import logging
import lcogt_logging
import argparse
import bpm.image_processing as image_processing
import numpy as np
import bpm.image_utils as image_utils

logger = logging.getLogger('lco-bpm-maker')

def setup_logging(log_level):
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(lcogt_logging.LCOGTFormatter())
    logger.addHandler(handler)


def parse_args():
    parser = argparse.ArgumentParser(description='Create a bad pixel mask from a set of calibration frames.')
    parser.add_argument('input_directory', help='Input directory of calibration images')
    parser.add_argument('output_directory', help='Output directory for bad pixel mask')
    parser.add_argument('--log-level', dest='log_level', default='INFO', help='Logging level to be displayed',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--dark-current-threshold', dest='dark_current_threshold',
                        help='Threshold for pixel dark current when flagging bad pixels in dark frames. Pixels above this will be flagged. Default = 35 [electrons/second]',
                        default=20)
    parser.add_argument('--flat-sigma-threshold', dest='flat_sigma_threshold',
                        help='Number of standard deviations from the median of the combined flat image for a pixel to be flagged as bad. Default = 10',
                        default=10)
    parser.add_argument('--bias-sigma-threshold', dest='bias_sigma_threshold',
                        help='Number of standard deviations from the median of the combined bias image for a pixel to be flagged as bad. Default = 10',
                        default=10)
    parser.add_argument('--fpack', dest='fpack_flag', action='store_true', help='Flag to fpack output BPM')

    args = parser.parse_args()

    return args


def generate_bpm():
    args = parse_args()
    setup_logging(getattr(logging, args.log_level))

    calibration_frames = get_calibration_frames(os.path.normpath(args.input_directory) + '/*.fits*')

    if calibration_frames:
        if len(set([frame[0].header['INSTRUME'] for frame in calibration_frames])) != 1:
            raise RuntimeError("Got calibration frames from more than one camera. Aborting.")

        process_frames(calibration_frames, args)
    else:
        raise RuntimeError("No calibration frames could be found. Check that the directory contains calibration frames.")


def process_frames(frames, command_line_args):
    """
    Process a set of calibration frames into bad pixel mask(s).
    """
    logger.info("Processing {num_frames} calibration frames.".format(num_frames=len(frames)))

    #use the first frame to determine the structure of all frames
    reference_hdu_list = frames[0]

    #Update all extensions with required header values for image processing methods
    header_keywords_to_update = ['OBSTYPE', 'EXPTIME', 'FILTER', 'CCDSUM', 'ORIGNAME']
    for keyword in header_keywords_to_update:
        image_utils.apply_header_value_to_all_extensions(frames, keyword)

    #retrieve all image extensions - any extension containing image data
    image_extensions = []
    for frame in frames:
        image_extensions.extend(image_utils.get_image_extensions(frame))

    #check camera for overscan region
    camera_has_no_overscan = True
    try:
        bias_section = image_utils.get_slices_from_header_section(image_extensions[0].header['BIASSEC'])
        camera_has_no_overscan = False
    except:
        logger.warn("Couldn't parse BIASSEC keyword. Using bias frames to determine camera bias level.")

    # sort frames by binning
    frames_sorted_by_binning = image_utils.sort_frames_by_header_values(image_extensions, 'CCDSUM')

    for binning in frames_sorted_by_binning.keys():
        frames_sorted_by_extver = image_utils.sort_frames_by_header_values(frames_sorted_by_binning[binning],
                                                                           'EXTVER')
        masks = []
        for extnum, extver in enumerate(frames_sorted_by_extver.keys()):
            combined_mask = create_final_mask(frames_sorted_by_extver[extver],
                                              command_line_args,
                                              camera_has_no_overscan)

            masks.append(combined_mask)
            logger.info("Created BPM for extension {extension_number}.".format(extension_number=extnum))


        mask_stack = np.dstack(masks)
        reference_hdu_list[0].header.update({'DATE_OBS': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                                             'CCDSUM': binning,
                                             'OBSTYPE': 'BPM'})

        #Update all extensions' EXTNAME to BPM for BANZAI compatibility.
        for hdu in reference_hdu_list:
            hdu.header.update({'EXTNAME': 'BPM'})

        write_bpm_to_file(mask_stack, command_line_args.output_directory, command_line_args.fpack_flag, reference_hdu_list)


def write_bpm_to_file(masks, output_directory, fpack, reference_hdu_list):
    """
    Write output BPM to file.
    """
    primary_header = reference_hdu_list[0].header
    today_date = datetime.datetime.utcnow().strftime("%Y%m%d")
    output_filename = "{site}{telescope}-{instrument}-{today}-bpm-{readout_mode}.fits".format(site=primary_header['SITEID'],
                                                                                             telescope=primary_header['TELESCOP'].replace("-", ""),
                                                                                             instrument=primary_header['INSTRUME'],
                                                                                             today=today_date,
                                                                                             readout_mode=primary_header['CONFMODE'])

    if len(reference_hdu_list) == 1:
        output_bpm = fits.HDUList([fits.PrimaryHDU(header=primary_header, data=masks[:,:,0])])
    else:
        output_bpm = fits.HDUList([fits.PrimaryHDU(header=primary_header)])
        for ext_num in range(1, len(reference_hdu_list)):
            bpm_data = masks[:,:,ext_num-1]
            hdu = fits.ImageHDU(header=reference_hdu_list[ext_num].header,
                                data=bpm_data)
            hdu.header['OBSTYPE'] = 'BPM'
            hdu.header['EXTVER'] = ext_num
            output_bpm.append(hdu)

    with tempfile.TemporaryDirectory() as temp_dir:
        output_bpm.writeto(os.path.join(temp_dir, output_filename), overwrite=True, output_verify='fix+warn')
        if fpack:
            command = 'fpack -q 64 {temp_dir}/{basename}'
            os.system(command.format(temp_dir=temp_dir, basename=output_filename))
            output_filename += '.fz'
        shutil.move(os.path.join(temp_dir, output_filename), output_directory)

    logger.info("Finished processing. BPM written to {file_path}".format(file_path=output_filename))


def create_final_mask(frames, command_line_args, camera_has_no_overscan=True):
    """
    From a set of calibration frames, create a final bad pixel mask.
    """
    bias_level = image_processing.get_bias_level_from_frames(get_frames_of_type(frames, 'BIAS')) if camera_has_no_overscan else None

    dark_mask = image_processing.process_dark_frames(get_frames_of_type(frames, 'DARK'),
                                                     int(command_line_args.dark_current_threshold),
                                                     bias_level)
    bias_mask = image_processing.process_bias_frames(get_frames_of_type(frames, 'BIAS'),
                                                     int(command_line_args.bias_sigma_threshold))

    flats_sorted = image_utils.sort_frames_by_header_values((get_frames_of_type(frames, 'FLAT')), 'FILTER')
    flat_masks = [image_processing.process_flat_frames(flats_sorted[filter],
                                                       int(command_line_args.flat_sigma_threshold),
                                                       bias_level)
                  for filter in flats_sorted.keys()]

    flat_masks.extend([bias_mask, dark_mask])
    combined_mask = np.sum(np.dstack(flat_masks), axis=2) > 0

    return np.uint8(combined_mask)


def get_calibration_frames(path_to_frames, calibration_types=['d00', 'f00', 'b00']):
    """
    Given a directory of fits files, return a list of calibration frames
    """
    frames = glob.glob(path_to_frames)
    frames = [image_utils.open_fits_file(frame) for frame in frames if any(obs_type in frame for obs_type in calibration_types)]
    return frames


def get_frames_of_type(frames, observation_type):
    """
    Takes in a list of frames, and returns frames which match the observation
    type provided.
    """
    return [frame for frame in frames if observation_type in frame.header['OBSTYPE']]
