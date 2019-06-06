""" helper utilities:
    - FCCalculator for using force constants to compute forces
    - Logger for tracking custom MD """
from pathlib import Path

from ase.calculators.calculator import Calculator

from hilde.harmonic_analysis.displacements import get_dR
from hilde.trajectory import son, input2dict


def get_F(dR, force_constants):
    """ Compute force from force_constants @ displacement """
    return -(force_constants @ dR.flatten()).reshape(dR.shape)


class FCCalculator(Calculator):
    """ Calculator that uses (2nd order) force constants to compute forces. """

    def __init__(self, ref_atoms, force_constants, **kwargs):
        super().__init__(**kwargs)
        self.implemented_properties = ["forces"]

        self.force_constants = force_constants
        self.atoms0 = ref_atoms

    def get_forces(self, atoms=None):
        dR = get_dR(atoms, self.atoms0)
        return get_F(dR, self.force_constants)


class MDLogger:
    """ MD logger class to write hilde trajectory files """

    def __init__(self, atoms, trajectory, metadata={}, overwrite=False):
        """ initialize """

        self.trajectory = trajectory
        if Path(trajectory).exists() and overwrite:
            Path(trajectory).unlink()
            print(f"** {trajectory} deleted.")

        son.dump({**metadata, **input2dict(atoms)}, self.trajectory, is_metadata=True)

    def __call__(self, atoms, info={}):
        """ log the current step to the trajectory """

        dct = {
            "atoms": {
                "cell": atoms.cell,
                "positions": atoms.positions,
                "velocities": atoms.get_velocities(),
            },
            "calculator": {"forces": atoms.get_forces()},
        }
        dct.update(info)

        son.dump(dct, self.trajectory)
