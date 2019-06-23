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
image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(150, 150), pixel_scale=pixel_scale,
                                                                   psf_shape=psf.shape, sub_grid_size=1)

# Setup the lens galaxy's light (elliptical Sersic), mass (SIE+Shear) and source galaxy light (elliptical Sersic) for
# this simulated lens.

lens_galaxy = g.Galaxy(mass=mp.SphericalIsothermal(centre=(0.0, 0.4), einstein_radius=0.8))
lens_galaxy = g.Galaxy(mass=mp.SphericalIsothermal(centre=(0.0, -0.4), einstein_radius=0.8))
source_galaxy = g.Galaxy(light=lp.EllipticalSersic(centre=(0.02, 0.02), axis_ratio=0.8, phi=60.0,
                                                   intensity=0.3, effective_radius=1.0, sersic_index=1.5))


# Use these galaxies to setup a tracer, which will generate the image-plane image for the simulated CCD data.
tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy, lens_galaxy], source_galaxies=[source_galaxy],
                                             image_plane_grid_stack=image_plane_grid_stack)

# Lets look at the tracer's image-plane image - this is the image we'll be simulating.
ray_tracing_plotters.plot_image_plane_image(tracer=tracer)

# Simulate the CCD data, remembering that we use a special image-plane image which ensures edge-effects don't
# degrade our modeling of the telescope optics (e.g. the PSF convolution).
ccd_data = simulated_ccd.SimulatedCCDData.from_image_and_exposure_arrays(array=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
                                                                         exposure_time=300.0, psf=psf, background_sky_level=0.1, add_noise=True)

# The phase can be passed a mask, which we setup below as a 3.0" circle.
mask = msk.Mask.circular_annular(shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, inner_radius_arcsec=0.5,
                                 outer_radius_arcsec=3.0)

# resampled (see howtolens/chapter_2_lens_modeling/tutorial_7_masking_and_positions.ipynb)
ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask)

# We're going to model our lens galaxy using a light profile (an elliptical Sersic) and mass profile
# (a singular isothermal ellipsoid). We load these profiles from the 'light_profiles (lp)' and 'mass_profiles (mp)'.

# To setup our model galaxies, we use the 'galaxy_model' module and GalaxyModel class.
# A GalaxyModel represents a galaxy where the parameters of its associated profiles are
# variable and fitted for by the analysis.
lens_galaxy_model = gm.GalaxyModel(mass=mp.SphericalIsothermal)
source_galaxy_model = gm.GalaxyModel(light=lp.EllipticalSersic)

class Phase(ph.LensSourcePlanePhase):

    def pass_priors(self, results):

        pass

# To perform the analysis, we set up a phase using the 'phase' module (imported as 'ph').
# A phase takes our galaxy models and fits their parameters using a non-linear search (in this case, MultiNest).
phase = Phase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                                 source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                                 optimizer_class=nl.MultiNest,
                                 phase_name='simulate_and_fit_image_2/x2_sie_centres_split_08')

# You'll see these lines throughout all of the example pipelines. They are used to make MultiNest sample the \
# non-linear parameter space faster (if you haven't already, checkout the tutorial '' in howtolens/chapter_2).

phase.optimizer.const_efficiency_mode = False
phase.optimizer.n_live_points = 75
phase.optimizer.sampling_efficiency = 0.5

# We run the phase on the image, print the results and plot the fit.
result = phase.run(data=ccd_data)
lens_fit_plotters.plot_fit_subplot(fit=result.most_likely_fit)