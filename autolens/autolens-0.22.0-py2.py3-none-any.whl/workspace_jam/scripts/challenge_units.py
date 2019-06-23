from astropy import cosmology
from astropy import constants
from astropy import units
from autolens.model.profiles import mass_profiles as mp

import numpy as np

cosmo = cosmology.FlatLambdaCDM(H0=70.0, Om0=0.3)

z_nfw = 0.6
z_source = 2.5

arc_per_kpc = cosmo.arcsec_per_kpc_proper(z=z_nfw)
H_l = cosmo.H0  # Hubble constant
G_l = constants.G
J_c = cosmo.critical_density(z=z_nfw)   # cosmic average density M_sun/kpc^(3)
C_v = constants.c

print('arc per kpc = ', arc_per_kpc)
print('H0 = ', H_l)
print('G = ', G_l)
print('Critical Density = ', J_c)
print('Speed of light = ', C_v)

s_crit = (C_v**2 * cosmo.angular_diameter_distance(z_source) /
          (4. * G_l * np.pi * cosmo.angular_diameter_distance(z_nfw) * cosmo.angular_diameter_distance_z1z2(z_nfw, z_source)))  # critical density

print()

print(s_crit.to('solMass / kpc^2'))
print(J_c.to('solMass / kpc^3'))
print(s_crit.to('solMass / kpc^2') / arc_per_kpc**2.0)
print(J_c.to('solMass / kpc^3') / arc_per_kpc**3.0)

stop

print()

mass_200 = 10**6
concentration = 11.5 * ((mass_200/10**10) + (mass_200/10**10)**2.0)**-0.05
print('Concentration 10**6 ', concentration)

mass_200 = 10**8
concentration = 11.5 * ((mass_200/10**10) + (mass_200/10**10)**2.0)**-0.05
print('Concentration 10**8 ', concentration)

mass_200 = 10**10
concentration = 11.5 * ((mass_200/10**10) + (mass_200/10**10)**2.0)**-0.05
print('Concentration 10**10 ', concentration)

nfw_challenge = mp.SphericalTruncatedNFWChallenge(kappa_s=0.003, scale_radius=0.1)
mass_at_200 = nfw_challenge.mass_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                  cosmic_average_density=262.30319684750657)
radius_at_200 = nfw_challenge.radius_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)
concentration = nfw_challenge.concentration_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)
mass_at_truncation_radius = nfw_challenge.mass_at_truncation_radius(critical_surface_density=1940654909.4133248,
                                                                    cosmic_average_density=262.30319684750657)

print(mass_200, radius_at_200, concentration, mass_at_truncation_radius)
stop

print()
print('mass = 10^6')
nfw_challenge = mp.SphericalTruncatedNFWChallenge(kappa_s=0.003, scale_radius=0.1)
mass_at_200 = nfw_challenge.mass_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                  cosmic_average_density=262.30319684750657)
concentration = nfw_challenge.concentration_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)


print("{:.4e}".format(mass_at_200[0]))
print(concentration)

print()
print('mass = 10^8')
nfw_challenge = mp.SphericalTruncatedNFWChallenge(kappa_s=0.01, scale_radius=0.5)
mass_at_200 = nfw_challenge.mass_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                  cosmic_average_density=262.30319684750657)
concentration = nfw_challenge.concentration_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)


print("{:.4e}".format(mass_at_200[0]))
print(concentration)

print()
print('mass = 10^10')
nfw_challenge = mp.SphericalTruncatedNFWChallenge(kappa_s=0.03, scale_radius=3.0)
mass_at_200 = nfw_challenge.mass_at_200_for_units(critical_surface_density=1940654909.4133248,
                                                  cosmic_average_density=262.30319684750657)
concentration = nfw_challenge.concentration_for_units(critical_surface_density=1940654909.4133248,
                                                      cosmic_average_density=262.30319684750657)


print("{:.4e}".format(mass_at_200[0]))
print(concentration)
