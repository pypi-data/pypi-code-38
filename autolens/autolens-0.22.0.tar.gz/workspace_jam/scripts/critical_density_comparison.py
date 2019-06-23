from astropy import cosmology
from scipy.optimize import fsolve
from autolens.model.profiles import mass_profiles as mp
from astropy import constants
import numpy as np

from autolens.model import cosmology_util

cosmo=cosmology.FlatLambdaCDM(H0=70.0, Om0=0.3)

z_lens = 0.6
z_source = 2.5

C_v = constants.c.to('km / s')
G_crit = 4.302e-6  # kpc M_sun^-1 (km/s)^2
G_crit = constants.G.to( 'kpc km2 / (solMass s2)')

s_crit = (C_v * C_v * cosmo.angular_diameter_distance(z_source) / (4. * np.pi * cosmo.angular_diameter_distance(z_lens) *
           cosmo.angular_diameter_distance_z1z2(z_lens, z_source)) /
          (1000.0 * G_crit))  # critical density at los halo

const = (C_v * C_v) / (4 * np.pi) / (1000.0 * G_crit)

print(const)

angs = (cosmo.angular_diameter_distance(z_source) / (cosmo.angular_diameter_distance(z_lens) *cosmo.angular_diameter_distance_z1z2(z_lens, z_source)))

s_crit_al = cosmology_util.critical_surface_density_between_redshifts_from_redshifts_and_cosmology(
    redshift_0=z_lens, redshift_1=z_source, cosmology=cosmo, unit_length='kpc', unit_mass='solMass')

print(s_crit)
print(s_crit_al)