""" Provide a full highlevel phonopy workflow

    Input: geometry.in and settings.in
    Output: geometry.in.supercell and trajectory.son """

from hilde.settings import Settings
from hilde.templates.aims import setup_aims
from hilde.tasks import calculate_socket
from hilde.helpers.warnings import warn
from hilde.helpers.restarts import restart

from .postprocess import postprocess
from . import metadata2dict


def run_phonopy(**kwargs):
    """ high level function to run phonopy workflow """

    args = bootstrap(**kwargs)

    try:
        postprocess(**args)
        exit("** Postprocess could be performed from previous calculations. Check!")
    except (FileNotFoundError, RuntimeError):
        completed = calculate_socket(**args)

    if not completed:
        restart()
    else:
        print("Start postprocess.")
        postprocess(**args)
        print("done.")


def bootstrap(name="phonopy", settings=None, **kwargs):
    """ load settings, prepare atoms, calculator, and phonopy """

    if name.lower() == "phonopy":
        from hilde.phonopy.wrapper import preprocess
    elif name.lower() == "phono3py":
        from hilde.phono3py.wrapper import preprocess

    if settings is None:
        settings = Settings()

    if "atoms" not in kwargs:
        atoms = settings.get_atoms()
    else:
        atoms = kwargs["atoms"]

    phonopy_settings = {"atoms": atoms}

    if name not in settings:
        warn(f"Settings do not contain {name} instructions.", level=1)
    else:
        phonopy_settings.update(settings[name])

    # Phonopy preprocess
    phonopy_settings.update(kwargs)
    phonon, supercell, scs = preprocess(**phonopy_settings)

    calc = kwargs.get(
        "calculator",
        setup_aims(
            atoms=supercell, settings=settings, custom_settings={"compute_forces": True}
        ),
    )

    # save metadata
    metadata = metadata2dict(phonon, calc)

    return {
        "atoms_to_calculate": scs,
        "calculator": calc,
        "metadata": metadata,
        "workdir": name,
        **phonopy_settings,
    }
