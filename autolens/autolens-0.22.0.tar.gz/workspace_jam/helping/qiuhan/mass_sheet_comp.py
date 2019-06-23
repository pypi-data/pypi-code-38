from autolens.data import ccd
from autolens.data.array import grids
from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.lens.plotters import ray_tracing_plotters
from autolens.data.plotters import ccd_plotters
from autolens.model.profiles.plotters import profile_plotters
from autolens.lens import plane
from autolens.lens.plotters import plane_plotters

import numpy as np
import matplotlib.pyplot as plt
from workspace_jam.helping.qiuhan.deflection_map import deflection_multi_map
from astropy.cosmology import FlatLambdaCDM


pixel_scale_img = 0.05
npixel_img = int(10/pixel_scale_img)

H0 = 100.0
OM0 = 0.3
cosmo = FlatLambdaCDM(H0=H0, Om0=OM0)

psf = ccd.PSF.from_gaussian(shape=(11, 11), sigma=0.1,
                            pixel_scale=pixel_scale_img)

image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(
        shape=(200, 200), pixel_scale=pixel_scale_img, psf_shape=psf.shape,
        sub_grid_size=1)

lens_galaxy = g.Galaxy(mass=mp.SphericalIsothermal(centre=(3.0, 3.0),
    einstein_radius=1.6), redshift=0.5)

source_galaxy = g.Galaxy(light=lp.EllipticalSersic(centre=(0.1, 0.0),
    axis_ratio=0.8, phi=0.0, intensity=1.0, effective_radius=1.0,
    sersic_index=2.5), redshift=1.0)

# "zero kappa" Mass Sheet
mass_sheet = g.Galaxy(sheet=mp.MassSheet(centre=(0.0, 0.0), kappa=0.0), redshift=0.2)



# Below, all variables with "_test" means inpluding the mass sheet and all
# variables with "_ref" means they don't have a mass sheet

lens_list_ref = [lens_galaxy, source_galaxy]

tracer_ref = ray_tracing.TracerMultiPlanes(
        galaxies=lens_list_ref,
        image_plane_grid_stack=image_plane_grid_stack, cosmology=cosmo)

################################################################################
# Here, I use deflection_multi_map function to calculate the deflection angles
# in multiplane situations. This function will return an N*N*2 array with
# [:, :, 1] to be deflections in x direction and [:, :, 0] to be deflections in
# y direction.

alpha_ref = deflection_multi_map(N=npixel_img,
        map_scale=pixel_scale_img, tracer=tracer_ref, z_lens=0.5,
        z_source=1.0)

alphax_ref = alpha_ref[:, :, 1]
alphay_ref = alpha_ref[:, :, 0]

lens_list_test = [lens_galaxy, mass_sheet, source_galaxy]

tracer_test = ray_tracing.TracerMultiPlanes(
        galaxies=lens_list_test,
        image_plane_grid_stack=image_plane_grid_stack, cosmology=cosmo)

alpha_test = deflection_multi_map(N=npixel_img,
        map_scale=pixel_scale_img, tracer=tracer_test, z_lens=0.5,
        z_source=1.0)

alphax_test = alpha_test[:, :, 1]
alphay_test = alpha_test[:, :, 0]


fig, axes = plt.subplots(1, 2, figsize=(8, 4))
axes[0].imshow(alphax_ref)
axes[0].set_title('no mass sheet')
axes[1].imshow(alphax_test)
axes[1].set_title('with mass sheet')
plt.show()