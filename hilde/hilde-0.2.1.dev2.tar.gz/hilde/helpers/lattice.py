""" Tools for dealing with lattices """

import scipy.linalg as la


def fractional(positions, lattice):
    """ compute fractioal components in terms of lattice

            r = r_frac . lattice

        =>  r_frac = r . inv_lattice

        """

    return positions @ la.inv(lattice)
