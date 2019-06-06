""" run molecular dynamics simulations using the ASE classes """

from pathlib import Path
from ase.calculators.socketio import SocketIOCalculator

from hilde.settings import Settings
from hilde.trajectory import step2file, metadata2file
from hilde.helpers.watchdogs import WallTimeWatchdog as Watchdog
from hilde.helpers.paths import cwd
from hilde.helpers.socketio import get_port, get_stresses
from hilde.helpers.socketio import socket_stress_on, socket_stress_off
from hilde.helpers.compression import backup_folder as backup
from hilde.helpers.restarts import restart
from hilde.helpers.warnings import warn
from hilde.templates.aims import setup_aims
from .initialization import setup_md
from . import metadata2dict


_calc_dirname = "calculations"


def run_md(logfile="md.log", **kwargs):
    """ high level function to run MD """

    args = bootstrap()

    md_settings = {"logfile": logfile, **args, **kwargs}

    atoms, md, _ = setup_md(**md_settings)

    md_settings.update({"atoms": atoms, "md": md})

    converged = run(**md_settings)

    if not converged:
        restart()
    else:
        print("done.")


def bootstrap():
    """ load settings, prepare atoms, calculator and MD algorithm """

    settings = Settings()
    atoms = settings.get_atoms()
    calc = setup_aims(settings=settings, custom_settings={"compute_forces": True})

    if "md" not in settings:
        warn("Settings do not contain MD instructions.", level=2)

    return {"atoms": atoms, "calc": calc, **settings.md}


def run(
    atoms,
    calc,
    md,
    compute_stresses=0,
    maxsteps=25000,
    trajectory="trajectory.son",
    metadata_file="md_metadata.yaml",
    workdir=".",
    backup_folder="backups",
    **kwargs,
):
    """ run and MD for a specific time  """

    # take the literal settings for running the task
    settings = Settings()

    # create watchdog
    watchdog = Watchdog(**{**settings.watchdog, **kwargs})

    # create working directories
    workdir = Path(workdir)
    trajectory = (workdir / trajectory).absolute()
    calc_dir = workdir / _calc_dirname
    backup_folder = workdir / backup_folder

    # make sure compute_stresses describes a step length
    if compute_stresses is True:
        compute_stresses = 1
    elif compute_stresses is False:
        compute_stresses = 0
    else:
        compute_stresses = int(compute_stresses)

    # atomic stresses
    if calc.name == "aims":
        if compute_stresses:
            warn(
                "Switch heat flux / atomic stress computation on. "
                + f"(Every {compute_stresses} steps)"
            )
            calc.parameters["compute_heat_flux"] = True

    # prepare the socketio stuff
    socketio_port = get_port(calc)
    if socketio_port is None:
        socket_calc = None
    else:
        socket_calc = calc
    atoms.calc = calc

    # backup previously computed data
    if calc_dir.exists():
        backup(calc_dir, target_folder=backup_folder)

    with SocketIOCalculator(socket_calc, port=socketio_port) as iocalc, cwd(
        calc_dir, mkdir=True
    ):

        if socketio_port is not None:
            atoms.calc = iocalc

        # store settings locally
        settings.write()

        # log very initial step and metadata
        metadata = metadata2dict(atoms, calc, md)
        if md.nsteps == 0:
            metadata2file(metadata, file=trajectory)
            atoms.info.update({"nsteps": md.nsteps, "dt": md.dt})
            # step2file(atoms, atoms.calc, trajectory)

        # store MD metadata locally
        metadata2file(metadata, file=metadata_file)

        print("\nStart MD.")

        while not watchdog() and md.nsteps < maxsteps:
            nsteps = md.nsteps

            md.run(1)

            if compute_stresses_now(compute_stresses, nsteps):
                stresses = get_stresses(atoms)
                atoms.calc.results["stresses"] = stresses

            atoms.info.update({"nsteps": md.nsteps, "dt": md.dt})
            step2file(atoms, atoms.calc, trajectory)

            if compute_stresses:
                if compute_stresses_next(compute_stresses, nsteps):
                    socket_stress_on(iocalc)
                else:
                    socket_stress_off(iocalc)

        print("Stop MD.\n")

    # restart
    if md.nsteps < maxsteps:
        return False
    return True


def compute_stresses_now(compute_stresses, nsteps):
    """ return if stress should be computed in this step """
    return compute_stresses and (nsteps % compute_stresses == 0)


def compute_stresses_next(compute_stresses, nsteps):
    """ return if stress should be computed in the NEXT step """
    return compute_stresses_now(compute_stresses, nsteps + 1)
