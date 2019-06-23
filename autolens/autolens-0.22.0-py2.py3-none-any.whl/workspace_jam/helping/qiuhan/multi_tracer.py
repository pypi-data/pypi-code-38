from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import mass_profiles as mp
from autolens.model.profiles import light_profiles as lp
from autolens.data.array import grids
from autolens.data import ccd
import numpy as np
import matplotlib.pyplot as plt

pixel_scale = 0.05

psf = ccd.PSF.from_gaussian(shape=(11, 11), sigma=0.1, pixel_scale=pixel_scale)

grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(200, 200), pixel_scale=pixel_scale, psf_shape=psf.shape,
                                                       sub_grid_size=1)

g0 = g.Galaxy(mass_profile=mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.6), redshift=0.5)

source_galaxy = g.Galaxy(light=lp.EllipticalSersic(centre=(0.0, 0.0),
    axis_ratio=1.0, phi=0.0, intensity=1.0, effective_radius=1.0,
    sersic_index=2.5), redshift=1.0)

tracer0 = ray_tracing.TracerMultiPlanes(galaxies=[g0, source_galaxy], image_plane_grid_stack=grid_stack)

redshift_1 = 0.5
subhalo_1 = g.Galaxy(mass=mp.SphericalNFW(centre=(1.6, 0.0), kappa_s=0.3,
    scale_radius=0.5), redshift=redshift_1)

tracer1 = ray_tracing.TracerMultiPlanes(galaxies=[g0, source_galaxy, subhalo_1], image_plane_grid_stack=grid_stack)

redshift_2 = 0.8
subhalo_2 = g.Galaxy(mass=mp.SphericalNFW(centre=(1.6, 0.0), kappa_s=0.3, scale_radius=0.5), redshift=redshift_2)

tracer2 = ray_tracing.TracerMultiPlanes(galaxies=[g0, source_galaxy, subhalo_2], image_plane_grid_stack=grid_stack)

redshift_3 = 0.9
traced_grid = tracer0.grid_at_redshift_from_image_plane_grid_and_redshift(
        image_plane_grid=np.array([[1.6, 0.0]]), redshift=redshift_3)

subhalo_3 = g.Galaxy(mass=mp.SphericalNFW(centre=traced_grid, kappa_s=0.3, scale_radius=0.5),
        light=lp.EllipticalSersic(centre=traced_grid, axis_ratio=1.0, phi=0.0, intensity=1.0, effective_radius=1.0,
        sersic_index=2.5), redshift=redshift_3)


tracer3 = ray_tracing.TracerMultiPlanes(galaxies=[g0, source_galaxy, subhalo_3], image_plane_grid_stack=grid_stack)

fig, axes = plt.subplots(3, 1, figsize=(4, 12))
axes[0].imshow(tracer1.profile_image_plane_image_2d)
axes[1].imshow(tracer2.profile_image_plane_image_2d)
axes[2].imshow(tracer3.profile_image_plane_image_2d)
plt.tight_layout()
plt.show()