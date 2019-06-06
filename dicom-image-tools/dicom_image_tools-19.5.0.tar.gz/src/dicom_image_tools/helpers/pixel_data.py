import logging
import numpy as np
from pydicom import Dataset


log = logging.getLogger(__name__)


def get_pixel_array(dcm: Dataset) -> np.ndarray:
    """ Take a DICOM dataset, extract the pixels, rescale the values according to metadata. Return the extracted image
    as a numpy ndarray of int16 values

    Args:
        dcm: The DICOM dataset from which the image should be extracted

    Returns:
        Extracted image as a numpy ndarray of int16 numbers

    """
    px = dcm.pixel_array.astype(np.int16)
    if 'RescaleSlope' in dcm:
        log.debug('Rescaling slope of pixel array')
        px *= np.int16(dcm.RescaleSlope)
    if 'RescaleIntercept' in dcm:
        log.debug('Rescaling intercept of pixel array')
        px += np.int16(dcm.RescaleIntercept)

    return px
