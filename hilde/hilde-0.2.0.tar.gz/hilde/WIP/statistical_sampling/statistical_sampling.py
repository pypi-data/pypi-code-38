"""Molecular Dynamics."""

import warnings
import numpy as np
from pathlib import Path

from ase.optimize.optimize import Dynamics
from ase.md.velocitydistribution import phonon_harmonics
from ase import units as u
from ase.utils.sobol import RandomState as QuasiRandomState

warnings.warn('this module can only work after ase MR 995 is accepted')

class Sampling(Dynamics):
    """Base-class for all statistical sampling classes."""
    def __init__(self, atoms, trajectory=None, logfile=None, loginterval=1):
        Dynamics.__init__(self, atoms, logfile=logfile, trajectory=trajectory)
        self.masses = self.atoms.get_masses()
        self.atoms_reference = self.atoms.copy()
        if 0 in self.masses:
            warnings.warn('Zero mass encountered in atoms; this will '
                          'likely lead to errors if the massless atoms '
                          'are unconstrained.')
        self.masses.shape = (-1, 1)

        # backup logfile
        if logfile:
            lf = Path(logfile)
            if lf.exists():
                log = lf.read_text()
                with open(logfile + '.bak', 'a') as f:
                    f.write(log)

    def todict(self):
        return {'type': 'statistical-sampling',
                'sampling-type': self.__class__.__name__}

    def irun(self, samples=10):
        """ Call Dynamics.irun """
        self.max_samples = samples + self.nsteps
        return Dynamics.irun(self)

    def run(self, samples=10):
        """ Call Dynamics.run"""
        self.max_samples = samples + self.nsteps
        return Dynamics.run(self)

    def converged(self):
        """ MD is 'converged' when number of maximum steps is reached. """
        return self.nsteps >= self.max_samples

    def log(self):
        """ log some data for testing """
        if self.logfile is not None:
            if self.nsteps == 0:
                self.logfile.write("   n   E_pot   E_kin   Temp\n")
                return
            a = self.atoms
            self.logfile.write('{:5d} {:.3f} {:.3f} {:.2f}\n'.format(
                self.nsteps, a.get_potential_energy(), a.get_kinetic_energy(),
                a.get_temperature()))
            self.logfile.flush()

class HarmonicSampling(Sampling):
    """ create samples from harmonic force constants """
    def __init__(self, atoms, force_constants, temperature=300*u.kB,
                 compute_forces=True,
                 quantum=False, failfast=True, quasi_random=False,
                 trajectory=None, logfile=None, loginterval=1):
        super().__init__(atoms, trajectory, logfile, loginterval)

        self.force_constants = force_constants
        self.temp = temperature
        self.compute_forces = compute_forces
        self.quasi_random = quasi_random
        self.quantum = quantum
        self.failfast = failfast

        if self.quasi_random:
            self.rng = QuasiRandomState(1, nmax=20000).rand
            # raise Exception('quasi random numbers not yet implemented')
        else:
            self.rng = np.random.rand


    def step(self, *args):
        """ create a sample and compute forces """

        force_constants = self.force_constants
        atoms = self.atoms
        temperature = self.temp

        d_ac, v_ac = phonon_harmonics(force_constants=force_constants,
                                      masses=atoms.get_masses(),
                                      temp=temperature,
                                      rng=self.rng,
                                      quantum=self.quantum,
                                      failfast=self.failfast)

        # Assign new positions (with displacements) and velocities
        atoms.positions = self.atoms_reference.positions + d_ac
        atoms.set_velocities(v_ac)

        if self.compute_forces:
            f = atoms.get_forces()
            return f
