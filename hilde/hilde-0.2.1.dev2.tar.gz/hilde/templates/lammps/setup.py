""" Provide a readily set up lammps calculator """

import os
from pathlib import Path
from ase.calculators.lammpsrun import LAMMPS

lmp_path = Path(os.getenv("LAMMPS_PATH"))

def setup_lammps_si(workdir):
    """Set up an ASE lammps calculator for silicon with Tersoff potential """
    # LAMMPS context information
    if isinstance(workdir, str):
        workdir = Path(workdir)
    potential = str(lmp_path / "potentials" / "Si.tersoff")
    files = [potential]
    parameters = {"mass": ["* 1.0"],
                  "pair_style": "tersoff",
                  "pair_coeff": ['* * ' + potential + ' Si']}

    # Logging
    lammps = LAMMPS(parameters=parameters,
                    files=files,
                    tmp_dir=workdir / 'lammps')

    return lammps

def setup_lammps_gan(workdir):
    if isinstance(workdir, str):
        workdir = Path(workdir)
    potential = str(lmp_path / "potentials" / "GaN.tersoff")
    files = [potential]
    parameters = {"mass": ["* 1.0"],
                  "pair_style": "tersoff",
                  "pair_coeff": ['* * ' +  potential + ' Ga N']}

    lammps = LAMMPS(parameters=parameters,
                    files=files,
                    tmp_dir=workdir / 'lammps')

    return lammps
