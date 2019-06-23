from autofit.tools import path_util
from autofit import conf
import sys

from autolens.data import ccd
from autolens.data.array import mask as msk

import os

# Given your username is where your data is stored, you'll need to put your cosma username here.
cosma_username = 'pdtw24'
cosma_path = '/cosma7/data/dp004/dc-nigh1/autolens/'

data_folder = 'subhalo_challenge'

cosma_data_path = path_util.make_and_return_path_from_path_and_folder_names(cosma_path,
                                                                            folder_names=['data', data_folder])
cosma_output_path = path_util.make_and_return_path_from_path_and_folder_names(cosma_path,
                                                                            folder_names=['output', data_folder])

workspace_path = '{}/../../../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path, and override the output path with the Cosma path.
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=cosma_output_path)

# The fifth line of this batch script - '#SBATCH --array=1-17' is what species this. Its telling Cosma we're going to
# run 17 jobs, and the id's of those jobs will be numbered from 1 to 17. Infact, these ids are passed to this runner,
# and we'll use them to ensure that each jobs loads a different image. Lets get the cosma array id for our job.
# cosma_array_id = int(sys.argv[1])
# data_level = str(sys.argv[2])
# data_name = str(sys.argv[3])

data_type = 'noise_10'
data_level = 'level_0'
data_name = 'small_hi_sn_system_1'

pixel_scale = 0.00976562

resized_ccd_shape = (320, 320)

data_path = path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_data_path, folder_names=[data_type, data_level, data_name])

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'image.fits',
                                       psf_path=data_path + 'psf.fits',
                                       noise_map_path=data_path + 'noise_map.fits',
                                       pixel_scale=pixel_scale, resized_ccd_shape=resized_ccd_shape)

mask = msk.load_mask_from_fits(mask_path=data_path + 'mask_irregular.fits', pixel_scale=pixel_scale)
mask = mask.resized_scaled_array_from_array(new_shape=resized_ccd_shape)

from workspace_jam.pipelines.no_lens_light.initialize import lens_sie_shear_source_sersic
from workspace_jam.pipelines.no_lens_light.power_law.from_initialize import lens_pl_shear_source_sersic
from workspace_jam.pipelines.no_lens_light.subhalo.from_power_law import lens_pl_shear_subhalo_source_sersic

pipeline_initializer = lens_sie_shear_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name])
pipeline_power_law = lens_pl_shear_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name])
pipeline_subhalo = lens_pl_shear_subhalo_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name],
                                                                     parallel=True)

pipeline = pipeline_initializer + pipeline_power_law + pipeline_subhalo

pipeline.run(data=ccd_data, mask=mask)