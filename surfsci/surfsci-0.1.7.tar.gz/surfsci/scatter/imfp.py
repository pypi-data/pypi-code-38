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
imfp.py

Equations relating to the Inelastic Mean Free Path (IMFP) of electrons

References
----------
IMFP TPP-2M (TPP-2 modified eqution)
    S. Tanuma, C. J. Powell, D. R. Penn: Surf. Interf. Anal.,Vol. 21, 165 (1994)
"""

from numpy import log as _log
from numpy import sqrt as _sqrt

def imfp_TPP2M(Ek, rho, M, Nv, Eg, units='Angstroms'):
    """The TPP-2M is the modified TPP-2 equation for estimating inelastic
    mean free paths (IMFP)

    S. Tanuma, C. J. Powell, D. R. Penn: Surf. Interf. Anal.,Vol. 21, 165 (1994)

    Ek    : Kinetic energy [eV]
    rho   : Density (g/cm**3)
    M     : Atomic or molar mass
    Nv    : Valence electrons
    Eg    : Bandgap energy [eV]
    units : 'Angstroms' or 'SI' [default: AA, or 1E-10 m]

    returns IMFP in Angstroms or meters [default: AA, or 1E-10 m]
    """
    # NOTE gamma, betaM, U, C, D are fitting parameters as in ref.
    U = Nv*rho/M
    C = 1.97 - 0.91*U
    D = 53.4 - 20.8*U
    Eplasmon = _sqrt(829.4*U)
    gamma = 0.191*rho**-0.50
    betaM = -0.10 + 0.944/_sqrt(Eplasmon**2 + Eg**2) + 0.069*rho**0.1

    imfp = Ek/(Eplasmon**2*(betaM*_log(gamma*Ek) - C/Ek+ D/Ek**2))

    if units.upper() == 'SI':
        # Convert to meters
        return imfp*1E-10
    # Leave units unmodified in Angstroms
    return imfp

if __name__ == '__main__':
    pass

