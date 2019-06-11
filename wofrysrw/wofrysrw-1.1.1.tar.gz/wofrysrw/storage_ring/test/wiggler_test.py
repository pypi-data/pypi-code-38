import numpy

from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.light_sources.srw_wiggler_light_source import SRWWigglerLightSource
from wofrysrw.storage_ring.srw_light_source import SourceWavefrontParameters, WavefrontPrecisionParameters

from srxraylib.plot.gol import plot, plot_contour, plot_surface

wiggler = SRWWigglerLightSource("XRD1",
                                electron_energy_in_GeV=2.0,
                                electron_energy_spread=0.0007,
                                ring_current=0.4,
                                electron_beam_size_h=0.05545e-3,
                                electron_beam_size_v=2.784e-6,
                                emittance=0.2525e-9,
                                coupling_costant=0.01,
                                K_vertical=20.9155,
                                period_length=0.064,
                                number_of_periods=24.5)

print(wiggler.get_electron_beam().get_electron_beam_geometrical_properties().to_info())


wf_parameters = SourceWavefrontParameters(photon_energy_min = 13000,
                                          photon_energy_max = 13000,
                                          photon_energy_points=1,
                                          h_slit_gap = 10e-3,
                                          v_slit_gap = 2e-3,
                                          h_slit_points=500,
                                          v_slit_points=50,
                                          distance = 10.0,
                                          wavefront_precision_parameters=WavefrontPrecisionParameters(sr_method=2,
                                                                                                      relative_precision=0.01,
                                                                                                      number_of_points_for_trajectory_calculation=20000,
                                                                                                      sampling_factor_for_adjusting_nx_ny=-1))

e, h, v, i = wiggler.get_intensity(source_wavefront_parameters=wf_parameters, multi_electron=False)


plot_contour(i[int(int(e.size/2))],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("XRD1",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]",plot_points=0,
             contour_levels=numpy.linspace(0, i.max(), 20), cmap=None, cbar=1,cbar_title="Flux ",show=1)

plot_surface(i[int(e.size/2)],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("XRD1",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]", show=1)