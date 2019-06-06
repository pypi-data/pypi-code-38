"""Function that performs a k-grid optimization for a structure"""
from pathlib import Path

from ase.calculators.socketio import SocketIOCalculator

from hilde.k_grid.kpointoptimizer import KPointOptimizer
from hilde.helpers.converters import input2dict
from hilde.helpers.paths import cwd
from hilde.trajectory import metadata2file, step2file
from hilde.helpers.watchdogs import WallTimeWatchdog as Watchdog
from hilde.helpers.k_grid import k2d


def converge_kgrid(
    atoms,
    calc,
    func=lambda x: x.calc.get_property("energy", x) / len(x),
    loss_func=lambda x: x,
    dfunc_min=1e-12,
    even=True,
    maxsteps=100,
    trajectory="kpt_trajectory.son",
    logfile="kpoint_conv.log",
    socketio_port=None,
    walltime=None,
    workdir=".",
):
    """
    Converges the k-grid relative to some loss function
    Args:
        atoms: (ASE Atoms object) geometry of the system you are converging the k-grid on
        calc: (ASE Calculator object) calculator for the k-grid convergence
        func: (function) Function used to get the property the routine is trying to converge relative to the k-grid density
        loss_func: (function) Function used to transform the property obtained in func into a score to compare agsint
        dfunc_min: (float) Convergence criteria for the loss function
        even: (bool) If True kgrid must be even valued
        unit_cell: (bool) if True system is periodic
        maxsteps: (int) maximum steps to run the optimization over
        trajecotry: (str) file name to store the trajectory
        logfile: (str) file name for the log file
        socketio_port: (int) port number for interactions with the socket
        walltime: (int) length of the wall time for the job in seconds
        workdir: (str) working directory for the calculation
        kpts_density_init: (float) initial k-point density
    Returns: (bool) True if the convergence criteria is met
    """
    watchdog = Watchdog(walltime=walltime)

    workdir = Path(workdir).absolute()
    trajectory = workdir / trajectory

    kpt_settings = {
        "func": func,
        "loss_func": loss_func,
        "dfunc_min": dfunc_min,
        "even": even,
        "logfile": str(workdir / logfile),
    }
    if "k_grid" in calc.parameters:
        kpt_settings["kpts_density_init"] = k2d(atoms, calc.parameters["k_grid"])
    if socketio_port is None:
        socket_calc = None
    else:
        socket_calc = calc

    atoms.calc = calc
    opt_atoms = atoms

    with SocketIOCalculator(socket_calc, port=socketio_port) as iocalc, cwd(
        workdir / "calculation", mkdir=True
    ):
        if socketio_port is not None:
            atoms.calc = iocalc

        opt = KPointOptimizer(opt_atoms, **kpt_settings)
        # log very initial step and metadata
        if opt.nsteps == 0 and not trajectory.exists():
            metadata = input2dict(atoms, calc)
            metadata["geometry_optimization"] = opt.todict()
            metadata2file(metadata, trajectory)

        for _, converged in enumerate(opt.irun(steps=maxsteps)):
            step2file(atoms, atoms.calc, trajectory)
            if watchdog():
                break

    return converged, opt.kpts_density, calc
