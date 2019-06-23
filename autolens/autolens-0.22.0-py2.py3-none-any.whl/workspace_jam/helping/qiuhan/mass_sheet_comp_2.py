from autolens.data import ccd
from autolens.data.array import grids
from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp

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

tracer_ref = ray_tracing.TracerMultiPlanes(
        galaxies=[lens_galaxy, source_galaxy],
        image_plane_grid_stack=image_plane_grid_stack, cosmology=cosmo)

print(tracer_ref.grid_at_redshift_from_image_plane_grid_and_redshift(image_plane_grid=image_plane_grid_stack.regular,
                                                                     redshift=1.0))

tracer_test = ray_tracing.TracerMultiPlanes(
        galaxies=[lens_galaxy, mass_sheet, source_galaxy],
        image_plane_grid_stack=image_plane_grid_stack, cosmology=cosmo)

print(tracer_test.grid_at_redshift_from_image_plane_grid_and_redshift(image_plane_grid=image_plane_grid_stack.regular,
                                                                      redshift=1.0))
