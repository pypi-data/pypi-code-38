import numpy

from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.light_sources.srw_undulator_light_source import SRWUndulatorLightSource
from wofrysrw.storage_ring.srw_light_source import SourceWavefrontParameters

from srxraylib.plot.gol import plot, plot_contour, plot_surface

period_length=0.02
harmonic = 7

undulator = SRWUndulatorLightSource("MicroXRD",
                                    electron_energy_in_GeV=2.0,
                                    electron_energy_spread=0.0007,
                                    ring_current=0.4,
                                    electron_beam_size_h=0.05545e-3,
                                    electron_beam_size_v=2.784e-6,
                                    emittance=0.2525e-9,
                                    coupling_costant=0.01,
                                    K_vertical=1.5,
                                    period_length=period_length,
                                    number_of_periods=int(1.5/period_length))

print(undulator.get_electron_beam().get_electron_beam_geometrical_properties().to_info())

resonance_energy = undulator.get_resonance_energy()

print("Harmonic Energy", resonance_energy*harmonic)

properties = undulator.get_photon_source_properties(harmonic=harmonic)

print(properties.to_info())

wf_parameters = SourceWavefrontParameters(photon_energy_min = resonance_energy*harmonic,
                                          photon_energy_max = resonance_energy*harmonic,
                                          photon_energy_points=1,
                                          h_slit_gap = 0.005,
                                          v_slit_gap = 0.005,
                                          h_slit_points=51,
                                          v_slit_points=51,
                                          distance = 10.0)

e, h, v, i = undulator.get_intensity(source_wavefront_parameters=wf_parameters)

plot_contour(i[int(e.size/2)],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("MicroXRD",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]",plot_points=0,
             contour_levels=numpy.linspace(0, i.max(), 20), cmap=None, cbar=1, cbar_title="Intensity [ph/s/.1%bw/mm^2]",show=1)

plot_surface(i[int(e.size/2)],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("MicroXRD",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]", show=1)

# ------------------------------------------
'''
wf_parameters = SourceWavefrontParameters(photon_energy_min = 1,
                                          photon_energy_max = 12001,
                                          photon_energy_points=12000,
                                          h_slit_gap = 0.001,
                                          v_slit_gap = 0.001,
                                          h_slit_points=10,
                                          v_slit_points=50,
                                          distance = 10.0)

e, i = undulator.get_spectral_flux(source_wavefront_parameters=wf_parameters, multi_electron=True)

plot(e, i, show=1, title="Flux for MicroXRD", xtitle="Energy [eV]",  ytitle="Flux [ph/s/.1%bw]")
'''

wf_parameters = SourceWavefrontParameters(photon_energy_min = 1,
                                          photon_energy_max = 12001,
                                          photon_energy_points=12000,
                                          h_slit_gap = 0.001,
                                          v_slit_gap = 0.001,
                                          h_slit_points=1,
                                          v_slit_points=1,
                                          distance = 10.0)

e, i = undulator.get_undulator_flux(source_wavefront_parameters=wf_parameters)

plot(e, i, show=1, title="Flux for MicroXRD", xtitle="Energy [eV]",  ytitle="Flux [ph/s/.1%bw]")

# ------------------------------------------

wf_parameters = SourceWavefrontParameters(h_slit_gap = 0.005,
                                          v_slit_gap = 0.005,
                                          h_slit_points=51,
                                          v_slit_points=51,
                                          distance = 10.0)

h, v, p = undulator.get_power_density(source_wavefront_parameters=wf_parameters)

total_power = SRWLightSource.get_total_power_from_power_density(h, v, p)

plot_contour(p, h*1e3, v*1e3,title="%s SRW, total power = %g"%("Micro XRD", total_power),xtitle="H [mm]",ytitle="V [mm]",plot_points=0,
             contour_levels=numpy.linspace(0,numpy.max([p.max()]), 100), cmap=None,cbar=1, cbar_title="Power density [$W/mm^2$]",show=1)

plot_surface(p,h*1e3,v*1e3,  title="%s SRW, total power = %g"%("Micro XRD", total_power),xtitle="H [mm]",ytitle="V [mm]",show=1)


