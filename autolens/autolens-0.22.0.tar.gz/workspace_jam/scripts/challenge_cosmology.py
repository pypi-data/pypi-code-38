from autolens.model import cosmology_util
from astropy import cosmology
from astropy import constants
import math

cosmo = cosmology.FlatLambdaCDM(H0=70.0, Om0=0.3)

const = constants.c.to('kpc / s') ** 2.0 / (4 * math.pi * constants.G.to('kpc3 / (solMass s2)'))

kpc_per_arcsec = cosmology_util.kpc_per_arcsec_from_redshift_and_cosmology(redshift=0.6,
                                                            cosmology=cosmo)

print(const / kpc_per_arcsec)
print(1.0 / const)

print(const)

stop

ang_lens_to_earth = cosmology_util.angular_diameter_distance_to_earth_from_redshift_and_cosmology(
    redshift=0.6, cosmology=cosmo)

ang_source_to_earth = cosmology_util.angular_diameter_distance_to_earth_from_redshift_and_cosmology(
    redshift=2.5, cosmology=cosmo)

ang_lens_to_source = cosmology_util.angular_diameter_distance_between_redshifts_from_redshifts_and_cosmlology(
    redshift_0=0.6, redshift_1=2.5, cosmology=cosmo)

print('Ang lens to earth = ', ang_lens_to_earth)
print('Ang source to earth = ', ang_source_to_earth)
print('Ang lens to source = ', ang_lens_to_source)

print(ang_lens_to_earth / ang_lens_to_source)