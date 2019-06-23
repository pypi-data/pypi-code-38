import sys
import numpy as np

from astropy import cosmology as cosmo
from astropy import constants

sys.path.append("../")

from workspace_jam.plotting.density_rj_lens_plots import density_plot_tools

slacs = density_plot_tools.SLACS()

image_dir = '/gpfs/data/pdtw24/PL_Data/RJLens3/'  # Dir of Object to make evidence tables from
image_name = 'Abell 1201'
file_name = 'density_decomposed_black_hole'
title = 'SIE + Decomposed (Black Hole) Density Profiles of '

number_bins = 50

## SIE ##

values = []
values.append(0.05247720) # Lens x
values.append(0.03497244) # Lens y
values.append(1.91716393) # Lens einR
values.append(0.68532604) # Lens axis ratio
values.append(66.83060729) # Lens phi

sie_mass_ein_r = slacs.masses_of_all_samples_sie(values=values, radius_kpc=slacs.einstein_radius * slacs.kpc_per_arcsec)
sie_mass_475 = slacs.masses_of_all_samples_sie(values=values, radius_kpc=4.75)
slacs.density_vs_radii_sie(radius_kpc=15.0, values=values, number_bins=number_bins)

### Decomposed Mis aligned model + BLACK HOLE###

center_skip = 2
ltm_skip = 1

values = []
values.append(0.01325835) # fg 1 x
values.append(0.03141879) # fg 1 y
values.append(0.19499256) # fg 1 intensity
values.append(0.55633797) # fg 1 eff rad
values.append(1.44111989) # fg 1 sersic inex
values.append(0.84441063) # fg 1 phi
values.append(72.90899614) # fg 1 axis ratio
values.append(0.10100496) # fg 2 x
values.append(0.08702267) # fg 2 y
values.append(0.03422805) # fg 2 intensity
values.append(4.56848742) # fg 2 effective radius
values.append(0.60149254) # fg 2 axis ratio
values.append(66.08021533) # fg 2 phi
values.append(0.05117416) # Lens Kappa s
values.append(2.25135624) # Lens MLR 1
values.append(4.87657708) # Lens MLR 2
values.append(0.40273428) # Lens Black hole EinR

total_mass, stellar_mass, bulge_mass, envelope_mass, dark_mass = slacs.masses_of_all_samples_ltm2(
    radius_kpc=slacs.einstein_radius * slacs.kpc_per_arcsec, values=values, center_skip=center_skip, ltm_skip=ltm_skip)

print('Masses as R_Ein (kpc) = ', slacs.einstein_radius * slacs.kpc_per_arcsec)
print()
print('SIE Mass = {:.3E}'.format(sie_mass_ein_r))
print('Total Decomposed Mass = {:.3E}'.format(total_mass))
print('Stellar Mass = {:.3E}'.format(stellar_mass))
print('Dark Mass = {:.3E}'.format(dark_mass))
print('Bulge Mass = {:.3E}'.format(bulge_mass))
print('Envelope Mass = {:.3E}'.format(envelope_mass))

total_mass, stellar_mass, bulge_mass, envelope_mass, dark_mass = slacs.masses_of_all_samples_ltm2(
    radius_kpc=4.75, values=values, center_skip=center_skip, ltm_skip=ltm_skip)

print('Masses as 4.75 kpc')
print()
print('SIE Mass = {:.3E}'.format(sie_mass_475))
print('Total Decomposed Mass = {:.3E}'.format(total_mass))
print('Stellar Mass = {:.3E}'.format(stellar_mass))
print('Dark Mass = {:.3E}'.format(dark_mass))
print('Bulge Mass = {:.3E}'.format(bulge_mass))
print('Envelope Mass = {:.3E}'.format(envelope_mass))

cosmology = cosmo.Planck15
a_to_earth = cosmology.angular_diameter_distance(z=slacs.redshift).to('kpc')
print(a_to_earth)
a_to_source = cosmology.angular_diameter_distance(z=slacs.source_redshift).to('kpc')
a_lens_to_source = cosmology.angular_diameter_distance_z1z2(z1=slacs.redshift, z2=slacs.source_redshift).to('kpc')
black_hole_mass = (((0.4027 * (constants.c.to('kpc / s')**2.0) /
                            (4.0 * constants.G.to('kpc3 / M_sun s2')))) * (a_lens_to_source/(a_to_earth*a_to_source)))
print('Black Hole Mass = {:.3E}'.format(black_hole_mass))
# stop

slacs.density_vs_radii_ltm2(radius_kpc=10.0, values=values, center_skip=2, ltm_skip=1, number_bins=number_bins)
slacs.plot_density(image_name=image_name, file_name=file_name, title=title, labels=['SIE', 'Sersic', 'Exponential', 'NFWSph'])

# model_indexes, sample_weights, total_masses, stellar_masses, bulge_masses, disk_masses, dark_masses = \
#      slacs.masses_of_all_samples(radius_kpc=10.0)