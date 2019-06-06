""" high-level access to mode projection functionality """

import numpy as np
import scipy.linalg as la

from ase import Atoms

from hilde.helpers.lattice_points import (
    map_I_to_iL,
    get_lattice_points,
    get_commensurate_q_points,
)
from hilde.helpers import Timer, progressbar
from hilde.helpers.numerics import clean_matrix
from hilde.structure.misc import get_sysname
from hilde.spglib.q_mesh import get_ir_reciprocal_mesh


from .displacements import get_U, get_dUdt
from .normal_modes import get_A_qst2, get_phi_qst, get_Zqst, projector as mode_projector


class HarmonicAnalysis:
    """ provide tools to perform harmonic analysis in periodic systems """

    def __init__(
        self,
        primitive,
        supercell,
        force_constants=None,
        lattice_points_frac=None,
        force_constants_supercell=None,
        q_points=None,
        verbose=False,
    ):
        """Initialize unit cell, supercell, force_constants and lattice points.

        Args:
            primitive (Atoms): unit cell
            supercell (Atoms): supercell
            force_constants (np.array): force constants as obtained from TDEP
                {inf,out}file.forceconstant
            lattice_points_frac (np.array): lattice points in fractional coordinates as
                obtained from TDEP {inf,out}file.forceconstant
            force_constants_supercell (np.array): force constants in the shape of the
                supercell (3N, 3N), e.g. obtained from infile.forceconstant_remapped

            """

        timer = Timer(f"Set up harmonic analysis for {get_sysname(primitive)}:")

        vbsty = {"verbose": verbose}

        self.primitive = primitive
        self.supercell = supercell

        # intialize
        self._dynamical_matrices = None
        self._irreducible_q_points = None
        self._irreducible_q_points_mapping = None

        # set or find lattice points, Cartesian and Fractional:
        if lattice_points_frac is not None:
            self.lattice_points_frac = lattice_points_frac
            lps = clean_matrix(lattice_points_frac @ self.primitive.cell)
            self.lattice_points = lps

        # set the lattice points that are contained in the supercell
        # these are in CARTESIAN coordinates!
        lattice_points, _ = get_lattice_points(primitive.cell, supercell.cell, **vbsty)
        self.lattice_points_supercell = lattice_points

        # get the map from supercell index I, to (i, L) as index in unit cell + lattice
        self.I_to_iL = map_I_to_iL(
            self.primitive, self.supercell, lattice_points=lattice_points
        )

        # Attach force constants in the shape fc[N_L, N_i, 3, N_j, 3]
        # and check dimensions
        self.force_constants = force_constants
        if self.force_constants is not None:
            fshape = self.force_constants.shape
            lshape = self.lattice_points.shape
            assert fshape[0] == lshape[0], (fshape, lshape)
            assert fshape[1] == fshape[3] == len(self.primitive), fshape
            assert fshape[2] == fshape[4] == 3, fshape
        else:
            print(f"** Force constants not set, your choice.")

        # Attach force constant matrix for supercell
        self.force_constants_supercell = force_constants_supercell

        # find commensurate q_points
        if q_points is None:
            self.q_points = get_commensurate_q_points(
                primitive.cell, supercell.cell, **vbsty
            )
        else:
            self.q_points = q_points

        # Write as property instead
        ## solve eigenvalue problem
        # self.omegas2, self.eigenvectors = self.diagonalize_dynamical_matrices()

        ## square root respecting the sign
        # self.omegas = np.sign(self.omegas2) * np.sqrt(abs(self.omegas2))

        # # find map from supercell to primitive + lattice point
        # self.indeces = map_I_to_iL(primitive, supercell)

        timer()

    @property
    def q_points_frac(self):
        """ return fractional q points w.r.t to primitive cell
        Fractional q points: frac_q = q . L.T """

        return clean_matrix(self.q_points @ self.primitive.cell.T)

    def set_irreducible_q_points(self, is_time_reversal=True, symprec=1e-5):
        """ determine the irreducible q grid in fractionals + mapping """

        fq_supercell = np.round(self.q_points @ self.supercell.cell.T).astype(int)

        mapping, ir_grid = get_ir_reciprocal_mesh(
            fq_supercell,
            self.primitive,
            self.supercell,
            is_time_reversal=is_time_reversal,
            symprec=symprec,
        )

        self._irreducible_q_points_mapping = mapping
        self._irreducible_q_points = ir_grid

    def get_irreducible_q_points_frac(self, is_time_reversal=True, symprec=1e-5):
        """ return the irreducible q grid in fractionals + mapping """

        if self._irreducible_q_points is None:
            self.set_irreducible_q_points(
                is_time_reversal=is_time_reversal, symprec=symprec
            )

        return self._irreducible_q_points

    def get_irreducible_q_points_mapping(self, is_time_reversal=True, symprec=1e-5):
        """ return the map from q points to irreducibe qpoints """
        if self._irreducible_q_points is None:
            self.set_irreducible_q_points(
                is_time_reversal=is_time_reversal, symprec=symprec
            )

        return self._irreducible_q_points_mapping

    @property
    def irreducible_q_points_mapping(self):
        """ return mapping from full to irred. q points """
        return self.get_irreducible_q_points_mapping()

    @property
    def irreducible_q_points(self):
        """ return irreducible qpoints in cartesian """
        ir_grid = self.get_irreducible_q_points_frac()

        return clean_matrix(ir_grid @ self.supercell.get_reciprocal_cell())

    @property
    def irreducible_q_points_frac(self):
        """ return irreducible qpoints in basis of the reciprocal lattice """
        ir_grid = self.irreducible_q_points

        return clean_matrix(ir_grid @ self.primitive.cell.T)

    def get_Dx(self):
        """ return mass-scaled force constants for each lattice point """
        na = len(self.primitive)
        fc = self.force_constants.reshape([-1, 3 * na, 3 * na])

        m = self.primitive.get_masses().repeat(3)

        return fc / np.sqrt(m[:, None] * m[None, :])

    def get_Dx_supercell(self):
        """ return mass-scaled hessian for supercell"""
        na = len(self.supercell)
        fc = self.force_constants_supercell.reshape(2 * [3 * na])

        m = self.supercell.get_masses().repeat(3)

        return fc / np.sqrt(m[:, None] * m[None, :])

    def get_Dq(self, q=np.array([0.0, 0.0, 0.0]), fractional=True):
        """ return dynamical matrix at q. """
        if fractional:
            phases = np.exp(2j * np.pi * self.lattice_points_frac @ q)
        else:
            phases = np.exp(2j * np.pi * self.lattice_points @ q)
        Dx = self.get_Dx()

        Dq = (phases[:, None, None] * Dx).sum(axis=0)

        # check for hermiticity
        assert la.norm(Dq - Dq.conj().T) < 1e-12

        if la.norm(Dq.imag) < 1e-12:
            return Dq.real

        return Dq

    def solve_Dq(self, q=np.array([0.0, 0.0, 0.0]), fractional=True):
        """ solve eigenvalue problem for dynamical matrix at q """

        Dq = self.get_Dq(q, fractional=fractional)

        w_2, ev = la.eigh(Dq)

        return w_2, ev

    def diagonalize_dynamical_matrices(self, q_points=None):
        """ solve eigenvalue problem for dyn. matrices at (commensurate) q-points """

        if q_points is None:
            q_points = self.q_points_frac

        omegas2, eigenvectors = [], []

        for q in q_points:
            w_2, ev = self.solve_Dq(q=q)
            omegas2.append(w_2)
            eigenvectors.append(ev)

        omegas2 = np.array(omegas2)
        eigenvectors = np.array(eigenvectors)

        return omegas2, eigenvectors

    @property
    def eigenvectors(self):
        """ return eigenvectors """
        _, eigenvectors = self.diagonalize_dynamical_matrices()
        return eigenvectors

    @property
    def omegas(self):
        """ return angular frequencies """
        omegas2, _ = self.diagonalize_dynamical_matrices()

        ## square root respecting the sign
        return np.sign(omegas2) * np.sqrt(abs(omegas2))

    @property
    def mode_projector(self):
        """ return unitary transformation for projecting displacements and velocities
            onto eigenmodes """

        kwargs = {
            "q_points": self.q_points,
            "lattice_points": self.lattice_points_supercell,
            "eigenvectors": self.eigenvectors,
            "indeces": self.I_to_iL,
        }

        proj = mode_projector(**kwargs, flat=True)

        return proj

    def get_Uqst(self, trajectory, displacements=True, velocities=True):
        """ Get the mode projected positions, weighted by mass.
            With `displacements=True`, return mode projected displacements.
            With `velocities=True`, return mode projected velocities.
        Returns:
            (U_qst, V_qst): tuple of np.ndarrays for mode projected displacements and
                velocities """

        print(f"Project trajectory onto modes:")
        shape = [len(trajectory), len(self.q_points), 3 * len(self.primitive)]
        Uqst = np.zeros(shape, dtype=complex)
        Vqst = np.zeros(shape, dtype=complex)

        proj = self.mode_projector

        atoms0 = self.supercell
        masses = trajectory[0].get_masses()
        for ii in progressbar(range(len(trajectory))):
            atoms = trajectory[ii]
            if displacements:
                Uqst[ii] = proj @ get_U(atoms, atoms0=atoms0, masses=masses).flatten()
            if velocities:
                Vqst[ii] = proj @ get_dUdt(atoms, masses=masses).flatten()

        return Uqst, Vqst

    def get_Zqst(self, trajectory):
        """ Return the imaginary mode amplitude for [t, q, s] """

        Uqst, Vqst = self.get_Uqst(trajectory)

        Z_qst = get_Zqst(Uqst, Vqst, self.omegas)

        return Z_qst

    def project(self, trajectory, times=None):
        """ perform mode projection for atoms objects in trajectory

        Return:
        Amplitdues, Angles, Energies in shape [q, s, t]
        """

        timer = Timer("Perform mode analysis for trajectory")

        if isinstance(trajectory, Atoms):
            trajectory = [trajectory]

        U_qst, V_qst = self.get_Uqst(trajectory)

        A_qst2 = get_A_qst2(U_qst, V_qst, self.omegas ** 2)
        phi_qst = get_phi_qst(U_qst, V_qst, self.omegas, in_times=times)

        E_qst = 0.5 * (self.omegas ** 2)[None, :, :] * A_qst2

        timer("project trajectory")

        return A_qst2, phi_qst, E_qst


# archive
# def get_Ut(self, trajectory, displacements=True, velocities=True, flat=True):
#     """ Get the positions, weighted by mass.
#         With `displacements=True`, return displacements.
#         With `velocities=True`, return velocities.
#     Returns:
#         (U_t, V_t): tuple of np.ndarrays, ready for mode projection """
#
#     print(f"Obtain mass weighted displacements and velocities:")
#     shape = [len(trajectory), *self.supercell.positions.shape]
#     Ut = np.zeros(shape)
#     Vt = np.zeros(shape)
#
#     atoms0 = self.supercell
#     masses = trajectory[0].get_masses()
#     for ii in progressbar(range(len(trajectory))):
#         atoms = trajectory[ii]
#         if displacements:
#             Ut[ii] = get_U(atoms, atoms0=atoms0, masses=masses)
#         if velocities:
#             Vt[ii] = get_dUdt(atoms, masses=masses)
#
#     if flat:
#         return Ut.reshape(len(trajectory), -1), Vt.reshape(len(trajectory), -1)
#     return Ut, Vt
