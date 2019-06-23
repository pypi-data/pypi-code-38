from autofit.tools import path_util
from autofit import conf
from autolens.data.array.util import array_util
from autolens.data import ccd
from autolens.data.plotters import ccd_plotters

import os
import numpy as np

slacs = []

slacs.append({'name' : 'slacs0216-0813', 'target_name' : 'GAL-0668-52162-428', 'exposure_time' : 2232.0,
              'redshift_lens' : 0.332, 'redshift_source' : 0.523})
slacs.append({'name' : 'slacs0252+0039', 'target_name' : 'GAL-0807-52295-614', 'exposure_time' : 2058.0,
              'redshift_lens' : 0.280, 'redshift_source' : 0.982})
slacs.append({'name' : 'slacs0737+3216', 'target_name' : 'GAL-0541-51959-145', 'exposure_time' : 2272.0,
              'redshift_lens' : 0.322, 'redshift_source' : 0.581})
slacs.append({'name' : 'slacs0912+0029', 'target_name' : 'GAL-0472-51955-429', 'exposure_time' : 2224.0,
              'redshift_lens' : 0.164, 'redshift_source' : 0.324}) # two exposures - was highest time used?
slacs.append({'name' : 'slacs0959+4410', 'target_name' : 'GAL-0572-52289-495', 'exposure_time' : 2224.0,
              'redshift_lens' : 0.126, 'redshift_source' : 0.535})
slacs.append({'name' : 'slacs0959+4416', 'target_name' : 'GAL-0942-52703-499', 'exposure_time' : 2128.0,
              'redshift_lens' : 0.237,  'redshift_source' : 0.531})
slacs.append({'name' : 'slacs0959+5100', 'target_name' : 'GAL-0902-52409-068', 'exposure_time' : 2440.0,
              'redshift_lens' : 0.241, 'redshift_source' : 0.470})
slacs.append({'name' : 'slacs1011+0143', 'target_name' : 'GAL-PLACE_HOLDER', 'exposure_time' : 2088.0,
              'redshift_lens' : 0.331, 'redshift_source' : 2.701})
slacs.append({'name' : 'slacs1205+4910', 'target_name' : 'GAL-0969-52442-134', 'exposure_time' : 2388.0,
              'redshift_lens' : 0.215, 'redshift_source' : 0.481})
slacs.append({'name' : 'slacs1250+0523', 'target_name' : 'GAL-0847-52426-549', 'exposure_time' : 2232.0,
              'redshift_lens' : 0.232, 'redshift_source' : 0.795})
slacs.append({'name' : 'slacs1402+6321', 'target_name' : 'GAL-0605-52353-503', 'exposure_time' : 2520.0,
              'redshift_lens' : 0.205, 'redshift_source' : 0.481})
slacs.append({'name' : 'slacs1420+6019', 'target_name' : 'GAL-0788-52338-605', 'exposure_time' : 2520.0,
              'redshift_lens' : 0.063, 'redshift_source' : 0.535})
slacs.append({'name' : 'slacs1430+4105', 'target_name' : 'GAL-1349-52797-406', 'exposure_time' : 2128.0,
              'redshift_lens' : 0.285, 'redshift_source' : 0.575})
slacs.append({'name' : 'slacs1627+0053', 'target_name' : 'GAL-0364-52000-084', 'exposure_time' : 2240.0,
              'redshift_lens' : 0.208, 'redshift_source' : 0.524})
slacs.append({'name' : 'slacs1630+4520', 'target_name' : 'GAL-0626-52057-518', 'exposure_time' : 2388.0,
              'redshift_lens' : 0.248, 'redshift_source' : 0.793})
slacs.append({'name' : 'slacs2238-0754', 'target_name' : 'GAL-0722-52224-442', 'exposure_time' : 2232.0,
              'redshift_lens' : 0.137, 'redshift_source' : 0.713})
slacs.append({'name' : 'slacs2300+0022', 'target_name' : 'GAL-0677-52606-520', 'exposure_time' : 2224.0,
              'redshift_lens' : 0.228, 'redshift_source' : 0.463})
slacs.append({'name' : 'slacs2303+1422', 'target_name' : 'GAL-0743-52262-304', 'exposure_time' : 2240.0,
              'redshift_lens' : 0.155, 'redshift_source' : 0.517})

workspace_path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
data_raw_path = path_util.make_and_return_path_from_path_and_folder_names(path=workspace_path,
                                                                          folder_names=['data_raw'])
slacs_sample_path = path_util.make_and_return_path_from_path_and_folder_names(path=data_raw_path,
                                                                              folder_names=['slacs_sample'])
for slac in slacs:

    name = slac['name']
    target_name = slac['target_name']
    exposure_time = slac['exposure_time']

    for filter in ['F814W', 'F555W']:

        slacs_data_path = path_util.make_and_return_path_from_path_and_folder_names(path=slacs_sample_path, 
                                                                                    folder_names=['david_0'])
        slacs_file = slacs_data_path + target_name + '_' + filter + '_post.fits'

        if os.path.exists(slacs_file):

            ccd_data = ccd.load_ccd_data_from_fits(image_path=slacs_file, image_hdu=1, pixel_scale=0.03,
                                                   psf_path=slacs_file, psf_hdu=3,
                                                   noise_map_from_image_and_background_noise_map=True,
                                                   background_noise_map_path=slacs_file,
                                                   background_noise_map_hdu=2,
                                                   convert_background_noise_map_from_inverse_noise_map=True,
                                                   poisson_noise_map_from_image=True,
                                                   exposure_time_map_from_single_value=exposure_time,
                                                   exposure_time_map_from_inverse_noise_map=True,
                                                   resized_psf_shape=(61, 61))

            ccd_data.noise_map = array_util.replace_noise_map_2d_values_where_image_2d_values_are_negative(
                image_2d=ccd_data.image_2d,
                noise_map_2d=ccd_data.noise_map)

            print()
            print(name + '  ' + filter + '  ' + str(ccd_data.absolute_signal_to_noise_max))

            slacs_output_path = path_util.make_and_return_path_from_path_and_folder_names(
                path=workspace_path, folder_names=['data', 'slacs', name])

            ccd.output_ccd_data_to_fits(ccd_data=ccd_data, image_path=slacs_output_path + filter + '_image.fits',
                                        psf_path=slacs_output_path + filter + '_psf.fits',
                                        noise_map_path=slacs_output_path + filter + '_noise_map.fits',
                                        background_noise_map_path=slacs_output_path + filter + '_background_noise_map.fits',
                                        poisson_noise_map_path=slacs_output_path + filter + '_poisson_noise_map.fits',
                                        exposure_time_map_path=slacs_output_path + filter + '_exposure_time_map.fits',
                                        overwrite=True)

            slacs_image_path = path_util.make_and_return_path_from_path_and_folder_names(path=slacs_output_path,
                                                                                         folder_names=['images'])

            ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, output_path=slacs_image_path + filter + '_',
                                          output_format='png')
            ccd_plotters.plot_ccd_individual(ccd_data=ccd_data,
                                             should_plot_image=True,
                                             should_plot_noise_map=True,
                                             should_plot_psf=True,
                                             should_plot_signal_to_noise_map=True,
                                             should_plot_absolute_signal_to_noise_map=True,
                                             should_plot_potential_chi_squared_map=True,
                                             output_path=slacs_image_path + filter + '_', output_format='png')