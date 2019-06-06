""" tools for storing MD trajectories

Logic:
* save md metadata to new trajectory
* append each md step afterwards

"""

import os
import json
import shutil

import numpy as np


from ase import units
from hilde import __version__ as version
from hilde import son
from hilde.helpers.converters import results2dict, dict2atoms, input2dict
from hilde.helpers.converters import dict2json as dumper
from hilde.helpers.hash import hash_atoms
from hilde.helpers import Timer, warn, progressbar


def step2file(atoms, calc=None, file="trajectory.son", append_cell=False):
    """ Save the current step """

    dct = results2dict(atoms, calc, append_cell)

    son.dump(dct, file, dumper=dumper)


def metadata2file(metadata, file="metadata.son"):
    """ save metadata to file """

    if metadata is None:
        metadata = {}

    son.dump({**metadata, "hilde": {"version": version}}, file, is_metadata=True)


def get_hashes_from_trajectory(trajectory):
    """ return all hashes from trajectory """

    try:
        traj = reader(trajectory)
    except (FileNotFoundError, KeyError):
        return []

    hashes = []
    for atoms in traj:
        try:
            hashes.append(atoms.info["hash"])
        except (KeyError, AttributeError):
            hashes.append(hash_atoms(atoms))

    return hashes


def reader(file="trajectory.son", get_metadata=False):
    """ convert information in trajectory and metadata files to atoms objects
     and return them """

    timer = Timer(f"Parse trajectory in {file}")

    print(".. read file:")
    try:
        metadata, pre_trajectory = son.load(file)
    except json.decoder.JSONDecodeError:
        metadata, pre_trajectory = son.load(file)

    pre_calc_dict = metadata["calculator"]
    pre_atoms_dict = metadata["atoms"]

    if "numbers" in pre_atoms_dict and "symbols" in pre_atoms_dict:
        del pre_atoms_dict["symbols"]

    if "MD" in metadata:
        md_metadata = metadata["MD"]

    trajectory = Trajectory(metadata=metadata)
    print(".. process file:")
    for obj in progressbar(pre_trajectory):

        atoms_dict = {**pre_atoms_dict, **obj["atoms"]}

        # remember that the results need to go to a dedicated results dict in calc
        calc_dict = {**pre_calc_dict, "results": obj["calculator"]}

        atoms = dict2atoms(atoms_dict, calc_dict)

        # info
        if "MD" in metadata:
            if "dt" in atoms.info:
                atoms.info["dt_fs"] = atoms.info["dt"] / md_metadata["fs"]
        elif "info" in obj:
            info = obj["info"]
            atoms.info.update(info)

        # compatibility with older trajectories
        if "MD" in obj:
            atoms.info.update(obj["MD"])

        trajectory.append(atoms)

    timer()

    if get_metadata:
        return trajectory, metadata
    return trajectory


class Trajectory(list):
    """ A Trajectory is basically a list of Atoms objects with some functionality, e.g.
           - extract and plot several statistics on the MD trajectory
           - convert to other formats like xyz or TDEP """

    def __init__(self, *args, metadata=None):
        super().__init__(*args)

        if metadata:
            self._metadata = metadata
        else:
            self._metadata = {}

    @classmethod
    def from_file(cls, file):
        """ Read trajectory from file """
        trajectory = reader(file)
        return trajectory

    @property
    def metadata(self):
        """ Return metadata """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """ Set the metadata """
        assert isinstance(metadata, dict)
        self._metadata = metadata

    #     fkdev: Might be useful?
    #     @property
    #     def ref_atoms(self):
    #         """ Reference atoms object for computing displacements etc """
    #         if "supercell" in self.metadata:
    #             return dict2atoms(self.metadata["supercell"]["atoms"])
    #         else:
    #             return self[0]

    @property
    def primitive(self):
        """ Return the primitive cell if it is there """
        if "primitive" in self.metadata:
            return dict2atoms(self.metadata["primitive"]["atoms"])
        warn("primitive cell not provided in trajectory metadata")

    @primitive.setter
    def primitive(self, atoms):
        """ Set the supercell atoms object """
        dct = input2dict(atoms)

        self.metadata["primitive"] = dct
        print(".. primitive added to metadata.")

    @property
    def supercell(self):
        """ Return the supercell if it is there """
        if "supercell" in self.metadata:
            return dict2atoms(self.metadata["supercell"]["atoms"])
        warn("supercell not provided in trajectory metadata")

    @supercell.setter
    def supercell(self, atoms):
        """ Set the supercell atoms object """
        dct = input2dict(atoms)

        self.metadata["supercell"] = dct
        print(".. supercell added to metadata.")

    @property
    def times(self):
        """ return the times as numpy array """
        try:
            fs = self.metadata["MD"]["fs"]
        except KeyError:
            warn("time unit not found in trajectory metadata, use ase.units.fs")
            fs = units.fs

        times = np.cumsum([a.info["dt"] * fs for a in self])
        return times

    @property
    def temperatures(self):
        """ return the temperatues as 1d array """
        return np.array([a.get_temperature() for a in self])

    def clean_drift(self):
        """ Clean constant drift CAUTION: respect ASE time unit correctly! """

        timer = Timer("Clean trajectory from constant drift")

        p_drift = np.mean([a.get_momenta().sum(axis=0) for a in self], axis=0)

        print(f".. drift momentum is {p_drift}")

        for atoms, time in zip(self, self.times):
            atoms.set_momenta(atoms.get_momenta() - p_drift / len(atoms))

            # the displacement
            disp = p_drift / atoms.get_masses().sum() * time
            atoms.positions = atoms.positions - disp

        timer("velocities and positions cleaned from drift")

    def write(self, file="trajectory.son"):
        """ Write to son file """

        timer = Timer(f"Write trajectory to {file}")

        temp_file = "temp.son"

        # check for file and make backup
        if os.path.exists(file):
            ofile = f"{file}.bak"
            shutil.copy(file, ofile)
            print(f".. {file} copied to {ofile}")

        metadata2file(self.metadata, temp_file)

        print(f"Write to {temp_file}:")
        for elem in progressbar(self):
            son.dump(results2dict(elem), temp_file)

        shutil.move(temp_file, file)

        timer()

    def to_xyz(self, file="positions.xyz"):
        """ Write positions to simple xyz file for e.g. viewing with VMD """
        from ase.io.xyz import simple_write_xyz

        with open(file, "w") as fo:
            simple_write_xyz(fo, self)

    def to_tdep(self, folder=".", skip=1):
        """ Convert to TDEP infiles for direct processing """
        from pathlib import Path
        from contextlib import ExitStack

        folder = Path(folder)
        folder.mkdir(exist_ok=True)

        print(f"Write tdep input files to {folder}:")

        # meta
        n_atoms = len(self[0])
        n_steps = len(self) - skip
        try:
            dt = self.metadata["MD"]["timestep"] / self.metadata["MD"]["fs"]
            T0 = self.metadata["MD"]["temperature"] / units.kB
        except KeyError:
            dt = 1.0
            T0 = 0

        lines = [f"{n_atoms}", f"{n_steps}", f"{dt}", f"{T0}"]

        fname = folder / "infile.meta"

        with fname.open("w") as fo:
            fo.write("\n".join(lines))
            print(f".. {fname} written.")

        # supercell and fake unit cell
        write_settings = {"format": "vasp", "direct": True, "vasp5": True}
        if self.primitive:
            fname = folder / "infile.ucposcar"
            self.primitive.write(str(fname), **write_settings)
            print(f".. {fname} written.")
        if self.supercell:
            fname = folder / "infile.ssposcar"
            self.supercell.write(str(fname), **write_settings)
            print(f".. {fname} written.")

        with ExitStack() as stack:
            pdir = folder / "infile.positions"
            fdir = folder / "infile.forces"
            sdir = folder / "infile.stat"
            fp = stack.enter_context(pdir.open("w"))
            ff = stack.enter_context(fdir.open("w"))
            fs = stack.enter_context(sdir.open("w"))

            for ii, atoms in enumerate(self[skip:]):
                # stress and pressure in GPa
                try:
                    stress = atoms.get_stress(voigt=True) / units.GPa
                    pressure = -1 / 3 * sum(stress[:3])
                except:
                    stress = np.zeros(6)
                    pressure = 0.0
                e_tot = atoms.get_total_energy()
                e_kin = atoms.get_kinetic_energy()
                e_pot = e_tot - e_kin
                temp = atoms.get_temperature()

                for spos in atoms.get_scaled_positions():
                    fp.write("{} {} {}\n".format(*spos))

                for force in atoms.get_forces():
                    ff.write("{} {} {}\n".format(*force))

                stat = (
                    f"{ii:5d} {ii*dt:10.2f} {e_tot:20.8f} {e_pot:20.8f} "
                    f"{e_kin:20.15f} {temp:20.15f} {pressure:20.15f} "
                )
                stat += " ".join([str(s) for s in stress])

                fs.write(f"{stat}\n")

        print(f".. {sdir} written.")
        print(f".. {pdir} written.")
        print(f".. {fdir} written.")

    def get_average_displacements(self, ref_atoms=None, window=-1):
        """ Return averaged displacements """

        from hilde.harmonic_analysis.displacements import get_dR

        # reference atoms
        if not ref_atoms:
            if "supercell" in self.metadata:
                ref_atoms = dict2atoms(self.metadata["supercell"]["atoms"])
            else:
                ref_atoms = self[0]

        # this will hold the averaged displacement
        avg_displacement = np.zeros_like(ref_atoms.get_positions())

        weigth = 1 / len(self)

        for atoms in self:
            avg_displacement += weigth * get_dR(ref_atoms, atoms)

        return avg_displacement

    def get_average_positions(self, ref_atoms=None, window=-1, wrap=False):
        """ Return averaged positions """

        # reference atoms
        if not ref_atoms:
            if "supercell" in self.metadata:
                ref_atoms = dict2atoms(self.metadata["supercell"]["atoms"])
            else:
                ref_atoms = self[0]

        avg_displacement = self.get_average_displacements(
            ref_atoms=ref_atoms, window=window
        )

        avg_atoms = ref_atoms.copy()
        avg_atoms.positions += avg_displacement

        if wrap:
            avg_atoms.wrap()

        return avg_atoms.get_positions()
