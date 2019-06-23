from autofit import conf
import os

workspace_path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=workspace_path + 'config', output_path=workspace_path + 'output')

from autolens.model.profiles import mass_profiles as mp

cosmology_util.angular_diameter_distance_between_redshifts_from_redshifts_and_cosmlology()



nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.033, scale_radius=0.169)
# nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.017, scale_radius=0.44)

sigma_cr = 1940654909.4133248
cos_den = 262.30319684750657

mass = nfw.mass_at_200_for_units(critical_surface_density=sigma_cr, cosmic_average_density=cos_den)
con = nfw.concentration_for_units(critical_surface_density=sigma_cr, cosmic_average_density=cos_den)
print('level 0 - large_hi_sn_system_1')
print("mass = {:.4e}, concentration = {:.4f} \n".format(mass, con))

nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.011, scale_radius=0.819)
nfw = mp.SphericalTruncatedNFWChallenge(kappa_s=0.016, scale_radius=0.389)

sigma_cr = 1940654909.4133248
cos_den = 262.30319684750657

mass = nfw.mass_at_200_for_units(critical_surface_density=sigma_cr, cosmic_average_density=cos_den)
con = nfw.concentration_for_units(critical_surface_density=sigma_cr, cosmic_average_density=cos_den)
print('level 0 - small_hi_sn_system_1')
print("mass = {:.4e}, concentration = {:.4f} \n".format(mass, con))