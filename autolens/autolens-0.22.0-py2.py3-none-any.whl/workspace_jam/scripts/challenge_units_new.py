from astropy import cosmology
from astropy import constants
from astropy import units
from autolens.model.profiles import mass_profiles as mp

import numpy as np

from astropy import cosmology

cosmo = cosmology.FlatLambdaCDM(H0=70.0, Om0=0.3)

z_nfw = 0.6
z_source = 2.5

nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.119, scale_radius=0.052)

concentration = nfw.concentration_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

mass_at_200 = nfw.mass_at_200_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

print('Concentration = ', concentration)
print('Mass at 200 = {:.4e}'.format(mass_at_200))

nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.08, scale_radius=0.3)

concentration = nfw.concentration_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

mass_at_200 = nfw.mass_at_200_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

print('Concentration = ', concentration)
print('Mass at 200 = {:.4e}'.format(mass_at_200))

nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.01, scale_radius=0.07)

concentration = nfw.concentration_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

mass_at_200 = nfw.mass_at_200_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

print('Concentration = ', concentration)
print('Mass at 200 = {:.4e}'.format(mass_at_200))


nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.002, scale_radius=0.02)

concentration = nfw.concentration_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

mass_at_200 = nfw.mass_at_200_for_units(redshift_profile=z_nfw, redshift_source=z_source, unit_length='kpc',
                                     unit_mass='solMass', redshift_of_cosmic_average_density='profile',
                                     cosmology=cosmo)

print('Concentration = ', concentration)
print('Mass at 200 = {:.4e}'.format(mass_at_200))