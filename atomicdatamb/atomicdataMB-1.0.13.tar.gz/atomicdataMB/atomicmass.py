"""
``atomicmass`` - Return the atomic mass of an atom or molecule.

This is really just a wrapper for
`periodictable
<https://periodictable.readthedocs.io/en/latest/index.html>`_
but returns the mass as an `astropy quantity
<http://docs.astropy.org/en/stable/units/index.html>`_.
"""
import sys
import periodictable as pt
from periodictable import formulas
import astropy.units as u


def atomicmass(species):
    r"""Return the atomic mass of an atom or molecule.

    **Parameters** 

    species
        Chemical formula requested species. See `periodictable
        <https://periodictable.readthedocs.io/en/latest/index.html>`_
        for formatting options.

    **Returns**

    output
        atomicmass of ``species`` as an astropy quantity with units = AMU
        :math:`(1\, \mathrm{AMU} = 1.660539 \times 10^{−27}\, \mathrm{kg})`
    """
    el = [e.symbol for e in pt.elements]
    if species in el:
        atom = eval('pt.' + species)
        mass = atom.mass * u.u
    else:
        try:
            mass = formulas.formula(species).mass * u.u
        except ValueError:
            print(f'WARNING: mathMB.atomicmass: {species} not found')
            mass = None
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    return mass
