from autolens.data.array import grids
from autolens.model.profiles import mass_profiles as mp
from autolens.model.profiles.plotters import profile_plotters

import numpy as np

regular_grid = grids.RegularGrid.from_shape_and_pixel_scale(shape=(800, 800), pixel_scale=0.1)

nfw_challenge = mp.SphericalTruncatedNFWChallenge(kappa_s=0.009, scale_radius=0.5)
mass_at_200 = nfw_challenge.mass_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                  cosmic_average_density=262.30319684750657)
concentration = nfw_challenge.concentration_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)


print("{:.4e}".format(mass_at_200))
print(concentration)

deflections = nfw_challenge.deflections_from_grid(grid=regular_grid)
print('defl y max = ' + str(np.max(deflections[:,0])))
print('defl x max = ' + str(np.max(deflections[:,1])))
print('defl r max = ' + str(np.max(np.sqrt(deflections[:,1]**2.0 + deflections[:,0]**2.0))))

profile_plotters.plot_deflections_x(mass_profile=nfw_challenge, grid=regular_grid)
profile_plotters.plot_deflections_y(mass_profile=nfw_challenge, grid=regular_grid)
