from autofit.tools import path_util
from autolens.data.array import grids
from autolens.lens.plotters import ray_tracing_plotters
from autolens.data.plotters import ccd_plotters
from autolens.data import ccd
from autolens.data import simulated_ccd
from autolens.data.array import mask as msk
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.galaxy import galaxy as g
from autolens.lens import ray_tracing
from autolens.lens import lens_fit
from autolens.lens import lens_data as ld
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg
from autolens.lens.plotters import lens_fit_plotters

import os

workspace_path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# The pixel scale of the image to be simulated
pixel_scale = 0.1

# Simulate a simple Gaussian PSF for the image.
psf = ccd.PSF.from_gaussian(shape=(11, 11), sigma=0.1, pixel_scale=pixel_scale)

# Setup the image-plane grid stack of the CCD array which will be used for generating the image-plane image of the
# simulated strong lens. The sub-grid size of 20x20 ensures we fully resolve the central regions of the lens and source
# galaxy light.
image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(100, 100), pixel_scale=pixel_scale,
                                                                   psf_shape=psf.shape, sub_grid_size=16)

# Setup the lens galaxy's light (elliptical Sersic), mass (SIE+Shear) and source galaxy light (elliptical Sersic) for
# this simulated lens.
lens_galaxy = g.Galaxy(redshift=0.5,
                       mass=mp.EllipticalIsothermal(centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0),
                       shear=mp.ExternalShear(magnitude=0.05, phi=90.0))

source_galaxy = g.Galaxy(redshift=1.0,
                         light=lp.EllipticalSersic(centre=(0.1, 0.1), axis_ratio=0.8, phi=60.0,
                                                   intensity=0.3, effective_radius=1.0, sersic_index=2.5))


# Use these galaxies to setup a tracer, which will generate the image-plane image for the simulated CCD data.
tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=image_plane_grid_stack)

# Lets look at the tracer's image-plane image - this is the image we'll be simulating.
# ray_tracing_plotters.plot_image_plane_image(tracer=tracer)

# Simulate the CCD data, remembering that we use a special image-plane image which ensures edge-effects don't
# degrade our modeling of the telescope optics (e.g. the PSF convolution).
ccd_data = simulated_ccd.SimulatedCCDData.from_image_and_exposure_arrays(
    image=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
    exposure_time=300.0, psf=psf, background_sky_level=0.1, add_noise=True)

# Lets plot the simulated CCD data before we output it to files.
# ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data)

mask = msk.Mask.circular(shape=ccd_data.shape, pixel_scale=pixel_scale, radius_arcsec=3.0)

lens_data = ld.LensData(ccd_data=ccd_data, mask=mask)

adaptive = pix.VoronoiMagnification(shape=(40, 40))

# Now lets plot our rectangular mapper with the image.
# mapper_plotters.plot_image_and_mapper(ccd_data=ccd_data, mapper=mapper, mask=mask, should_plot_grid=True)

# Okay, so lets think about the rectangular pixelization. Is it the optimal way to pixelize our source plane? Are there
# features in the source-plane that arn't ideal? How do you think we could do a better job?

# Well, given we're doing a whole tutorial on using a different pixelization to the rectangular grid, you've probably
# guessed that it isn't optimal. Infact, its pretty rubbish, and not a pixelization we'll actually want to model
# many lenses with!

# So what is wrong with the grid? Well, first, lets think about the source reconstruction.
# inversion_plotters.plot_reconstructed_pixelization(inversion=inversion, should_plot_centres=True)

source_galaxy = g.Galaxy(redshift=1.0, pixelization=adaptive, regularization=reg.Constant(coefficients=(1.0,)))
tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=lens_data.grid_stack)
fit = lens_fit.LensDataFit.for_data_and_tracer(lens_data=lens_data, tracer=tracer)

print(fit.figure_of_merit)

# lens_fit_plotters.plot_fit_subplot(fit=fit, should_plot_mask=True, extract_array_from_mask=True, zoom_around_mask=True)

source_galaxy = g.Galaxy(redshift=1.0, pixelization=adaptive,
                         regularization=reg.AdaptiveBrightness(coefficients=(1.0, 1.0), signal_scale=1.0),
                         hyper_model_image_1d=fit.model_image_1d, hyper_galaxy_image_1d=fit.model_image_1d,
                         hyper_minimum_value=0.0)

tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=lens_data.grid_stack)
fit = lens_fit.LensDataFit.for_data_and_tracer(lens_data=lens_data, tracer=tracer)

print(fit.figure_of_merit)

lens_fit_plotters.plot_fit_subplot(fit=fit, should_plot_mask=True, extract_array_from_mask=True, zoom_around_mask=True)