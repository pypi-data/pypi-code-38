""" Tools for hashing atoms objects """

from json import dumps
from pathlib import Path
from configparser import ConfigParser
from hashlib import sha1 as hash_sha
from .converters import atoms2dict, atoms2json, get_json, dict2json


def hashfunc(string, empty_str="", digest=True):
    """ Wrap the sha hash function and check for empty objects """
    if string in ("", "[]", "{}", "None"):
        string = empty_str
    if digest:
        return hash_sha(string.encode("utf8")).hexdigest()
    return hash_sha(string.encode("utf8"))


def hash_atoms(atoms):
    """hash the atoms object as it would be written to trajectory"""
    a = atoms.copy()
    a.info = {}

    rep = dict2json(atoms2dict(a))

    atoms_hash = hashfunc(rep)

    return atoms_hash


def hash_atoms_and_calc(
    atoms,
    ignore_results=True,
    ignore_keys=["unique_id", "info"],
    ignore_calc_params=[],
    ignore_file=None,
):
    """ Hash atoms and calculator object, with possible ignores"""

    if ignore_file is not None:
        fil = Path(ignore_file)
        if fil.exists():
            configparser = ConfigParser()
            configparser.read(fil)
            ignores = configparser["hash_ignore"]

            ignore_keys += [key for key in ignores if not ignores.getboolean(key)]

            ignore_calc_params = [key for key in ignores if not ignores.getboolean(key)]

    atomsjson, calcjson = atoms2json(
        atoms, ignore_results, ignore_keys, ignore_calc_params
    )

    atomshash = hashfunc(atomsjson)
    calchash = hashfunc(calcjson)

    return atomshash, calchash


def hash_traj(ca, meta, hash_meta=False):
    ca_dct = [atoms2json(at) for at in ca]
    dct = dict(meta, calculated_atoms=ca_dct)
    if hash_meta:
        return hashfunc(dumps(dct)), hashfunc(dumps(meta))
    return hashfunc(dumps(dct))


def hash_dict(dct):
    if "calculator_parameters" in dct:
        if "species_dir" in dct["calculator_parameters"]:
            dct["calculator_parameters"]["species_dir"] = Path(
                dct["calculator_parameters"]["species_dir"]
            ).parts[-1]

    return hashfunc(get_json(dct))
