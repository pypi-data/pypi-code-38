import getdist
import re
import os
import math
import numpy as np
from astropy import cosmology as cosmo
import matplotlib.pyplot as plt

from autolens.data.array import grids
from autolens.model.galaxy import galaxy
from autolens.model.profiles import light_profiles
from autolens.model.profiles import mass_profiles
from autolens.lens import ray_tracing


class SLACS(object):
            
    def __init__(self):

        cosmological_model = cosmo.LambdaCDM(H0=70, Om0=0.3, Ode0=0.7)
        cosmological_model = cosmo.Planck15

        self.redshift = 0.169
        self.source_redshift = 0.451
        self.critical_density_arcsec = 40246450650.700836
        self.einstein_radius = 1.91716
        self.source_light_min = 0.1
        self.source_light_max = 2.5

        self.arcsec_per_kpc = cosmological_model.arcsec_per_kpc(self.redshift).value
        self.kpc_per_arcsec = 1.0/self.arcsec_per_kpc

        # stop

    def setup_lensing_plane_sie(self, values):

        total_mass = mass_profiles.EllipticalIsothermal(centre=(values[0], values[1]), einstein_radius=values[2],
                                                        axis_ratio=values[3], phi=values[4])

        self.lens_galaxy = galaxy.Galaxy(redshift=self.redshift, sie=total_mass)
        self.source_galaxy = galaxy.Galaxy(redshift=self.source_redshift)

    def setup_lensing_plane_ltm2(self, values, center_skip, ltm_skip):

        sersic_bulge_light = light_profiles.EllipticalSersic(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4])

        exponential_halo_light = light_profiles.EllipticalExponential(axis_ratio=values[9 + center_skip],
                                                                   phi=values[10 + center_skip],
                                                                   intensity=values[7 + center_skip],
                                                                   effective_radius=values[8 + center_skip])

        sersic_bulge = mass_profiles.EllipticalSersic(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4],
                                                          mass_to_light_ratio=values[12 + center_skip])

        exponential_halo = mass_profiles.EllipticalExponential(axis_ratio=values[9 + center_skip],
                                                                   phi=values[10 + center_skip],
                                                                   intensity=values[7 + center_skip],
                                                                   effective_radius=values[8 + center_skip],
                                                                   mass_to_light_ratio=values[
                                                                    12 + ltm_skip + center_skip])

        dark_matter_halo = mass_profiles.SphericalNFW(kappa_s=values[11 + center_skip],
                                                      scale_radius=30.0*self.arcsec_per_kpc)

        self.lens_galaxy = galaxy.Galaxy(redshift=self.redshift, light1=sersic_bulge_light, light2=exponential_halo_light,
                                         bulge=sersic_bulge, envelope=exponential_halo, halo=dark_matter_halo)

        self.source_galaxy = galaxy.Galaxy(redshift=self.source_redshift)

    def setup_lensing_plane_ltm2r_bulge(self, values, center_skip, ltm_skip):

        sersic_bulge_light = light_profiles.EllipticalSersic(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4])

        exponential_halo_light = light_profiles.EllipticalExponential(axis_ratio=values[9 + center_skip],
                                                                   phi=values[10 + center_skip],
                                                                   intensity=values[7 + center_skip],
                                                                   effective_radius=values[8 + center_skip])

        sersic_bulge = mass_profiles.EllipticalSersicRadialGradient(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4],
                                                          mass_to_light_ratio=values[12 + center_skip],
                                                                    mass_to_light_gradient=values[
                                                                    13 + ltm_skip + center_skip])

        exponential_halo = mass_profiles.EllipticalSersic(axis_ratio=values[9 + center_skip],
                                                                            phi=values[10 + center_skip],
                                                                            intensity=values[7 + center_skip],
                                                                            effective_radius=values[8 + center_skip],
                                                                            sersic_index=1.0,
                                                                            mass_to_light_ratio=values[
                                                                    12 + ltm_skip + center_skip])

        dark_matter_halo = mass_profiles.SphericalNFW(kappa_s=values[11 + center_skip],
                                                      scale_radius=30.0*self.arcsec_per_kpc)

        self.lens_galaxy = galaxy.Galaxy(redshift=self.redshift, light1=sersic_bulge_light, light2=exponential_halo_light,
                                         bulge=sersic_bulge, envelope=exponential_halo, halo=dark_matter_halo)

        self.source_galaxy = galaxy.Galaxy(redshift=self.source_redshift)

    def setup_lensing_plane_ltm2r_envelope(self, values, center_skip, ltm_skip):

        sersic_bulge_light = light_profiles.EllipticalSersic(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4])

        exponential_halo_light = light_profiles.EllipticalExponential(axis_ratio=values[9 + center_skip],
                                                                   phi=values[10 + center_skip],
                                                                   intensity=values[7 + center_skip],
                                                                   effective_radius=values[8 + center_skip])

        sersic_bulge = mass_profiles.EllipticalSersic(centre=(values[0], values[1]), axis_ratio=values[5],
                                                          phi=values[6], intensity=values[2],
                                                          effective_radius=values[3],
                                                          sersic_index=values[4],
                                                          mass_to_light_ratio=values[12 + center_skip])

        exponential_halo = mass_profiles.EllipticalSersicRadialGradient(axis_ratio=values[9 + center_skip],
                                                                            phi=values[10 + center_skip],
                                                                            intensity=values[7 + center_skip],
                                                                            effective_radius=values[8 + center_skip],
                                                                            sersic_index=1.0,
                                                                            mass_to_light_ratio=values[
                                                                    12 + ltm_skip + center_skip],
                                                                            mass_to_light_gradient=values[
                                                                    13 + ltm_skip + center_skip])

        dark_matter_halo = mass_profiles.SphericalNFW(kappa_s=values[11 + center_skip],
                                                      scale_radius=30.0*self.arcsec_per_kpc)

        self.lens_galaxy = galaxy.Galaxy(redshift=self.redshift, light1=sersic_bulge_light, light2=exponential_halo_light,
                                         bulge=sersic_bulge, envelope=exponential_halo, halo=dark_matter_halo)

        self.source_galaxy = galaxy.Galaxy(redshift=self.source_redshift)

    def density_vs_radii_sie(self, values, radius_kpc, number_bins=60):

        self.setup_lensing_plane_sie(values)
        radii = list(np.linspace(5e-3, radius_kpc*self.arcsec_per_kpc, number_bins+1))

        self.sie_density_plot = []
        self.sie_density_upper_plot = []
        self.sie_density_lower_plot = []

        self.radii_plot = []

        for r in range(number_bins):

            annuli_area = (math.pi * radii[r + 1] ** 2 - math.pi * radii[r] ** 2)

            self.setup_lensing_plane_sie(values)

            sie_density = self.critical_density_arcsec * (self.lens_galaxy.sie.mass_within_circle_in_units(radii[r + 1]) -
                                                          self.lens_galaxy.sie.mass_within_circle_in_units(radii[r])) / annuli_area

            self.sie_density_plot.append(sie_density)

            self.radii_plot.append( ((radii[r+1] + radii[r]) / 2.0) * self.kpc_per_arcsec)

    def density_vs_radii_ltm2(self, values, radius_kpc, center_skip, ltm_skip, gradient=None, number_bins=60):

        if gradient is None:
            self.setup_lensing_plane_ltm2(values, center_skip, ltm_skip)
        elif gradient is 'bulge':
            self.setup_lensing_plane_ltm2r_bulge(values, center_skip, ltm_skip)
        elif gradient is 'envelope':
            self.setup_lensing_plane_ltm2r_envelope(values, center_skip, ltm_skip)

        radii = list(np.linspace(5e-3, radius_kpc*self.arcsec_per_kpc, number_bins+1))

        self.bulge_density_plot = []
        self.bulge_density_upper_plot = []
        self.bulge_density_lower_plot = []

        self.envelope_density_plot = []
        self.envelope_density_upper_plot = []
        self.envelope_density_lower_plot = []

        self.dark_density_plot = []
        self.dark_density_upper_plot = []
        self.dark_density_lower_plot = []

        self.radii_plot = []

        for r in range(number_bins):

            annuli_area = (math.pi * radii[r + 1] ** 2 - math.pi * radii[r] ** 2)

            if gradient is None:
                self.setup_lensing_plane_ltm2(values, center_skip, ltm_skip)
            elif gradient is 'bulge':
                self.setup_lensing_plane_ltm2r_bulge(values, center_skip, ltm_skip)
            elif gradient is 'envelope':
                self.setup_lensing_plane_ltm2r_envelope(values, center_skip, ltm_skip)

            bulge_density = self.critical_density_arcsec * (self.lens_galaxy.bulge.mass_within_circle_in_units(radii[r + 1]) -
                                                            self.lens_galaxy.bulge.mass_within_circle_in_units(radii[r])) / annuli_area

            envelope_density = self.critical_density_arcsec * (self.lens_galaxy.envelope.mass_within_circle_in_units(radii[r + 1]) -
                                                               self.lens_galaxy.envelope.mass_within_circle_in_units(radii[r])) / annuli_area

            halo_density = self.critical_density_arcsec * (self.lens_galaxy.halo.mass_within_circle_in_units(radii[r + 1]) -
                                                           self.lens_galaxy.halo.mass_within_circle_in_units(radii[r])) / annuli_area

            self.bulge_density_plot.append(bulge_density)
            self.envelope_density_plot.append(envelope_density)
            self.dark_density_plot.append(halo_density)

            self.radii_plot.append( ((radii[r+1] + radii[r]) / 2.0) * self.kpc_per_arcsec)

    def plot_density(self, image_name='', file_name='file', title='', labels=None, xaxis_is_physical=True, yaxis_is_physical=True):

        plt.figure(figsize=(10, 10))
        plt.title(title + image_name, size=18)

        if xaxis_is_physical:
            plt.xlabel('Distance From Galaxy Center (kpc)', size=20)
        else:
            plt.xlabel('Distance From Galaxy Center (")', size=20)

        if yaxis_is_physical:
            plt.ylabel(r'Surface Mass Density $\Sigma$ ($M_{\odot}$ / kpc $^2$)', size=20)
        else:
            pass

        self.decomposed_density_plot = list(map(lambda bulge, envelope, dark : bulge + envelope + dark,
                                                self.bulge_density_plot, self.envelope_density_plot, self.dark_density_plot))

        plt.semilogy(self.radii_plot, self.sie_density_plot, color='g', label='SIE')
        plt.semilogy(self.radii_plot, self.decomposed_density_plot, color='c', label='Decomposed Total')
        plt.semilogy(self.radii_plot, self.bulge_density_plot, color='r', linestyle='--', label='Sersic')
        plt.semilogy(self.radii_plot, self.envelope_density_plot, color='b', linestyle='--', label='Exponential')
        plt.semilogy(self.radii_plot, self.dark_density_plot, color='k', linestyle='--', label='Dark Matter')
        #
        # plt.semilogy(self.radii_plot, self.bulge_density_upper_plot, color='r', linestyle='--')
        # plt.semilogy(self.radii_plot, self.halo_density_upper_plot, color='g', linestyle='--')
        # plt.semilogy(self.radii_plot, self.dark_density_upper_plot, color='k', linestyle='--')
        #
        # plt.semilogy(self.radii_plot, self.bulge_density_lower_plot, color='r', linestyle='--')
        # plt.semilogy(self.radii_plot, self.halo_density_lower_plot, color='g', linestyle='--')
        # plt.semilogy(self.radii_plot, self.dark_density_lower_plot, color='k', linestyle='--')

        # plt.loglog(radii_plot, density_0, color='r', label='Sersic Bulge')
        # plt.loglog(radii_plot, density_1, color='g', label='EllipticalExponentialMass Halo')
        # plt.loglog(radii_plot, density_2, color='k', label='Dark Matter Halo')

        # plt.semilogy(radii_plot, density_lower[:, 0], color='r', linestyle='--')
        # plt.semilogy(radii_plot, density_upper[:, 0], color='r', linestyle='--')
        # plt.semilogy(radii_plot, density_lower[:, 1], color='g', linestyle='--')
        # plt.semilogy(radii_plot, density_upper[:, 1], color='g', linestyle='--')
        # plt.semilogy(radii_plot, density_lower[:, 2], color='k', linestyle='--')
        # plt.semilogy(radii_plot, density_upper[:, 2], color='k', linestyle='--')

        plt.axvline(x=self.einstein_radius*self.kpc_per_arcsec, linestyle='--')
        plt.axvline(x=self.source_light_min*self.kpc_per_arcsec, linestyle='-')
        plt.axvline(x=self.source_light_max*self.kpc_per_arcsec, linestyle='-')

        plt.tick_params(labelsize=16)
        plt.legend(fontsize=11.5)

        import os
        path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))
        plt.savefig(path + 'plots/' + file_name, bbox_inches='tight')
        plt.show()

    def masses_of_all_samples_sie(self, radius_kpc, values):

        self.setup_lensing_plane_sie(values=values)

        radius_arc = radius_kpc * self.arcsec_per_kpc
        sie_mass =  self.critical_density_arcsec * self.lens_galaxy.sie.mass_within_circle_in_units(radius=radius_arc)

        return sie_mass

    def masses_of_all_samples_ltm2(self, radius_kpc, values, center_skip, ltm_skip):

        self.setup_lensing_plane_ltm2(values=values, center_skip=center_skip, ltm_skip=ltm_skip)

        radius_arc = radius_kpc * self.arcsec_per_kpc
        bulge_mass =  self.critical_density_arcsec * self.lens_galaxy.bulge.mass_within_circle_in_units(radius=radius_arc)
        envelope_mass = self.critical_density_arcsec * self.lens_galaxy.envelope.mass_within_circle_in_units(radius=radius_arc)
        halo_mass = self.critical_density_arcsec * self.lens_galaxy.halo.mass_within_circle_in_units(radius=radius_arc)

        total_mass = bulge_mass + envelope_mass + halo_mass
        stellar_mass = (bulge_mass + envelope_mass)
        dark_mass = halo_mass

        return total_mass, stellar_mass, bulge_mass, envelope_mass, dark_mass

    def masses_of_all_samples_ltm2r_bulge(self, radius_kpc, values, center_skip, ltm_skip):

        self.setup_lensing_plane_ltm2r_bulge(values=values, center_skip=center_skip, ltm_skip=ltm_skip)

        radius_arc = radius_kpc * self.arcsec_per_kpc
        bulge_mass =  self.critical_density_arcsec * self.lens_galaxy.bulge.mass_within_circle_in_units(radius=radius_arc)
        envelope_mass = self.critical_density_arcsec * self.lens_galaxy.envelope.mass_within_circle_in_units(radius=radius_arc)
        halo_mass = self.critical_density_arcsec * self.lens_galaxy.halo.mass_within_circle_in_units(radius=radius_arc)

        total_mass = bulge_mass + envelope_mass + halo_mass
        stellar_mass = (bulge_mass + envelope_mass)
        dark_mass = halo_mass

        return total_mass, stellar_mass, bulge_mass, envelope_mass, dark_mass

    def masses_of_all_samples_ltm2r_envelope(self, radius_kpc, values, center_skip, ltm_skip):

        self.setup_lensing_plane_ltm2r_envelope(values=values, center_skip=center_skip, ltm_skip=ltm_skip)

        radius_arc = radius_kpc * self.arcsec_per_kpc
        bulge_mass =  self.critical_density_arcsec * self.lens_galaxy.bulge.mass_within_circle_in_units(radius=radius_arc)
        envelope_mass = self.critical_density_arcsec * self.lens_galaxy.envelope.mass_within_circle_in_units(radius=radius_arc)
        halo_mass = self.critical_density_arcsec * self.lens_galaxy.halo.mass_within_circle_in_units(radius=radius_arc)

        total_mass = bulge_mass + envelope_mass + halo_mass
        stellar_mass = (bulge_mass + envelope_mass)
        dark_mass = halo_mass

        return total_mass, stellar_mass, bulge_mass, envelope_mass, dark_mass