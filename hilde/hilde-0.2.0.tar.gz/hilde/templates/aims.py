""" Provide an aims calculator without much ado """
import shutil
from os import path
from pathlib import Path

# from ase.calculators.aims import Aims
from ase.calculators.aims import Aims
from hilde.settings import Settings
from hilde import DEFAULT_CONFIG_FILE
from hilde.helpers import talk
from hilde.helpers.k_grid import update_k_grid
from hilde.helpers.warnings import warn

def create_species_dir(atoms, settings, tmp_folder="basissets"):
    """ create a custom bassiset folder for the computation

    Args:
        atoms (Atoms): structure
        basissetloc (path): where to find basissets
        basissets (list): the individual basisset types
    """

    loc = Path(settings.machine.basissetloc)

    # if old section with `basisset.type` is used:
    if "basisset" in settings and "type" in settings.basisset:
        default = settings.basisset.type
        return str(loc / default)
    elif "basissets" in settings and "default" in settings.basissets:
        default = settings.basissets.default
    else:
        warn("basissets not specified in settings.file.", level=2)

    # return default if no atom is given for reference
    if atoms is None:
        default_path = loc / default
        talk(f"no Atoms object given, return default path {default_path} for basissets")
        return str(default_path)

    folder = Path(tmp_folder)
    folder.mkdir(exist_ok=True)

    symbols = atoms.get_chemical_symbols()
    numbers = atoms.symbols.numbers

    dct = {sym: num for (sym, num) in zip(symbols, numbers)}

    key_vals = (
        (key.capitalize(), val)
        for (key, val) in settings.basissets.items()
        if "default" not in key
    )

    if len(settings.basissets) > 1:
        for (key, val) in key_vals:
            # copy the respective basisset
            shutil.copy(loc / val / f"{dct[key]:02d}_{key}_default", folder)
            del dct[key]

    # add remaining ones
    for key in dct.keys():
        # copy the respective basisset
        shutil.copy(loc / default / f"{dct[key]:02d}_{key}_default", folder)

    return str(folder.absolute())


def setup_aims(
    atoms=None,
    settings=None,
    custom_settings={},
    workdir=None,
    config_file=DEFAULT_CONFIG_FILE,
    output_level="MD_light",
):
    """Set up an aims calculator.

    Args:
        atoms (Atoms): Atoms object that will be used for computation.
        settings (Settings): the hilde settings
        custom_settings (dict): for working interactively
        workdir (str): directory to work in
        config_file (str): path to config file
        output_level (str): the default output level if not specified explicitly

    Returns:
        Aims: ASE calculator object
    """

    if settings is None:
        settings = Settings(config_file)

    if atoms is None:
        atoms = settings.get_atoms()

    if "control" not in settings:
        msg = f"No [control] section in {config_file}, return calc=None, good luck!"
        talk(msg)
        return None

    default_settings = {"output_level": output_level, **settings.control}

    if not "output_level" in settings.control:
        talk("output_level MD_light has been set.")

    if "relativistic" not in default_settings:
        default_settings.update({"relativistic": "atomic_zora scalar"})
        talk("relativistic flag not set in settings.in, set to atomic_zora scalar")

    ase_settings = {"aims_command": settings.machine.aims_command}

    # Check if basisset type is supposed to be changed by custom settings
    if "species_type" in custom_settings:
        warn("Please use `settings.basissets` section in the config file.", level=2)

    if "socketio" in settings and settings.socketio.port is not None:
        custom_settings.update(
            {"use_pimd_wrapper": ("localhost", settings.socketio.port)}
        )
        if "use_socketio" in custom_settings:
            del custom_settings["use_socketio"]

    # create basissetfolder
    species_dir = create_species_dir(atoms, settings)
    ase_settings["species_dir"] = species_dir

    aims_settings = {**default_settings, **ase_settings, **custom_settings}

    if workdir:
        calc = Aims(label=Path(workdir).absolute(), **aims_settings)
    else:
        calc = Aims(**aims_settings)

    # update k_grid
    if atoms and "control_kpt" in settings:
        update_k_grid(atoms, calc, settings.control_kpt.density)

    if "k_grid" not in calc.parameters:
        talk("No k_grid in aims calculator. Check!")

    return calc
