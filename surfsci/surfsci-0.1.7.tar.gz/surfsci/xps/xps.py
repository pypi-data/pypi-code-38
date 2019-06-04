# ISC License
#
# Copyright 2018 David Kalliecharan <dave@dal.ca>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
xps.py

X-Ray photoelectron spectroscopy (XPS) helper functions to adjust the
machine dependent intensities to Wagner intensities
"""

__author__  = 'David Kalliecharan'
__license__ = 'ISC License'
__status__  = 'Development'

from numpy import log10 as _log10
from numpy import poly1d as _poly1d
from pandas import DataFrame as _DataFrame

photon_energy = {
    'Mg' : 1253.6, # eV
    'Al' : 1486.6, # eV
}

mach_param = {
    'Dalhousie': {
        'coef'      : [0.9033, -4.0724, 5.0677, 1.1066],
        'scale'     : 0.01,
        'work_func' : 4.6,
    }
}

def kinetic_energy(be, hv, psi):
    """Calculates the kinetic energy (KE) with a Mg source (Dalhousie default):

    be  : binding energy (BE [eV])
    psi : Work function (Psi [eV])
    hv  : Phonton energy (h*nu [eV])
    """
    return hv - be - psi


def transmission(ke, pe, a, scale):
    """Dalhousie standard for the Transmission function

    ke    : Kinetic energy (KE [eV])
    pe    : Pass Energy (PE [eV])
    a     : List of coefficients for series expansion, _NOTE_ coefficents are
            reversed such that (aN, ..., a0) -> aN*x**N + ... + a0
            See documentation on numpy.poly1d
    scale : required scaling factor according to Avantage software
    """
    f = _poly1d(a)
    x = _log10(ke/pe)
    y = f(x)
    return scale*pe*10**y


def sf_machine(sf_wagner, transmission_mach, transmission_wagner):
    """Sensitivity factor for XPS machine correction from the Wagner XPS machine

    sf_wagner              : Wagner sensitivity factor
    transmission_mach      : Transmission function for the selected element
    transmission_wagner    : Wagner transmission function for the selected
                             element.
                             Proportional to 1/(kinetic_energy) [1/eV]
    """
    return sf_wagner*transmission_mach/transmission_wagner


def peak_correction(peak_area, sf_machine):
    """Corrected intensity of peak fitting by scaling to the sensitivity
    factor of the machine.

    peak_area   : peak area [CPS*eV]
    sf_machine  : sensitivity factor of xps machine
    """
    return peak_area/sf_machine


def matrix_factor(mfp_a, mfp_b, mfp_matrix_a, mfp_matrix_b, rho_a, rho_b):
    """Determines the matrix multiplicity factor. Mean free path values can be
found using an external program QUASES-IMFP-TPP2M.

    mfp_a        : Mean free path (mfp) of a in bulk, eg. mfp_a(KE_{Mn 2p3/2})
    mfp_b        : Mean free path (mfp) of b in bulk, eg. mfp_b(KE_{Co 2p3/2})
    mfp_matrix_a : Mean free path of matrix with kinetic energy of a
                   mfp_matirx(KE_{Mn 2p3/2})
    mfp_matrix_b : Mean free path of matrix with kinetic energy of b
                   mfp_matirx(KE_{Co 2p3/2})
    rho_a        : Density of species a
    rho_b        : Density of species b
    """
    a = mfp_matrix_a/mfp_a/rho_a
    b = mfp_matrix_b/mfp_b/rho_b
    return a/b


class XPSPeak():
    """XPSPeakBase class that conveniently wraps the base functions into an object
    peak_id    : Peak ID label
    be         : Binding energy [eV]
    peak_area  : Area of peak [CPS*eV]
    sf_wag     : Wagner sensitivity factor
    hv         : Photon energy
    pe         : Pass energy
    mach_param : Dictionary of XPS machine parameters:
                 coef      : [aN, aN-1, ..., a1, a0]
                 work_func : float [eV]
                 scale     : float
    """
    def __init__(self, peak_id, be, peak_area, sf_wagner, hv, pe, mach_param,
            *args, **kws):
        self.__peak_id = peak_id
        self.__be = be
        self.__peak_area = peak_area
        self.__sf_wagner = sf_wagner
        self.__hv = hv
        self.__pe = pe
        self.__a = mach_param['coef']
        self.__psi = mach_param['work_func']
        self.__scale = mach_param['scale']
        self.__args = args
        self.__kws = kws

    def get_kinetic_energy(self):
        return kinetic_energy(self.__be, self.__hv, self.__psi)

    def get_transmission(self):
        ke = self.get_kinetic_energy()
        return transmission(ke, self.__pe, self.__a, self.__scale)

    def get_sf_machine(self):
        ke = self.get_kinetic_energy()
        transmission_wagner = 1/ke # proportional to 1/KE
        if 'transmission_wagner' in self.__kws:
            self.transmission_wagner = self.__kws['transmission_wagner']

        tx_xps = self.get_transmission()
        return sf_machine(self.__sf_wagner, tx_xps, transmission_wagner)

    def get_peak_correction(self):
        sf_mach = self.get_sf_machine()
        return peak_correction(self.__peak_area, sf_mach)

    def get_mach_params(self):
        params = {
            'photon_energy' : self.__hv,
            'pass_energy'   : self.__pe,
            'coefficients'  : self.__a,
            'scale'         : self.__scale,
            'work_func'     : self.__psi,
        }
        return params

    def set_matrix_component(self, mfp, mfp_matrix, rho):
        """
    mfp        : Mean free path (mfp) in bulk, eg. mfp_a(KE_{Mn 2p3/2})
    mfp_matrix : Mean free path of matrix with kinetic energy of a
                   mfp_matirx(KE_{Mn 2p3/2})
    rho        : Density of material
        """
        self.__matrix_component = mfp_matrix/mfp/rho

    def df(self, return_dict=False):
        data_dict = {
            'peak_id'           : [self.__peak_id],
            'binding_energy'    : [self.__be],
            'kinetic_energy'    : [self.get_kinetic_energy()],
            'transmission_func' : [self.get_transmission()],
            'sf_wagner'         : [self.__sf_wagner],
            'sf_machine'        : [self.get_sf_machine()],
            'peak'              : [self.__peak_area],
            'peak_corrected'    : [self.get_peak_correction()],
        }

        if hasattr(self, '_XPSPeak__matrix_component'):
            data_dict['matrix_component'] = [self.__matrix_component]

        if return_dict == True:
            return data_dict
        return _DataFrame(data=data_dict)


if __name__ == '__main__':
    pass

