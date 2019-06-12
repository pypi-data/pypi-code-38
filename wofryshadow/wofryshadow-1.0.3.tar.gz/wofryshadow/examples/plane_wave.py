#
# example of SHADOW <-> GENERIC WAVEFRONT conversion
#
# First draft: plane wave


import Shadow

from wofryshadow.propagator.wavefront2D.shadow3_wavefront import SHADOW3Wavefront
from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

import scipy.constants as codata
m_to_eV = codata.h*codata.c/codata.e

from srxraylib.plot.gol import plot_image

import numpy


def create_wavefront_generic(size_factor=1,pixel_size=1e-6,wavelength=1.5e-10):

    w = GenericWavefront2D.initialize_wavefront_from_steps(x_start=-0.5*pixel_size*512*size_factor,x_step=pixel_size,
                                                           y_start=-0.5*pixel_size*512*size_factor,y_step=pixel_size,
                                                           number_of_points=(512*size_factor,512*size_factor),wavelength=wavelength)
    w.set_plane_wave_from_complex_amplitude(complex_amplitude=(1.0+0.0j))
    w.clip_square(x_min=-100e-6,x_max=100e-6,y_min=-10e-6,y_max=10e-6)
    return w


def create_wavefront_shadow3(width=200e-6,height=20e-6,
                                    divergence_h=0.0,divergence_v=0.0,
                                    wavelength=1.5e-10,
                                    number_of_rays=512*512,
                                    iwrite=False):

    photon_energy = m_to_eV / wavelength

    #
    # initialize shadow3 source (oe0) and beam
    #
    beam = Shadow.Beam()
    oe0 = Shadow.Source()

    #
    # Define variables. See meaning of variables in:
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/source.nml
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/oe.nml
    #

    oe0.FDISTR = 1
    oe0.FSOUR = 1
    oe0.F_COHER = 1
    oe0.F_PHOT = 0
    oe0.IDO_VX = 0
    oe0.IDO_VZ = 0
    oe0.IDO_X_S = 0
    oe0.IDO_Y_S = 0
    oe0.IDO_Z_S = 0
    oe0.PH1 = photon_energy

    oe0.HDIV1 = 0.5 * divergence_h
    oe0.HDIV2 = 0.5 * divergence_h
    oe0.VDIV1 = 0.5 * divergence_v
    oe0.VDIV2 = 0.5 * divergence_v
    oe0.WXSOU = width
    oe0.WZSOU = height
    oe0.NPOINT = number_of_rays

    #Run SHADOW to create the source

    if iwrite:
        oe0.write("start.00")

    beam.genSource(oe0)

    if iwrite:
        oe0.write("end.00")
        beam.write("begin.dat")


    return beam


def plot_wavefront_generic(w,show=True,title=None):
    z = w.get_intensity()
    x = w.get_coordinate_x()
    y = w.get_coordinate_y()
    a = w.get_phase()

    if title is None:
        title="WOFRY"

    plot_image(z,1e6*x,1e6*y,title=title+" Intensity",xtitle='x [um]',ytitle='y [um]',show=False)
    plot_image(a,1e6*x,1e6*y,title=title+" Phase",xtitle='x [um]',ytitle='y [um]',show=show)

def plot_wavefront_shadow3(w,nbins=None,title=""):

    if nbins == None:
        nbins = int(numpy.sqrt(w.nrays()))

    Shadow.ShadowTools.plotxy(w,1,3,nbins=nbins,title=title+" Real space")
    Shadow.ShadowTools.plotxy(w,4,6,nbins=nbins,title=title+" Divergence space")


if __name__ == "__main__":

    # # test initializer
    # wf3 = SHADOW3Wavefront(N=10000)
    # print(">>>> initializer, shape: ",wf3.rays.shape)
    #
    # # test init from beam
    # beam3 = create_wavefront_shadow3()
    # w3 = SHADOW3Wavefront.initialize_from_shadow3_beam(beam3)
    # Shadow.ShadowTools.plotxy(w3,1,3)


    #
    # GENERIC -> SHADOW
    #
    wfG = create_wavefront_generic()
    print(wfG.get_complex_amplitude().shape)
    plot_wavefront_generic(wfG,title='generic')
    print("total intensity",wfG.get_intensity().sum())
    #
    wf3 = SHADOW3Wavefront.fromGenericWavefront(wfG)
    plot_wavefront_shadow3(wf3,title='SHADOW')



    #
    # SHADOW ->  GENERIC
    #

    wf3 = create_wavefront_shadow3()
    wf3 = SHADOW3Wavefront.decorateSHADOW3WF(wf3)
    plot_wavefront_shadow3(wf3,title='SHADOW')

    wfG = wf3.toGenericWavefront(range_h=512e-6,range_v=512e-6)
    plot_wavefront_generic(wfG,title='generic')
