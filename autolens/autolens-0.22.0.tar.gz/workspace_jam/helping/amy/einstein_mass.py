from autofit import conf

import os

# Get the relative path to the config files and output folder in our workspace.
path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path and output path.
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

import numpy as np
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.galaxy import galaxy as g
from autolens.model.galaxy import galaxy_model as gm
from autolens.lens import ray_tracing
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg
from astropy import cosmology
from autolens.data.array import grids
from autolens.data import ccd
from autolens.lens import lens_data as ld
from autolens.data.array import mask as msk

#lens_name = np.array(['slacs0216-0813', 'slacs0252+0039', 'slacs0737+3216', 'slacs0912+0029', 'slacs0959+4410',
#                      'slacs0959+4416', 'slacs1011+0143', 'slacs1011+0143', 'slacs1205+4910', 'slacs1250+0523',
#                      'slacs1402+6321', 'slacs1420+6019', 'slacs1430+4105', 'slacs1627+0053', 'slacs1630+4520',
#                      'slacs2238-0754', 'slacs2300+0022', 'slacs2303+1422'])

lens_name = 'slacs1430+4105'

pixel_scale = 0.03
new_shape = (301, 301)

ccd_data = ccd.load_ccd_data_from_fits(image_path=path + '/data/slacs/' + lens_name + '/F814W_image.fits',
                                       psf_path=path+'/data/slacs/'+lens_name+'/F814W_psf.fits',
                                       noise_map_path=path+'/data/slacs/'+lens_name+'/F814W_noise_map.fits',
                                       pixel_scale=pixel_scale,
                                       resized_ccd_shape=new_shape, resized_psf_shape=(15, 15))
mask = msk.load_mask_from_fits(mask_path=path + '/data/slacs/' + lens_name + '/mask.fits', pixel_scale=pixel_scale)
mask = mask.resized_scaled_array_from_array(new_shape=new_shape)

lens_data = ld.LensData(ccd_data=ccd_data, mask=mask)

list_ = []
n_params = 17

image_plane_grid_stack = grids.GridStack.from_shape_pixel_scale_and_sub_grid_size(shape=ccd_data.shape,
                                                                                  pixel_scale=ccd_data.pixel_scale,
                                                                                  sub_grid_size=2)

lens_galaxy = g.Galaxy(mass=mp.EllipticalIsothermal(centre=(0.0, 0.0), axis_ratio=0.9,
                                                    phi=45.0, einstein_radius=1.0),
                       shear=mp.ExternalShear(magnitude=0.01, phi=0.0), redshift=0.285)
source_galaxy = g.Galaxy(pixelization=pix.VoronoiMagnification(shape=(10.0, 10.0)),
                         regularization=reg.Constant(1.0), redshift=0.575)

# lens_galaxy = g.Galaxy(mass=mp.EllipticalIsothermal(centre=(data.iloc[0,5], data.iloc[0,6]), axis_ratio=data.iloc[0,7],
#                                                     phi=data.iloc[0,8], einstein_radius=data.iloc[0,9]),
#                        shear=mp.ExternalShear(magnitude=data.iloc[0,10], phi=data.iloc[0,11]), redshift=0.285)
# source_galaxy = g.Galaxy(pixelization=pix.VoronoiMagnification(shape=(data.iloc[0,14], data.iloc[0,15])),
#                          regularization=reg.Constant(data.iloc[0,16]), redshift=0.575)
#image_plane_grid_stack = grids.GridStack.from_shape_pixel_scale_and_sub_grid_size(shape=(301, 301), pixel_scale=0.03,
#                                                                      sub_grid_size=2)

tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=image_plane_grid_stack, cosmology=cosmology.Planck15)

print(tracer.einstein_mass_between_planes_in_units)