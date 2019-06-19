import numpy as np
import astropy.stats
import logging
import bpm.image_utils as image_utils

logger = logging.getLogger('lco-bpm-maker')

def process_bias_frames(bias_frames, mask_threshold=10):
    """
    Create bad pixel mask from bias frames.

    :param bias_frames: List of bias frames to be processed
    :param mask_threshold: Number of standard deviations from the median of the combined bias image
    for a pixel to be flagged as bad. (default 10)
    """
    logger.info("Processing {num_frames} bias frames".format(num_frames=len(bias_frames)))
    corrected_frames = []

    for frame in bias_frames:
        image_data = np.float32(frame.data)
        image_data -= np.median(image_data)
        corrected_frames.append(image_data)

    return image_utils.mask_outliers(np.dstack(corrected_frames), mask_threshold)


def process_dark_frames(dark_frames, dark_current_threshold=35, bias_level=None):
    """
    Create bad pixel mask from dark frames.

    :param dark_frames: List of bias frames to be processed
    :param dark_current_threshold: Threshold for pixel dark current when flagging
    bad pixels in dark frames. Pixels above this will be flagged. (default 20 (electrons/second))
    :param bias_level: Bias level for camera (default None)
    If bias_level is None: camera has an overscan region, and bias level will be determined from dark frames
    """
    logger.info("Processing {num_frames} dark frames".format(num_frames=len(dark_frames)))
    corrected_frames = []

    for frame in dark_frames:
        image_data = np.float32(frame.data)
        if bias_level is None:
            overscan_section = image_utils.get_slices_from_header_section(frame.header['BIASSEC'])
            bias_level = np.median(image_data[overscan_section])

        image_data -= bias_level
        image_data /= np.float32(frame.header['EXPTIME'])

        gain = frame.header.get('GAIN')

        if gain == 0:
            logger.error("GAIN value from FITS header is 0! Skipping image. [{origname}]".format(origname=frame.header['ORIGNAME']))
            continue
        elif gain == None:
            logger.error("GAIN keyword not present in FITS header. Skipping image. [{origname}]".format(origname=frame.header['ORIGNAME']))
            continue

        image_data /= np.float32(gain)

        corrected_frames.append(image_data)

    return np.uint8(np.median(np.dstack(corrected_frames), axis=2) > dark_current_threshold)


def process_flat_frames(flat_frames, mask_threshold=10, bias_level=None):
    """
    Create bad pixel mask from flat frames.

    :param flat_frames: List of flat frames to be processed
    :param mask_threshold: Number of standard deviations from the median of the combined flat image for a
    pixel to be flagged as bad. (default 10)
    :param bias_level: Bias level for camera (default None)
    If bias_level is None: camera has an overscan region, and bias level will be determined from flat frames
    """
    logger.info("Processing {num_frames} flat frames taken with filter: {filter}".format(num_frames=len(flat_frames),
                                                                                         filter=flat_frames[0].header['FILTER']))
    corrected_frames = []

    for frame in flat_frames:
        image_data = np.float32(frame.data)
        if bias_level is None:
            overscan_section = image_utils.get_slices_from_header_section(frame.header['BIASSEC'])
            bias_level = np.median(image_data[overscan_section])

        image_data -= bias_level
        image_data /= np.median(image_data)

        corrected_frames.append(image_data)

    return image_utils.mask_outliers(np.dstack(corrected_frames), mask_threshold)

def get_bias_level_from_frames(bias_frames):
    """
    Determine camera bias level from a set of bias frames

    :param bias_frames: list of bias frames
    """
    return np.median([np.median(frame.data) for frame in bias_frames])
