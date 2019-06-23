from autofit import conf
from autofit.optimize import non_linear as nl
from autolens.pipeline import phase as ph
from autolens.data.array import mask as msk
from autolens.model.galaxy import galaxy_model as gm
from autolens.lens.plotters import lens_fit_plotters
from autolens.data import ccd
from autolens.data.array import grids
from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.lens.plotters import ray_tracing_plotters
from autolens.data.plotters import ccd_plotters

import numpy as np
import os

# In this example, we'll generate a phase which fits a simple lens + source plane system. Whilst I would generally
# recommend that you write pipelines when using PyAutoLens, it can be convenient to sometimes perform non-linear
# searches in one phase to get results quickly.

# Get the relative path to the config files and output folder in our workspace.
path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))

# There is a x2 '/../../' because we are in the 'workspace/scripts/examples' folder. If you write your own script \
# in the 'workspace/script' folder you should remove one '../', as shown below.
# path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path and output papth
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

pixel_scale = 0.05

# Simulate a simple Gaussian PSF for the image.
psf = ccd.PSF.from_gaussian(shape=(11, 11), sigma=0.1, pixel_scale=pixel_scale)

# Setup the image-plane grid stack of the CCD array which will be used for generating the image-plane image of the
# simulated strong lens. The sub-grid size of 20x20 ensures we fully resolve the central regions of the lens and source
# galaxy light.
image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(250, 250), pixel_scale=pixel_scale,
                                                                   psf_shape=psf.shape, sub_grid_size=1)

# Setup the lens galaxy's light (elliptical Sersic), mass (SIE+Shear) and source galaxy light (elliptical Sersic) for
# this simulated lens.
# lens_galaxy = g.Galaxy(mass=mp.SphericalNFW(centre=(0.0, 0.0), kappa_s=0.5, scale_radius=5.0))
# lens_galaxy = g.Galaxy(mass=mp.SphericalSersic(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=1.0))

# NFW 1

# lens_galaxy = g.Galaxy(mass=mp.EllipticalNFW(centre=(0.0, 0.0), kappa_s=0.5, scale_radius=5.0, axis_ratio=0.2))

# gNFW 1

lens_galaxy = g.Galaxy(mass=mp.EllipticalGeneralizedNFW(centre=(0.0, 0.0), kappa_s=0.5, inner_slope=0.5,
                                                        scale_radius=5.0, axis_ratio=0.2))


lens_galaxy = g.Galaxy(mass=mp.EllipticalGeneralizedNFW(centre=(0.0, 0.0), kappa_s=0.5, inner_slope=1.5,
                                                        scale_radius=5.0, axis_ratio=0.2))

# Sersic 1

lens_galaxy = g.Galaxy(mass=mp.EllipticalSersic(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=0.2,
                       sersic_index=4.0, effective_radius=2.0, axis_ratio=0.8))

# Sersic 2

lens_galaxy = g.Galaxy(mass=mp.EllipticalSersic(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=0.3,
                       sersic_index=1.0, effective_radius=6.0, axis_ratio=0.5))

# Sersic 3

# lens_galaxy = g.Galaxy(mass=mp.EllipticalSersic(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=0.1,
#                        sersic_index=2.0, effective_radius=10.0, axis_ratio=0.2))

# Sersic Rad Grad 1

# lens_galaxy = g.Galaxy(mass=mp.EllipticalSersicRadialGradient(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=0.2,
#                        sersic_index=4.0, effective_radius=10.0, axis_ratio=0.2, mass_to_light_gradient=-0.3))


# Sersic Rad Grad 2

# lens_galaxy = g.Galaxy(mass=mp.EllipticalSersicRadialGradient(centre=(0.0, 0.0), intensity=1.0, mass_to_light_ratio=0.01,
#                        sersic_index=2.0, effective_radius=10.0, axis_ratio=0.2, mass_to_light_gradient=0.5))

# lens_galaxy = g.Galaxy(mass=mp.EllipticalIsothermal(centre=(0.0, 0.0), axis_ratio=0.2, einstein_radius=2.0))
source_galaxy = g.Galaxy(light=lp.EllipticalSersic(centre=(0.02, 0.02), axis_ratio=0.8, phi=60.0,
                                                   intensity=0.3, effective_radius=1.0, sersic_index=1.5))


# Use these galaxies to setup a tracer, which will generate the image-plane image for the simulated CCD data.
tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=image_plane_grid_stack)

# Lets look at the tracer's image-plane image - this is the image we'll be simulating.
ray_tracing_plotters.plot_image_plane_image(tracer=tracer)

# Simulate the CCD data, remembering that we use a special image-plane image which ensures edge-effects don't
# degrade our modeling of the telescope optics (e.g. the PSF convolution).
ccd_data = simulated_ccd.SimulatedCCDData.from_image_and_exposure_arrays(array=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
                                                                         exposure_time=300.0, psf=psf, background_sky_level=0.1, add_noise=True)

# The phase can be passed a mask, which we setup below as a 3.0" circle.
mask = msk.Mask.circular_annular(shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, inner_radius_arcsec=0.5,
                                 outer_radius_arcsec=4.0)

# resampled (see howtolens/chapter_2_lens_modeling/tutorial_7_masking_and_positions.ipynb)
ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask)

class Phase(ph.LensSourcePlanePhase):

    def pass_priors(self, results):

        pass

# To perform the analysis, we set up a phase using the 'phase' module (imported as 'ph').
# A phase takes our galaxy models and fits their parameters using a non-linear search (in this case, MultiNest).
phase = Phase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                                 source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                                 optimizer_class=nl.MultiNest,
                                 phase_name='simulate_and_fit_image/sie_to_sersicell_2_no_rescale')

# You'll see these lines throughout all of the example pipelines. They are used to make MultiNest sample the \
# non-linear parameter space faster (if you haven't already, checkout the tutorial '' in howtolens/chapter_2).

phase.optimizer.const_efficiency_mode = False
phase.optimizer.n_live_points = 75
phase.optimizer.sampling_efficiency = 0.5

# We run the phase on the image, print the results and plot the fit.
result = phase.run(data=ccd_data, mask=mask)
lens_fit_plotters.plot_fit_subplot(fit=result.most_likely_fit)