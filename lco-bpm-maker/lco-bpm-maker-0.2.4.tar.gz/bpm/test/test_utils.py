import astropy.io.fits as fits
import numpy as np
import bpm.image_processing as image_processing
import bpm.image_utils as image_utils

def generate_test_bias_frame(bad_pixel_locations):
    hdr = fits.Header({'BIASSEC': '[95:100, 1:100]',
                       'TRIMSEC': '[1:94, 1:100]'})

    overscan_slices = image_utils.get_slices_from_header_section(hdr['BIASSEC'])

    bias_frame = np.round(np.random.normal(1000, 50, (100, 100)))
    bias_frame[bad_pixel_locations] = np.random.normal(5000, 3000)
    bias_frame[overscan_slices] = np.round(np.random.normal(1000, 50))

    return fits.ImageHDU(data=bias_frame, header=hdr)

def generate_test_flat_frame(bad_pixel_locations, image_mean, image_std):
    hdr = fits.Header({'FILTER': 'w',
                       'BIASSEC': '[95:100, 1:100]',
                       'TRIMSEC': '[1:94, 1:100]'})

    overscan_slices = image_utils.get_slices_from_header_section(hdr['BIASSEC'])

    flat_frame = np.round(np.random.normal(image_mean, image_std, (100,100)))
    flat_frame[bad_pixel_locations] = np.round(np.random.normal(image_mean, 20*image_std))
    flat_frame[overscan_slices] = np.round(np.random.normal(1000, 50))

    return fits.ImageHDU(data=flat_frame, header=hdr)

def generate_test_dark_frame(bad_pixel_locations):
    hdr = fits.Header({'BIASSEC': '[95:100, 1:100]',
                       'TRIMSEC': '[1:94, 1:100]',
                       'EXPTIME': '10.0',
                       'GAIN': '1.0'})

    dark_frame = np.round(np.random.normal(30, 5, (100,100)))
    dark_frame[bad_pixel_locations] = 1000

    return fits.ImageHDU(data=dark_frame, header=hdr)

def generate_bad_pixel_locations(x_limit, y_limit, num_pixels):
    bad_pixels_y = np.array([np.random.randint(y_limit) for index in range(0, num_pixels)])
    bad_pixels_x = np.array([np.random.randint(x_limit) for index in range(0, num_pixels)])
    bad_pixels = tuple((bad_pixels_y, bad_pixels_x))

    return bad_pixels
