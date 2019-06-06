"""
 Functions to run several related calculations with using trajectories as cache
"""
from pathlib import Path

from ase.calculators.socketio import SocketIOCalculator
from hilde import Settings
from hilde.helpers import talk
from hilde.helpers.compression import backup_folder as backup
from hilde.helpers.socketio import get_port
from hilde.helpers.watchdogs import WallTimeWatchdog as Watchdog
from hilde.trajectory import (
    get_hashes_from_trajectory,
    hash_atoms,
    metadata2file,
    step2file,
)

from hilde.helpers.paths import cwd

calc_dirname = "calculations"


def cells_and_workdirs(cells, base_dir):
    """ generate tuples of atoms object and workingdirectory path """
    for ii, cell in enumerate(cells):
        workdir = Path(base_dir) / f"{ii:05d}"
        yield cell, workdir


def calculate(atoms, calculator, workdir="."):
    """Short summary.
    Perform a dft calculation with ASE
    Args:
        atoms (Atoms or pAtoms): Structure.
        calculator (calculator): Calculator.
        workdir (folder): Folder to perform calculation in.

    Returns:
        int: 1 when error happened, otherwise None
    """
    if atoms is None:
        return atoms
    calc_atoms = atoms.copy()
    calc_atoms.calc = calculator
    with cwd(workdir, mkdir=True):
        calc_atoms.calc.calculate(calc_atoms)
    return calc_atoms


def calculate_multiple(cells, calculator, workdir):
    """Calculate several atoms object sharing the same calculator. """

    cells_calculated = []
    for cell, wdir in cells_and_workdirs(cells, workdir):
        if cell is None:
            cells_calculated.append(cell)
            continue
        if cell.calc is None:
            cell = calculate(cell, calculator, wdir)
        cells_calculated.append(cell)

    return cells_calculated


def setup_multiple(cells, calculator, workdir, mkdir):
    """
    Write input files for calculations on a list of atoms objects
    Args:
        cells (Atoms): List of atoms objects.
        calculator (calculator): Calculator to run calculation.
        workdir (str/Path): working directory
        mkdir(bool): if true make new directories for each calculation
    """
    workdirs = []
    for cell, wdir in cells_and_workdirs(cells, workdir):
        workdirs.append(wdir)
        if cell is None:
            continue
        cell.set_calculator(calculator)
        if mkdir:
            with cwd(wdir, mkdir=True):
                try:
                    calculator.write_input(cell)
                except AttributeError:
                    print("Calculator has no input just attaching to cell")
    return cells, workdirs


def calculate_socket(
    atoms_to_calculate,
    calculator,
    metadata=None,
    trajectory="trajectory.son",
    workdir="calculations",
    backup_folder="backups",
    **kwargs,
):
    """ perform calculations for a set of atoms objects """

    # take the literal settings for running the task
    settings = Settings()

    # create watchdog
    watchdog = Watchdog(**{"buffer": 1, **settings.watchdog, **kwargs})

    # create working directories
    workdir = Path(workdir)
    trajectory = (workdir / trajectory).absolute()
    backup_folder = workdir / backup_folder
    calc_dir = workdir / calc_dirname

    # perform backup if calculation folder exists
    if calc_dir.exists():
        backup(calc_dir, target_folder=backup_folder)

    # perform backup of settings
    with cwd(calc_dir, mkdir=True):
        settings.write()

    # save fist atoms object for computation
    atoms = atoms_to_calculate[0].copy()

    # handle the socketio
    socketio_port = get_port(calculator)
    if socketio_port is None:
        socket_calc = None
    else:
        socket_calc = calculator

    # fetch list of hashes from trajectory
    precomputed_hashes = get_hashes_from_trajectory(trajectory)

    # perform calculation
    n_cell = -1
    with cwd(calc_dir, mkdir=True):
        with SocketIOCalculator(socket_calc, port=socketio_port) as iocalc:
            if not precomputed_hashes:
                metadata2file(metadata, trajectory)

            if socketio_port is not None:
                calc = iocalc
            else:
                calc = calculator

                # fix for EMT calculator
                try:
                    calc.initialize(atoms)
                    talk("calculator initialized.")
                except AttributeError:
                    pass

            for n_cell, cell in enumerate(atoms_to_calculate):
                # skip if cell is None or already computed
                if cell is None:
                    continue
                if hash_atoms(cell) in precomputed_hashes:
                    continue

                # make sure a new calculation is started
                calc.results = {}
                atoms.calc = calc

                # update calculation_atoms and compute force
                atoms.info = cell.info
                atoms.positions = cell.positions
                atoms.calc.calculate(atoms, system_changes=["positions"])

                step2file(atoms, atoms.calc, trajectory)

                talk(f"computed structure {n_cell + 1} of {len(atoms_to_calculate)}")

                if watchdog():
                    break

    # backup and restart if necessary
    if n_cell < len(atoms_to_calculate) - 1:
        backup(calc_dir, target_folder=backup_folder)
        return False

    return True
