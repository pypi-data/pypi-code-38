from pathlib import Path

from ase.constraints import UnitCellFilter
from ase.calculators.socketio import SocketIOCalculator

from hilde.settings import Settings
from hilde.helpers.watchdogs import WallTimeWatchdog as Watchdog
from hilde.helpers.paths import cwd
from hilde.helpers.socketio import get_port
from hilde.trajectory import step2file, metadata2file
from hilde.helpers.structure import clean_atoms
from . import metadata2dict


_calc_dirname = "calculation"


def relax(
    atoms,
    calculator,
    linesearch=False,
    fmax=0.01,
    maxstep=0.2,
    unit_cell=True,
    cell_factor=None,
    maxsteps=100,
    trajectory="trajectory.son",
    logfile="relax.log",
    walltime=84400,
    workdir="bfgs",
    clean_output=True,
    output="geometry.in.relaxed",
    **kwargs,
):
    """ run a BFGS relaxation with ASE """

    if linesearch:
        from ase.optimize.bfgslinesearch import BFGSLineSearch as BFGS
    else:
        from ase.optimize.bfgs import BFGS

    watchdog = Watchdog(walltime=walltime, **kwargs)

    workdir = Path(workdir)
    trajectory = (workdir / trajectory).absolute()
    logfile = (workdir / logfile).absolute()
    calc_dir = workdir / _calc_dirname

    bfgs_settings = {"logfile": str(logfile), "maxstep": maxstep}

    # take the literal settings for running the task
    settings = Settings()

    if calculator.name == "aims":
        calculator.parameters["compute_forces"] = True
        calculator.parameters["compute_analytical_stress"] = bool(unit_cell)

    socketio_port = get_port(calculator)
    if socketio_port is None:
        socket_calc = None
    else:
        socket_calc = calculator

    atoms.calc = calculator

    if unit_cell:
        opt_atoms = UnitCellFilter(atoms, cell_factor=cell_factor)
    else:
        opt_atoms = atoms

    with SocketIOCalculator(socket_calc, port=socketio_port) as iocalc, cwd(
        calc_dir, mkdir=True
    ):
        if socketio_port is not None:
            atoms.calc = iocalc

        opt = BFGS(opt_atoms, **bfgs_settings)

        # log very initial step and metadata
        if opt.nsteps == 0:
            metadata = metadata2dict(atoms, calculator, opt)
            metadata2file(metadata, trajectory)
            settings.write()

        for _, converged in enumerate(opt.irun(fmax=fmax, steps=maxsteps)):
            atoms.info.update({"nsteps": opt.nsteps})
            step2file(atoms, atoms.calc, trajectory, append_cell=unit_cell)
            if watchdog():
                break

    with cwd(workdir):

        if clean_output:
            atoms = clean_atoms(atoms)

        atoms.write(
            output,
            format="aims",
            scaled=True,
            info_str=f"Relaxed with BFGS, fmax={fmax} eV/AA",
        )

    return converged
