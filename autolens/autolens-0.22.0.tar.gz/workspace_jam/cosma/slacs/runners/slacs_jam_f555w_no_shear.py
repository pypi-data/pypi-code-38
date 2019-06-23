from autofit import conf
from autofit.tools import path_util
from autolens.data import ccd
from autolens.data.array import mask as msk

import os
import sys

cosma_username = 'dc-nigh1'
cosma_path = '/cosma6/data/dp004/dc-nigh1/'
cosma_data_path = path_util.make_and_return_path_from_path_and_folder_names(
    cosma_path, folder_names=['data'])
cosma_output_path = path_util.make_and_return_path_from_path_and_folder_names(
    cosma_path, folder_names=['output','slacs_jam'])

workspace_path = '{}/../../../'.format(os.path.dirname(os.path.realpath(__file__)))

# Lets now use the above paths to set the config path and output path for our Cosma run.
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=cosma_output_path)

# Lets take a look at a Cosma batch script, which can be found at 'workspace/runners/cosma/batch/pipeline_runner_cosma'.
# When we submit a PyAutoLens job to Cosma, we submit a 'batch' of jobs, whereby each job will run on one CPU of Cosma.
# Thus, if our lens sample contains, lets say, 17 lenses, we'd submit 17 jobs at the same time where each job applies
# our pipeline to each image.

# The fifth line of this batch script - '#SBATCH --array=1-17' is what species this. Its telling Cosma we're going to
# run 17 jobs, and the id's of those jobs will be numbered from 1 to 17. Infact, these ids are passed to this runner,
# and we'll use them to ensure that each jobs loads a different image. Lets get the cosma array id for our job.
cosma_array_id = int(sys.argv[1])

# Now, I just want to really drive home what the above line is doing. For every job we run on Cosma, the cosma_array_id
# will be different. That is, job 1 will get a cosma_array_id of 1, job 2 will get an id of 2, and so on. This is our
# only unique identifier of every job, thus its our only hope of specifying for each job which image they load!

# Fortunately, we're used to specifying the lens name as a string, so that our pipeline can be applied to multiple
# images with ease. On Cosma, we can apply the same logic, but put these strings in a list such that each Cosma job
# loads a different lens name based on its ID. neat, huh?

data_type = 'slacs_jam'

data_filter = 'F555W'

data_name = []
data_name.append('') # Task number beings at 1, so keep index 0 blank
data_name.append('slacs0216-0813') # Index 1
data_name.append('slacs0737+3216') # Index 2
data_name.append('slacs0912+0029') # Index 3
data_name.append('slacs0959+4410') # Index 4
data_name.append('slacs1205+4910') # Index 5
data_name.append('slacs1250+0523') # Index 6
data_name.append('slacs1402+6321') # Index 7
data_name.append('slacs1420+6019') # Index 7
data_name.append('slacs1627+0053') # Index 9
data_name.append('slacs1630+4520') # Index 10
data_name.append('slacs2238-0754') # Index 11
data_name.append('slacs2300+0022') # Index 12
data_name.append('slacs2303+1422') # Index 13

inner_mask_radii = []
inner_mask_radii.append(0.1)
inner_mask_radii.append(0.3) # Index 1, slacs0216-0813
inner_mask_radii.append(0.3) # Index 2, slacs0737+3216
inner_mask_radii.append(0.5) # Index 3, slacs0912+0029
inner_mask_radii.append(0.2) # Index 4, slacs0959+4410
inner_mask_radii.append(0.3) # Index 5, slacs1205+4910
inner_mask_radii.append(0.2) # Index 6, slacs1250+0523
inner_mask_radii.append(0.5) # Index 7, slacs1402+6321
inner_mask_radii.append(0.5) # Index 8, slacs1420+6019
inner_mask_radii.append(0.3) # Index 9, slacs1627+0053
inner_mask_radii.append(0.3) # Index 10, slacs1630+4520
inner_mask_radii.append(0.3) # Index 11, slacs2238-0754
inner_mask_radii.append(0.4) # Index 12, slacs2300+0022
inner_mask_radii.append(0.3) # Index 13, slacs2303+1422

data_name = data_name[cosma_array_id]
inner_mask_radii = inner_mask_radii[cosma_array_id]

pixel_scale = 0.03 # Make sure your pixel scale is correct!

# We now use the lens_name list to load the image on each job, noting that in this example I'm assuming our lenses are
# on the Cosma data directory folder called 'slacs'
data_path = path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_data_path, folder_names=[data_type, data_name])

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + 'F814W_image.fits',
                                       psf_path=data_path + 'F814W_psf.fits',
                                       noise_map_path=data_path + 'F814W_noise_map.fits',
                                       pixel_scale=pixel_scale, resized_ccd_shape=(301, 301),
                                       resized_psf_shape=(15, 15))

mask = msk.load_mask_from_fits(mask_path=data_path + 'mask.fits', pixel_scale=pixel_scale)
mask = mask.resized_scaled_array_from_array(new_shape=(301, 301))

positions = ccd.load_positions(positions_path=data_path + 'positions.dat')

# Running a pipeline is exactly the same as we're used to. We import it, make it, and run it, noting that we can
# use the lens_name's to ensure each job outputs its results to a different directory.

from workspace_jam.pipelines.with_lens_light.bulge_disk.initialize import lens_sersic_exp_sie_source_sersic
from workspace_jam.pipelines.with_lens_light.bulge_disk.inversion.from_initialize import lens_sersic_exp_sie_source_inversion
# from workspace_jam.pipelines.with_lens_light.power_law.from_inversion import lens_sersic_pl_shear_source_inversion
# from workspace_jam.pipelines.with_lens_light.subhalo.from_power_law import lens_sersic_pl_shear_subhalo_source_inversion

pipeline_initializer = lens_sersic_exp_sie_source_sersic.make_pipeline(
    phase_folders=[data_filter, data_name], positions_threshold=1.0, inner_mask_radii=inner_mask_radii,
    pl_align_bulge_disk_centre=True)

pipeline_inversion = lens_sersic_exp_sie_source_inversion.make_pipeline(
    phase_folders=[data_filter, data_name], positions_threshold=1.0, inner_mask_radii=inner_mask_radii,
    pl_fix_lens_light=True, pl_align_bulge_disk_centre=True)

# pipeline_power_law = lens_sersic_pl_shear_source_inversion.make_pipeline(phase_folders=[data_type, data_name])
# pipeline_subhalo = lens_sersic_pl_shear_subhalo_source_inversion.make_pipeline(phase_folders=[data_type, data_name])

pipeline = pipeline_initializer + pipeline_inversion # + pipeline_power_law + pipeline_subhalo

pipeline.run(data=ccd_data, mask=mask, positions=positions)