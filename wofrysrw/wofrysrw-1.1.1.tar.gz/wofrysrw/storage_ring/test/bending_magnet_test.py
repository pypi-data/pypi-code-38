import numpy

from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.light_sources.srw_bending_magnet_light_source import SRWBendingMagnetLightSource
from wofrysrw.storage_ring.srw_light_source import SourceWavefrontParameters, SRWPrecisionParameters

from srxraylib.plot.gol import plot, plot_contour, plot_surface

period_length=0.14

bm = SRWBendingMagnetLightSource("MCX",
                      electron_energy_in_GeV=2.0,
                      electron_energy_spread=0.0007,
                      ring_current=0.4,
                      electron_beam_size_h=0.05545e-3,
                      electron_beam_size_v=2.784e-6,
                      emittance=0.2525e-9,
                      coupling_costant=0.01,
                      magnetic_field=1.2,
                      length=0.2)

print(bm.get_electron_beam().get_electron_beam_geometrical_properties().to_info())

wf_parameters = SourceWavefrontParameters(photon_energy_min = 13000,
                                          photon_energy_max = 13000,
                                          photon_energy_points=1,
                                          h_slit_gap = 20e-3,
                                          v_slit_gap = 2e-3,
                                          h_slit_points=100,
                                          v_slit_points=10,
                                          distance = 10.0,
                                          srw_precision_parameters=SRWPrecisionParameters(relative_precision=0.001))

e, h, v, i = bm.get_intensity(bm.get_SRW_Wavefront(wf_parameters))


plot_contour(i[int(int(e.size/2))],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("MCX",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]",plot_points=0,
             contour_levels=numpy.linspace(0, i.max(), 20), cmap=None, cbar=1,cbar_title="Flux ",show=1)

plot_surface(i[int(e.size/2)],h*1e3,v*1e3,title="%s SRW; E=%g eV"%("MCX",e[int(e.size/2)]),xtitle="H [mm]",ytitle="V [mm]",show=1)
