from autofit import conf
from autofit.tools import path_util
from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import numpy as np
import os

# Welcome to the pipeline runner. This tool allows you to load strong lens data, and pass it to pipelines for a
# PyAutoLens analysis. To show you around, we'll load up some example data and run it through some of the example
# pipelines that come distributed with PyAutoLens.

# The runner is supplied as both this Python script and a Juypter notebook. Its up to you which you use - I personally
# prefer the python script as provided you keep it relatively small, its quick and easy to comment out different lens
# names and pipelines to perform different analyses. However, notebooks are a tidier way to manage visualization - so
# feel free to use notebooks. Or, use both for a bit, and decide your favourite!

# The pipeline runner is fairly self explanatory. Make sure to checkout the pipelines in the
#  workspace/pipelines/examples/ folder - they come with detailed descriptions of what they do. I hope that you'll
# expand on them for your own personal scientific needs

# Setup the path to the workspace, using a relative directory name.
workspace_path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
output_path = workspace_path + '../../outputs/PyAutoLens/slacs_jam'
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=output_path)

# It is convenient to specify the data type and data name as a string, so that if the pipeline is applied to multiple
# images we don't have to change all of the path entries in the load_ccd_data_from_fits function below.

data_type = 'slacs'

data_filter = 'F814W'

# data_name = 'slacs0216-0813' # Incorrect
data_name = 'slacs0252+0039' # Works
# data_name = 'slacs0737+3216' # Works
# data_name = 'slacs0912+0029' # Works
# data_name = 'slacs0959+4410' # Bad fit phase 5 due to source demag thing
# data_name = 'slacs0959+4416' # Bad Fit because its the hard to fit lens
# data_name = 'slacs1011+0143' # x2 lenses
# data_name = 'slacs1205+4910' # Bad fit because foreground galaxy is fitted
data_name = 'slacs1250+0523' # Bad fit due to poor parametric source.
# data_name = 'slacs1402+6321' # Bad fit and i cant even see the source :/
# data_name = 'slacs1420+6019' # Bad fit phase 5 due to complex source.
# data_name = 'slacs1430+4105' # Works
# data_name = 'slacs1627+0053' # Works, but weird low res source
# data_name = 'slacs1630+4520'
# data_name = 'slacs2238-0754'
# data_name = 'slacs2300+0022'
# data_name = 'slacs2303+1422'

pixel_scale = 0.03

# Create the path where the data will be loaded from, which in this case is
# '/workspace/data/example/lens_light_and_x1_source/'
data_path = path_util.make_and_return_path_from_path_and_folder_names(path=workspace_path,
                                                                      folder_names=['data', data_type, data_name])

from autolens.data import ccd

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'F814W_image.fits',
                                       psf_path=data_path + 'F814W_psf.fits',
                                       noise_map_path=data_path + 'F814W_noise_map.fits',
                                       pixel_scale=pixel_scale, renormalize_psf=True,
                                       resized_ccd_shape=(301, 301), resized_psf_shape=(15, 15))

# mask = msk.load_mask_from_fits(mask_path=data_path + 'mask.fits', pixel_scale=pixel_scale)
# mask = mask.resized_scaled_array_from_array(new_shape=(301, 301))

positions = ccd.load_positions(positions_path=data_path + 'positions.dat')

ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data)

# Running a pipeline is easy, we simply import it from the pipelines folder and pass the lens data to its run function.
# Below, we'll' use a 3 phase example pipeline to fit the data with a parametric lens light, mass and source light
# profile. Checkout 'workspace/pipelines/examples/lens_light_and_x1_source_parametric.py' for a full description of
# the pipeline.

# The phase folders input determines the output directory structure of the pipeline, for example the input below makes
# the directory structure:
# 'autolens_workspace/output/phase_folder_1/phase_folder_2/pipeline_name/' or
# 'autolens_workspace/output/example/lens_light_and_x1_source/lens_light_and_x1_source_parametric/'

# For large samples of images, we can therefore easily group lenses that are from the same sample or modeled using the
# same pipeline.

from workspace_jam.pipelines.with_lens_light.bulge_disk.initialize import lens_sersic_exp_sie_shear_source_sersic
from workspace_jam.pipelines.with_lens_light.bulge_disk.inversion.from_initialize import lens_sersic_exp_sie_shear_source_inversion
from workspace_jam.pipelines import slacs1520
# from workspace_jam.pipelines.with_lens_light.power_law.from_inversion import lens_sersic_pl_shear_source_inversion
# from workspace_jam.pipelines.with_lens_light.subhalo.from_power_law import lens_sersic_pl_shear_subhalo_source_inversion

pipeline_initializer = lens_sersic_exp_sie_shear_source_sersic.make_pipeline(
    phase_folders=[data_filter, data_name], positions_threshold=1.0, inner_mask_radii=0.2,
    pl_align_bulge_disk_centre=True)

pipeline_inversion = lens_sersic_exp_sie_shear_source_inversion.make_pipeline(
    phase_folders=[data_filter, data_name], positions_threshold=1.0, pl_align_bulge_disk_centre=True)

pipeline_slacs = slacs1520.make_pipeline(
    phase_folders=[data_filter, data_name], positions_threshold=1.0, pl_align_bulge_disk_centre=True)

# pipeline_power_law = lens_sersic_pl_shear_source_inversion.make_pipeline(phase_folders=[data_type, data_name])
# pipeline_subhalo = lens_sersic_pl_shear_subhalo_source_inversion.make_pipeline(phase_folders=[data_type, data_name])

pipeline = pipeline_initializer + pipeline_slacs # + pipeline_power_law + pipeline_subhalo

pipeline.run(data=ccd_data, positions=positions)