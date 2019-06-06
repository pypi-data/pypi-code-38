""" Relaxation.
 * Optimizers from ASE
 * SocketIO
 * Yaml Trajectory """

from hilde.settings import Settings
from hilde.templates.aims import setup_aims
from hilde.helpers.converters import input2dict


def metadata2dict(atoms, calc, opt):
    """ convert metadata information to plain dict """
    opt_dict = opt.todict()

    return {"geometry_optimization": opt_dict, **input2dict(atoms, calc)}


def run_relaxation(**kwargs):
    """ high level function to run relaxation """
    from .bfgs import relax as bfgs_relax

    args = bootstrap(**kwargs)

    completed = bfgs_relax(**args)

    if completed:
        print("done.")
    else:
        print("Relaxation not converged, please inspect.")
    return completed


def bootstrap(settings=None, **kwargs):
    """ load settings, prepare atoms, calculator, and optimizer """

    if settings is None:
        settings = Settings()

    if "atoms" not in kwargs:
        atoms = settings.get_atoms()
    else:
        atoms = kwargs["atoms"]

    relax_settings = {"atoms": atoms}

    if "relaxation" not in settings:
        warn(f"Settings do not contain relaxation instructions.", level=1)
    else:
        relax_settings.update(settings["relaxation"])

    # Optimizer preprocess
    relax_settings.update(kwargs)

    calc = kwargs.get("calculator", setup_aims(settings=settings, atoms=atoms))

    return {"atoms": atoms, "calculator": calc, **relax_settings}
