from autofit import conf
from autolens.data import ccd
from autolens.data.array.util import array_util
from autolens.plotters import array_plotters

import os
import numpy as np

slacs = []

slacs.append({'name' : 'slacs0216-0813', 'target_name' : 'GAL-0668-52162-428', 'exposure_time' : 2232.0,
              'redshift_lens' : 0.332, 'redshift_source' : 0.523})

path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

for slac in slacs:

    name = slac['name']
    target_name = slac['target_name']
    exposure_time = slac['exposure_time']

    for filter in ['F555W']:

        path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))

        image_path = path+'/david_0/'+target_name+'_'+filter+'_post.fits'

        if os.path.exists(image_path):

            psf_path = path+'/david_0/'+target_name+'_'+filter+'_post.fits'
            background_noise_map_path = path+'/david_0/'+target_name+'_'+filter+'_post.fits'

            ccd_data = ccd.load_ccd_data_from_fits(image_path=image_path, image_hdu=1, pixel_scale=0.03,
                                                  psf_path=psf_path, psf_hdu=3,
                                                  noise_map_from_image_and_background_noise_map=True,
                                                  background_noise_map_path=background_noise_map_path,
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
            print(name + '  ' + filter + '  ' + str(ccd_data.signal_to_noise_max))
            array_plotters.plot_array(array=1.0 / ccd_data.noise_map)
            # print(np.max(ccd_data.exposure_time_map))
            # print(np.max(ccd_data.poisson_noise_map))
            # print(np.max(ccd_data.noise_map))

            max_noise = np.max(ccd_data.noise_map)
            print()

            absolute_signal_to_noise = np.abs(ccd_data.image_2d) / ccd_data.noise_map
            array_plotters.plot_array(absolute_signal_to_noise)
            print(np.max(absolute_signal_to_noise))

            ccd_data.noise_map[absolute_signal_to_noise > 200.0] = max_noise

            absolute_signal_to_noise = np.abs(ccd_data.image_2d) / ccd_data.noise_map
            array_plotters.plot_array(absolute_signal_to_noise)
            stop
#            ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data)

            path = path + '../../data/slacs/'+name+'/'

            if not os.path.exists(path):
                os.mkdir(path)

            ccd.output_ccd_data_to_fits(ccd_data=ccd_data, image_path=path + filter + '_image.fits',
                                       psf_path=path+filter+'_psf.fits',
                                       noise_map_path=path + filter+'_noise_map.fits',
                                       background_noise_map_path=path+filter+'_background_noise_map.fits',
                                       poisson_noise_map_path=path+filter+'_poisson_noise_map.fits',
                                       exposure_time_map_path=path+filter+'_exposure_time_map.fits', overwrite=True)