from autofit import conf
from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters
from autolens.lens import lens_data as ld
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.galaxy import galaxy as g
from autolens.lens import ray_tracing
from autolens.data.plotters import ccd_plotters
from autolens.lens.plotters import plane_plotters

import os

path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

lens_name = 'slacs0737+3216' # Works

ccd_data = ccd.load_ccd_data_from_fits(image_path=path + '/data/slacs/' + lens_name + '/F814W_image.fits',
                                       psf_path=path+'/data/slacs/'+lens_name+'/F814W_psf.fits',
                                       noise_map_path=path+'/data/slacs/'+lens_name+'/F814W_noise_map.fits',
                                       pixel_scale=0.03, resized_ccd_shape=(301, 301), resized_psf_shape=(21,21))

mask = msk.load_mask_from_fits(mask_path=path + '/data/slacs/' + lens_name + '/mask.fits', pixel_scale=0.03)

# ccd_plotters.plot_image(ccd_data=ccd_data, mask=mask)

lens_data = ld.LensData(ccd_data=ccd_data, mask=mask)

sie = mp.EllipticalIsothermal(centre=(0.007332219831800636, -0.017091734979904037), axis_ratio=0.8394667884862433,
                              einstein_radius=0.9733056210502408, phi=97.61311065689567)
shear=mp.ExternalShear(magnitude=0.06821354969124815, phi=0.3748585976691017)

lens_galaxy = g.Galaxy(mass=sie, shear=shear)

source_galaxy = g.Galaxy(light=lp.EllipticalSersic(centre=(0.028673479294845223, -0.13237833417289763),
                                                   axis_ratio=0.6681602590613542, phi=40.19143668987858,
                                                   intensity=0.006995496893309517, effective_radius=0.389050969603033,
                                                   sersic_index=2.965580682063875))

tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy],
                                             source_galaxies=[g.Galaxy(light=lp.SphericalSersic(intensity=0.0))],
                                             image_plane_grid_stack=lens_data.grid_stack)

path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))

plane_plotters.plot_plane_image(
    plane=tracer.source_plane, positions=None, plot_grid=True,
    units='arcsec', figsize=(7, 7), aspect='auto',
    output_path=path, output_filename='grid_only', output_format='png')

tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy],
                                             source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=lens_data.grid_stack)

plane_plotters.plot_plane_image(
    plane=tracer.source_plane, positions=None, plot_grid=True,
    units='arcsec', figsize=(7, 7), aspect='auto',
    output_path=path, output_filename='source_and_grid', output_format='png')

plane_plotters.plot_plane_image(
    plane=tracer.source_plane, positions=None, plot_grid=False,
    units='arcsec', figsize=(7, 7), aspect='auto',
    output_path=path, output_filename='source_no_grid', output_format='png')


