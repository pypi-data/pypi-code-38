import numpy as np
import astropy.stats
import astropy.io.fits as fits
import os
import tempfile

def mask_outliers(stacked_frames, mask_threshold=10):
    """
    Mask pixels outside a specified number of standard deviations

    Generate MAD for each pixel - 2D array - pixel_mads
    Generate standard deviation of all pixel MADs - Scalar - std_all_pixels
    Generate median of all pixels MADs - Scalar - median_all_pixels

    Flag any pixels whose std value is outside the median +/- mask_threshold * std_all_pixels

    :param stacked_frames: stack of corrected frames
    :param mask_threshold: standard deviation threshold
    """
    pixel_mads = astropy.stats.median_absolute_deviation(stacked_frames, axis=2)
    std_all_pixels = np.std(pixel_mads)
    median_all_pixels = np.median(pixel_mads)

    outlier_mask = np.logical_or(pixel_mads < median_all_pixels - (mask_threshold * std_all_pixels),
                                 pixel_mads > median_all_pixels + (mask_threshold * std_all_pixels))

    return np.uint8(outlier_mask)


def get_slices_from_header_section(header_section_string):
    """
    Borrowed from BANZAI. Convert FITS header image section value to tuple of slices.

    Example:  '[3100:3135,1:2048]' --> (slice(0, 2048, 1), slice(3099, 3135, 1))
    Note:
    FITS Header image sections are 1-based and indexed by [column, row]
    Numpy arrays are zero-based and indexed by [row, column]

    :param header_string: An image section string in the form "[x1:x2, y1:y2]"
    :return: Row-indexed tuple of slices, (row_slice, col_slice)
    """

    # Strip off the brackets and split the coordinates
    pixel_sections = header_section_string[1:-1].split(',')
    x_slice = split_slice(pixel_sections[0])
    y_slice = split_slice(pixel_sections[1])
    pixel_slices = (y_slice, x_slice)
    return pixel_slices


def split_slice(pixel_section):
    """
    Borrowed from BANZAI. Convert FITS header pixel section to Numpy-friendly
    slice.

    Example: '3100:3135' --> slice(3099, 3135, 1)
    """
    pixels = pixel_section.split(':')
    if int(pixels[1]) > int(pixels[0]):
        pixel_slice = slice(int(pixels[0]) - 1, int(pixels[1]), 1)
    else:
        if int(pixels[1]) == 1:
            pixel_slice = slice(int(pixels[0]) - 1, None, -1)
        else:
            pixel_slice = slice(int(pixels[0]) - 1, int(pixels[1]) - 2, -1)
    return pixel_slice

def get_image_extensions(fits_hdulist, name='SCI'):
    """
    Get a list of the image extensions for a FITS file.

    For multi-extension FITS, this will return an HDUList of all SCI extensions.

    For single-extension FITS with the image on the PrimaryHDU, this will simply return
    an HDUList with a that single HDU.
    """
    extension_info = fits_hdulist.info(False)
    image_extensions = [fits_hdulist[ext[0]] for ext in extension_info if ext[1] == name]
    if not image_extensions:
        return fits_hdulist
    else:
        return fits.HDUList(image_extensions)


def apply_header_value_to_all_extensions(frames, header_keyword):
    """
    Apply a header value from an image's PrimaryHDU to its
    extensions.
    """
    for frame in frames:
        header_value = frame[0].header[header_keyword]
        for extension_num in range(1, len(frame)):
            frame[extension_num].header[header_keyword] = header_value


def sort_frames_by_header_values(frames, header_keyword):
    """
    Given a set of frames and a header keyword, sort the frames by the corresponding
    header values into a form:
    {header_value:[frames_with_header_value]}
    """
    header_values = set([frame.header.get(header_keyword) for frame in frames])
    return {value: [frame for frame in frames if frame.header.get(header_keyword) == value]
                    for value in header_values}


def open_fits_file(filename):
    """
    Load a fits file
    Parameters
    ----------
    filename: str
              File name/path to open
    Returns
    -------
    hdulist: astropy.io.fits
    Notes
    -----
    This is a wrapper to astropy.io.fits.open but funpacks the file first.
    """
    base_filename, file_extension = os.path.splitext(os.path.basename(filename))
    if file_extension == '.fz':
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_filename = os.path.join(tmpdirname, base_filename)
            os.system('funpack -O {0} {1}'.format(output_filename, filename))
            hdulist = fits.open(output_filename, 'readonly')
    else:
        hdulist = fits.open(filename, 'readonly')

    return hdulist
