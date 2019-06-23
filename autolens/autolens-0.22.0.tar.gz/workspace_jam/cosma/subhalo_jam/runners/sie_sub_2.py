from autofit.tools import path_util
from autofit import conf
import sys

from autolens.data import ccd
from autolens.data.array import mask as msk

import os

# Given your username is where your data is stored, you'll need to put your cosma username here.
cosma_username = 'pdtw24'
cosma_path = '/cosma7/data/dp004/dc-nigh1/autolens/'

data_type = 'subhalo_jam'

cosma_data_path = path_util.make_and_return_path_from_path_and_folder_names(cosma_path,
                                                                            folder_names=['data', data_type])
cosma_output_path = path_util.make_and_return_path_from_path_and_folder_names(cosma_path,
                                                                              folder_names=['output', data_type])

workspace_path = '{}/../../../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path, and override the output path with the Cosma path.
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=cosma_output_path)

# The fifth line of this batch script - '#SBATCH --array=1-17' is what species this. Its telling Cosma we're going to
# run 17 jobs, and the id's of those jobs will be numbered from 1 to 17. Infact, these ids are passed to this runner,
# and we'll use them to ensure that each jobs loads a different image. Lets get the cosma array id for our job.
cosma_array_id = int(sys.argv[1])

### Subhalo challenge data strings ###

if cosma_array_id == 1:
    pixel_scale = 0.05
    data_name = 'large_rein'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 2:
    pixel_scale = 0.04
    data_name = 'large_rein'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 3:
    pixel_scale = 0.03
    data_name = 'large_rein'
    resized_ccd_shape = (500, 500)
elif cosma_array_id == 4:
    pixel_scale = 0.02
    data_name = 'large_rein'
    resized_ccd_shape = (700, 700)
elif cosma_array_id == 5:
    pixel_scale = 0.01
    data_name = 'large_rein'
    resized_ccd_shape = (1024, 1024)
elif cosma_array_id == 6:
    pixel_scale = 0.05
    data_name = 'small_rein'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 7:
    pixel_scale = 0.04
    data_name = 'small_rein'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 8:
    pixel_scale = 0.03
    data_name = 'small_rein'
    resized_ccd_shape = (500, 500)
elif cosma_array_id == 9:
    pixel_scale = 0.02
    data_name = 'small_rein'
    resized_ccd_shape = (700, 700)
elif cosma_array_id == 10:
    pixel_scale = 0.01
    data_name = 'small_rein'
    resized_ccd_shape = (1024, 1024)
elif cosma_array_id == 11:
    pixel_scale = 0.05
    data_name = 'large_rein_no_sub'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 12:
    pixel_scale = 0.04
    data_name = 'large_rein_no_sub'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 13:
    pixel_scale = 0.03
    data_name = 'large_rein_no_sub'
    resized_ccd_shape = (500, 500)
elif cosma_array_id == 14:
    pixel_scale = 0.02
    data_name = 'large_rein_no_sub'
    resized_ccd_shape = (700, 700)
elif cosma_array_id == 15:
    pixel_scale = 0.01
    data_name = 'large_rein_no_sub'
    resized_ccd_shape = (1024, 1024)
elif cosma_array_id == 16:
    pixel_scale = 0.05
    data_name = 'small_rein_no_sub'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 17:
    pixel_scale = 0.04
    data_name = 'small_rein_no_sub'
    resized_ccd_shape = (400, 400)
elif cosma_array_id == 18:
    pixel_scale = 0.03
    data_name = 'small_rein_no_sub'
    resized_ccd_shape = (500, 500)
elif cosma_array_id == 19:
    pixel_scale = 0.02
    data_name = 'small_rein_no_sub'
    resized_ccd_shape = (700, 700)
elif cosma_array_id == 20:
    pixel_scale = 0.01
    data_name = 'small_rein_no_sub'
    resized_ccd_shape = (1024, 1024)

sub_grid_size = 2

data_values = 'pixel_scale_' + str(pixel_scale) + '_sub_grid_' + str(sub_grid_size)

data_path = path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_path, folder_names=['data', data_type, data_name, data_values])

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'image.fits',
                                       psf_path=data_path + 'psf.fits',
                                       noise_map_path=data_path + 'noise_map.fits',
                                       resized_ccd_shape=resized_ccd_shape,
                                       pixel_scale=pixel_scale, resized_psf_shape=(15, 15))

mask = msk.load_mask_from_fits(mask_path=data_path + 'mask_irregular.fits', pixel_scale=pixel_scale)
mask = mask.resized_scaled_array_from_array(new_shape=resized_ccd_shape)

positions = ccd.load_positions(positions_path=data_path + 'positions.dat')

from workspace_jam.pipelines.no_lens_light.initializer import lens_sie_shear_source_sersic
from workspace_jam.pipelines.no_lens_light.subhalo.from_initializer import lens_sie_shear_subhalo_source_sersic

pipeline_initializer = lens_sie_shear_source_sersic.make_pipeline(phase_folders=[data_name, data_values])
pipeline_subhalo = lens_sie_shear_subhalo_source_sersic.make_pipeline(phase_folders=[data_name, data_values])

pipeline = pipeline_initializer + pipeline_subhalo

pipeline.run(data=ccd_data, mask=mask)