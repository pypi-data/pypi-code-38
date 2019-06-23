import sys
import numpy as np

sys.path.append("../")

from workspace_jam.plotting.density_rj_lens_plots import density_plot_tools

slacs = density_plot_tools.SLACS()

image_dir = '/gpfs/data/pdtw24/PL_Data/RJLens3/'  # Dir of Object to make evidence tables from
image_name = 'Abell 1201'
file_name = 'density_decomposed_radial_gradient_disk'
title = 'SIE + Decomposed (Radial Gradient Disk) Density Profiles of '

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

### Decomposed Mis aligned model + Rad Grad Disk ###

center_skip = 2
ltm_skip = 1

values = []
values.append(0.01429371) # fg 1 x
values.append(0.03482821) # fg 1 y
values.append(0.19719856) # fg 1 intensity
values.append(0.54707512) # fg 1 eff rad
values.append(1.40547183) # fg 1 sersic inex
values.append(0.84835895) # fg 1 axis ratio
values.append(73.97940933) # fg 1 phi
values.append(0.10119909) # fg 2 x
values.append(0.08338715) # fg 2 y
values.append(0.03513022) # fg 2 intensity
values.append(4.47678502) # fg 2 effective radius
values.append(0.61034664) # fg 2 axis ratio
values.append(65.64533590) # fg 2 phi
values.append(0.02625320) # Lens Kappa s
values.append(6.14116954) # Lens MLR 1
values.append(4.95553279) # Lens MLR 2
values.append(-0.08614826) # Lens Grad

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

slacs.density_vs_radii_ltm2(radius_kpc=10.0, values=values, center_skip=2, ltm_skip=1, gradient='disk', number_bins=number_bins)
slacs.plot_density(image_name=image_name, file_name=file_name,  title=title, labels=['SIE', 'Sersic', 'Exponential', 'NFWSph'])

# model_indexes, sample_weights, total_masses, stellar_masses, bulge_masses, disk_masses, dark_masses = \
#      slacs.masses_of_all_samples(radius_kpc=10.0)