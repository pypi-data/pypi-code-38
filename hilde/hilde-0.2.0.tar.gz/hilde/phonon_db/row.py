"""
A file defining a row object for the phonon database
"""
import numpy as np
import re

from ase.db.row import AtomsRow, atoms2dict
from ase.io.jsonio import decode

from spglib import get_spacegroup

from hilde import konstanten as const
from hilde.phonon_db.ase_converters import dict2atoms
from hilde.materials_fp.material_fingerprint import get_phonon_bs_fingerprint_phononpy
from hilde.materials_fp.material_fingerprint import get_phonon_dos_fingerprint_phononpy
from hilde.materials_fp.material_fingerprint import to_dict
from hilde.structure.convert import to_Atoms, to_phonopy_atoms


def phonon_to_dict(phonon, to_mongo=False, add_fc=False):
    """
    Converts a phonopy object to a dictionary
    Args:
        phonon: the phonopy object to be converted
        to_mongo: True if it is being sent to a mongo database
    Returns:
        dct: the dictionary representation of phonon
    """
    dct = atoms2dict(to_Atoms(phonon.get_primitive()))
    dct["symprec"] = phonon._symprec
    if phonon.get_supercell_matrix() is not None:
        dct["sc_matrix_2"] = list(
            np.array(phonon.get_supercell_matrix()).transpose().flatten()
        )
        dct["natoms_in_sc_2"] = len(dct["numbers"]) * int(
            round(np.linalg.det(phonon.get_supercell_matrix()))
        )
    if not add_fc:
        dct["forces_2"] = []
        for disp1 in phonon._displacement_dataset["first_atoms"]:
            if "forces" in disp1:
                dct["forces_2"].append(disp1.pop("forces"))

        dct["forces_2"] = np.array(dct["forces_2"])
    else:
        n_atoms = phonon.get_supercell().get_number_of_atoms()
        dct["_fc_2"] = np.array(phonon.get_force_constants())
    dct["displacement_dataset_2"] = phonon._displacement_dataset

    if phonon.mesh is not None:
        dct["qmesh"] = phonon.mesh.mesh_numbers
    if phonon._total_dos is not None:
        dct["phonon_dos_fp"] = to_dict(get_phonon_dos_fingerprint_phononpy(phonon))

    if phonon.band_structure is not None:
        dct["qpoints"] = {}
        for ii, q_pt in enumerate(phonon.band_structure.qpoints):
            if list(q_pt[0]) not in dct["qpoints"].values():
                dct["qpoints"][phonon.band_structure.distances[ii][0]] = list(q_pt[0])
            if list(q_pt[-1]) not in dct["qpoints"].values():
                dct["qpoints"][phonon.band_structure.distances[ii][-1]] = list(q_pt[-1])
        dct["phonon_bs_fp"] = to_dict(
            get_phonon_bs_fingerprint_phononpy(phonon, dct["qpoints"]), to_mongo
        )
        if to_mongo and "qpoints" in dct:
            q_pt = {}
            for pt in dct["qpoints"]:
                q_pt[re.sub("[.]", "_", str(pt))] = dct["qpoints"][pt]
            dct["qpoints"] = q_pt
    if phonon.thermal_properties is not None:
        dct["tp_ZPE"] = phonon.thermal_properties.zero_point_energy
        dct["tp_high_T_S"] = phonon.thermal_properties.high_T_entropy
        dct["tp_T"], dct["tp_A"], dct["tp_S"], dct[
            "tp_Cv"
        ] = phonon.get_thermal_properties()
    return dct

def phonon3_to_dict(phonon3, store_second_order=False, to_mongo=False):
    """
    Converts a phonopy object to a dictionary
    Args:
        phonon: the phonopy object to be converted
        to_mongo: True if it is being sent to a mongo database
    Returns:
        dct: the dictionary representation of phonon
    """
    dct = atoms2dict(to_Atoms(phonon3.get_primitive()))
    dct["symprec"] = phonon3._symprec

    if phonon3.get_supercell_matrix() is not None:
        dct["sc_matrix_3"] = list(
            np.array(phonon3.get_supercell_matrix()).transpose().flatten()
        )
        dct["natoms_in_sc_3"] = len(dct["numbers"]) * int(
            round(np.linalg.det(phonon3.get_supercell_matrix()))
        )

    if phonon3._phonon_supercell_matrix is not None and store_second_order:
        dct["sc_matrix_2"] = list(
            np.array(phonon3._phonon_supercell_matrix).transpose().flatten()
        )
        dct["natoms_in_sc_2"] = len(dct["numbers"]) * int(
            round(np.linalg.det(phonon3._phonon_supercell_matrix))
        )

    dct["forces_3"] = []
    get_forces = True
    for disp1 in phonon3._displacement_dataset["first_atoms"]:
        if "forces" in disp1:
            if disp1["forces"].shape[0] == dct["natoms_in_sc_3"]:
                dct["forces_3"].append(disp1.pop("forces"))
            else:
                get_forces = False
                break

    if get_forces:
        for ii, disp1 in enumerate(phonon3._displacement_dataset["first_atoms"]):
            for disp2 in disp1["second_atoms"]:
                if "delta_forces" in disp2:
                    dct["forces_3"].append(
                        disp2.pop("delta_forces") + dct["forces_3"][ii]
                    )
    else:
        print(
            "Warning not storing forces as number of atoms in the supercell are not consistent"
        )
        dct["forces_3"] = []

    dct["forces_3"] = np.array(dct["forces_3"])
    dct["displacement_dataset_3"] = phonon3._displacement_dataset

    if phonon3.get_thermal_conductivity():
        dct["tp_T"] = phonon3.get_thermal_conductivity().get_temperatures()
        dct["tp_kappa"] = phonon3.get_thermal_conductivity().get_kappa()[0]
        dct["qmesh"] = phonon3.get_thermal_conductivity().get_mesh_numbers()

    return dct

class PhononRow(AtomsRow):
    """
    Class that is largely based off of the ASE AtomsRow object but expanded for phonopy
    """

    def __init__(self, dct=None, phonon3=None, phonon=None, store_second_order=False):
        """
        Constructor for the PhononRow.
        Args:
            dct: a phonopy object or a dict
                representation of the phonopy object to be added to the database
        """
        if dct:
            dct = dct.copy()
            if "sc_matrix_2" in dct and isinstance(dct["sc_matrix_2"], np.ndarray):
                dct["sc_matrix_2"] = list(dct["sc_matrix_2"].flatten())
            elif (
                "sc_matrix_2" in dct
                and isinstance(dct["sc_matrix_2"], list)
                and isinstance(dct["sc_matrix_2"][0], str)
            ):
                for i, sc_el in enumerate(dct["sc_matrix_2"]):
                    dct["sc_matrix_2"][i] = int(sc_el)
            if "sc_matrix_3" in dct and isinstance(dct["sc_matrix_3"], np.ndarray):
                dct["sc_matrix_3"] = list(dct["sc_matrix_3"].flatten())
            elif (
                "sc_matrix_3" in dct
                and isinstance(dct["sc_matrix_3"], list)
                and isinstance(dct["sc_matrix_3"][0], str)
            ):
                for i, sc_el in enumerate(dct["sc_matrix_3"]):
                    dct["sc_matrix_3"][i] = int(sc_el)
        elif phonon3:
            dct = phonon3_to_dict(phonon3, store_second_order)
        elif phonon:
            dct = phonon_to_dict(phonon)
        else:
            raise AttributeError("dct, phonon3 or phonon must be defined")
        assert "numbers" in dct
        assert "cell" in dct
        try:
            symprec = dct["symprec"] if "symprec" in dct else 1e-5
            dct["space_group"] = get_spacegroup(dict2atoms(dct), symprec=symprec)
            kvp = dct.pop("key_value_pairs", {})
            kvp["space_group"] = dct["space_group"]
        except AttributeError:
            kvp = dct.pop("key_value_pairs", {})
        self._constraints = dct.pop("constraints", [])
        self._constrained_forces = None
        self._data = dct.pop("data", {})
        # If the dictionary has additional keys that are not default add them here
        self._keys = list(kvp.keys())
        self.__dict__.update(kvp)
        self.__dict__.update(dct)
        self.clean_displacement_dataset()

    def clean_displacement_dataset(self):
        if "displacement_dataset_2" in self and self.displacement_dataset_2 is not None:
            for disp1 in self.displacement_dataset_2["first_atoms"]:
                disp1["number"] = int(disp1["number"])
        if "displacement_dataset_3" in self and self.displacement_dataset_3 is not None:
            for ii, disp1 in enumerate(self.displacement_dataset_3["first_atoms"]):
                disp1["number"] = int(disp1["number"])
                for disp2 in disp1["second_atoms"]:
                    disp2["number"] = int(disp2["number"])

    @property
    def fc_2(self):
        if "_fc_2" in self:
            return self._fc_2
        else:
            self.__dict__["_fc_2"] = self.get_fc_2()
            return self._fc_2

    def get_fc_2(self):
        from phonopy import Phonopy
        phonon = Phonopy(
            to_phonopy_atoms(self.toatoms()),
            supercell_matrix=np.array(self.sc_matrix_2).reshape(3, 3),
            symprec=self.symprec,
            is_symmetry=True,
            factor=const.omega_to_THz,
            log_level=0,
        )
        phonon.set_displacement_dataset(self.displacement_dataset_2)
        if "forces_2" in self and len(self.forces_2) > 0:
            phonon.produce_force_constants(self.forces_2)
        return phonon.get_force_constants()

    @property
    def fc_3(self):
        if "_fc_3" in self:
            return self._fc_3
        else:
            self.__dict__["_fc_3"] = self.get_fc_3()
            return self._fc_3

    def get_fc_3(self):
        from phono3py.phonon3 import Phono3py

        phonon3 = Phono3py(
            to_phonopy_atoms(self.toatoms()),
            supercell_matrix=np.array(self.sc_matrix_3).reshape(3, 3),
            phonon_supercell_matrix=np.array(self.sc_matrix_2).reshape(3, 3),
            symprec=self.symprec,
            is_symmetry=True,
            frequency_factor_to_THz=const.omega_to_THz,
            log_level=0,
            mesh=self.qmesh,
        )
        phonon3._phonon_displacement_dataset = self.displacement_dataset_2.copy()
        phonon3.set_displacement_dataset(self.displacement_dataset_3)

        if "forces_3" in self and len(self.forces_3) > 0:
            phonon3.produce_fc3(self.forces_3)
        return phonon3.get_fc3()

    def to_phonon(self):
        """
        Converts the row back into a phonopy object
        Returns:
            phonon: The phonopy object the PhononRow represents
        """
        from phonopy import Phonopy

        phonon = Phonopy(
            to_phonopy_atoms(self.toatoms()),
            supercell_matrix=np.array(self.sc_matrix_2).reshape(3, 3).transpose(),
            symprec=self.symprec,
            is_symmetry=True,
            factor=const.omega_to_THz,
        )
        phonon.set_displacement_dataset(self.displacement_dataset_2)
        if "_fc_2" in self:
            phonon.set_force_constants(self.fc_2)
        elif "forces_2" in self and len(self.forces_2) > 0:
            phonon.produce_force_constants(self.forces_2)
            self.__dict__["_fc_2"] = phonon.get_force_constants()
        if "qmesh" in self and self.qmesh is not None:
            phonon.set_mesh(self.qmesh)
            if "tp_T" in self and self.tp_T is not None:
                phonon.set_thermal_properties(temperatures=self.tp_T)
        return phonon

    def to_phonon3(self, mesh=None):
        """
        Converts the row back into a phono3py object
        Returns:
            phonon3: The phono3py object the PhononRow represents
        """
        from phono3py.phonon3 import Phono3py
        phonon3 = Phono3py(
            to_phonopy_atoms(self.toatoms()),
            supercell_matrix=np.array(self.sc_matrix_3).reshape(3, 3).transpose(),
            phonon_supercell_matrix=np.array(self.sc_matrix_2)
            .reshape(3, 3)
            .transpose(),
            symprec=self.symprec,
            is_symmetry=True,
            frequency_factor_to_THz=const.omega_to_THz,
            log_level=0,
            mesh=self.qmesh if "qmesh" in self else None,
        )
        phonon3._phonon_displacement_dataset = self.displacement_dataset_2.copy()
        phonon3.set_displacement_dataset(self.displacement_dataset_3)

        if "forces_2" in self and len(self.forces_2) > 0:
            phonon3.produce_fc2(
                self.forces_2, displacement_dataset=self.displacement_dataset_2
            )
            self.__dict__["_fc_2"] = phonon3.get_fc2()

        if "forces_3" in self and len(self.forces_3) > 0:
            phonon3.produce_fc3(
                self.forces_3, displacement_dataset=self.displacement_dataset_3
            )
            self.__dict__["_fc_3"] = phonon3.get_fc3()

        if mesh is None and "qmesh" in self and self.qmesh is not None:
            phonon3._mesh = np.array(self.qmesh, dtype="intc")
        elif mesh is not None:
            phonon3._mesh = np.array(mesh, dtype="intc")

        if "tp_T" in self:
            phonon3.run_thermal_conductivity(temperatures=self.tp_T, write_kappa=True)
        return phonon3

    def thermal_heat_capacity_v(self, T):
        """
        Gets the Cv of the material at a given temperature
        Args:
            T: float
                The temperature
        Returns:
            Cv : float
                the heat_capacity_v at temperature T
        """
        return self.tp_Cv[np.where(self.tp_T == T)[0]][0]

    def thermal_entropy(self, T):
        """
        Gets the entropy of the material at a given temperature
        Args:
            T: float
                The temperature
        Returns:
            S: float
                The entropy at temperature T
        """
        return self.tp_S[np.where(self.tp_T == T)[0]][0]

    def thermal_free_energy(self, T):
        """
        Gets the Hemholtz free energy of the material at a given temperature
        Args:
            T: float
                The temperature
        Returns:
            A: float
                The Hemholtz free energy at temperature T
        """
        return self.tp_A[np.where(self.tp_T == T)[0]][0]

    def thermal_conductivity(self, T):
        """
        Gets the thermal conductivity of the material at a given temperature
        Args:
            T: float
                The temperature
        Returns:
            A: float
                The Hemholtz free energy at temperature T
        """
        return self.tp_kappa[np.where(self.tp_T == T)[0]][0]
