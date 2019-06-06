""" prepare molecular dynamics simulations using the ASE classes """

from ase import units as u
from hilde.helpers.converters import input2dict, results2dict


def metadata2dict(atoms, calc, md):
    """ convert metadata information to plain dict """

    md_dict = md.todict()
    # save time and mass unit
    md_dict.update({"fs": u.fs, "kB": u.kB, "dt": md.dt, "kg": u.kg})

    return {"MD": md_dict, **input2dict(atoms, calc)}


from .workflow import run_md
from .initialization import initialize_md
