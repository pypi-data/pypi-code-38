from autofit import conf
from autofit.tools import path_util
from autolens.data import ccd
from autolens.data.array import scaled_array
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import numpy as np
import os

# Setup the path to the workspace, using a relative directory name.
workspace_path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path and output path.
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=workspace_path + 'output')

pixel_scale = 0.00976562
data_type = 'subhalo_challenge_lp'
data_level = 'level_0'
data_name = 'small_hi_sn_system_1'

data_path = path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=['data', data_type, data_level, data_name])

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'image.fits',
                                       psf_path=data_path + 'psf.fits',
                                       noise_map_path=data_path + 'noise_map.fits',
                                       pixel_scale=pixel_scale, resized_ccd_shape=(400, 400))

blurring_psf = ccd.PSF.from_gaussian(shape=(31, 31), pixel_scale=pixel_scale, sigma=50.0)

blurred_image = blurring_psf.convolve(ccd_data.image_2d)
blurred_image = scaled_array.ScaledSquarePixelArray(array=blurred_image, pixel_scale=pixel_scale)
# array_plotters.plot_array(array=blurred_image)
absolute_blurred_signal_to_noise_map = np.abs(blurred_image) / ccd_data.noise_map
absolute_blurred_signal_to_noise_map = scaled_array.ScaledSquarePixelArray(array=absolute_blurred_signal_to_noise_map,
                                                                           pixel_scale=pixel_scale)
# array_plotters.plot_array(array=absolute_blurred_signal_to_noise_map)

mask = np.where(absolute_blurred_signal_to_noise_map > 1.0, False, True)
mask = msk.Mask(array=mask, pixel_scale=pixel_scale)

ccd_plotters.plot_image(ccd_data=ccd_data, mask=mask)