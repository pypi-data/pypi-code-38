from autofit import conf
from autofit.tools import path_util

from autolens.data import ccd
from autolens.data.array import mask as msk

import os

# Setup the path to the workspace, using a relative directory name.
workspace_path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
output_path = workspace_path + '../../outputs/PyAutoLens/'
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=output_path)

data_type = 'noise_normal'
data_level = 'level_0'
data_name = 'small_hi_sn_system_1'

pixel_scale = 0.00976562

data_path = path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=['data', 'subhalo_challenge', data_type, data_level, data_name])

resized_ccd_shape = (320, 320)

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'image.fits',
                                       psf_path=data_path + 'psf.fits',
                                       noise_map_path=data_path + 'noise_map.fits', pixel_scale=pixel_scale,
                                       resized_ccd_shape=resized_ccd_shape)

mask = msk.load_mask_from_fits(mask_path=data_path + 'mask_irregular.fits', pixel_scale=pixel_scale)
mask = mask.resized_scaled_array_from_array(new_shape=resized_ccd_shape)

from workspace_jam.pipelines.no_lens_light.initialize import lens_sie_shear_source_sersic
from workspace_jam.pipelines.no_lens_light.power_law.from_initialize import lens_pl_shear_source_sersic
from workspace_jam.pipelines.no_lens_light.subhalo.from_power_law import lens_pl_shear_subhalo_source_sersic

pipeline_initialize = lens_sie_shear_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name])
pipeline_power_law = lens_pl_shear_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name])
pipeline_subhalo = lens_pl_shear_subhalo_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name],
                                                                     parallel=True)

pipeline = pipeline_initialize + pipeline_power_law + pipeline_subhalo

# from workspace_jam.pipelines.no_lens_light.initialize import lens_sie_shear_source_sersic
# from workspace_jam.pipelines.no_lens_light.subhalo.from_initialize import lens_sie_shear_subhalo_source_sersic
#
# pipeline_initialize = lens_sie_shear_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name])
# pipeline_subhalo = lens_sie_shear_subhalo_source_sersic.make_pipeline(phase_folders=[data_type, data_level, data_name],
#                                                                      parallel=True)
#
# pipeline = pipeline_initialize + pipeline_subhalo
#
pipeline.run(data=ccd_data, mask=mask)