"""Dataset and Subset classes."""

from pathlib import Path
import numpy as np
import qmmlpack as qmml

from cmlkit.engine import compute_hash, Configurable, save_npy
from cmlkit.utility import convert

# Yes, this is a bit of a nightmare -- it is really a very very overloaded class.
# Note that we're using the Configurable infrastructure here, but it really is
# a bit of a hack -- it is not intended for "heavy" applications where we move
# around large ndarrays. But it's Good Enough For Now!


class Dataset(Configurable):
    """Dataset class.

    A Dataset is a collection of geometries (of periodic or non-periodic systems),
    combined with properties (currently only scalar properties), augmented with
    some metadata and methods.

    ***

    The geometries in a dataset are composed of positions (`r`), atomic charges (`z`) and,
    in the case of periodic systems the basis vectors (`b`).

    `cmlkit` implicitly assumes the following types:
        `z`: `ndarray` of `dtype=object` wrapping a list,
            in which each entry is an ndarray of `dtype=int`
        `r`: `ndarray` of `dtype=object` wrapping a list,
            in which each entry is an ndarray of `dtype=float`
        `b`: either None or `ndarray` of `dtype=float`.

    Each of these must share a common `len` equal to the number of systems in the dataset.
    In `z` and `r`, each individual entry must have `len = number_of_atoms`. Since not
    all systems can be expected to have the same number of atoms, these are ragged arrays.

    Currently, no type checking is performed. Also, it should be noted that storing
    `r` or `z` as `object`-type arrays is not particularly efficient, but simple --
    in the future, we will most likely transition to a linearised array model, which
    allows us to store everything contiguous in memory.

    In addition to geometries, a Dataset can also contain *properties*, which are the
    quantities that we're trying to build models for. They are stored in the attribute `p`.

    `p` is simply a `dict`, with each string-labelled entry expected to be an `ndarray`
    with one particular property.

    We implicitly expect all properties to be given PER ATOM! This is due to the fact
    that the `Model` class performs internal conversion of properties depending on what is
    best for the performance of the regression model -- sometimes it is better to predict
    quantities per structure rather than per atom. So we need some common baseline.

    ***

    A Dataset is identified by its `.name`, which is expected to be unique. Datasets
    are loaded using this identifier!

    Additionally `.hash` and `.geom_hash` can be used to distinguish `Datasets`.

    These hashes are only computed ONCE -- Datasets are not supposed to be mutable.
    This is (in true Python fashion) not enforced, but things like caching will break.

    ***

    Datasets are saved to disk as `.npy` files, the filename should be the name of the dataset.

    They can be loaded using the `load_dataset` method supplied by `cmlkit`, which looks
    for `Datasets` in an environment variable called `CML_DATASET_PATH` and the `cwd`.

    ***

    Subsets of a Dataset can be defined using the `Subset` class.

    ***

    Attributes:
        z: Atomic charges.
        r: Atomic positions.
        b: Basis if periodic.
        p: Dict with properties.
        name: Name of dataset.
        desc: Description of dataset.
        splits: List of pre-rolled train/test splits of the form
            [[train_1, test_1], [train_2, test_2]]. Mainly to be used
            to ensure tighly controlled CV-losses. Ignored in hashing.
        hash: Hash, ignoring name and description.
        geom_hash: Like hash, but also ignoring properties.
        report: String with a report on this dataset and its statistics.
        info: Dict with various properties of this dataset.

    Methods:
        pp: Properties per X.
        save: Save dataset to disk.


    """

    kind = "dataset"

    def __init__(self, z, r, b=None, p={}, name=None, desc="", splits=[]):
        super().__init__()

        # Sanity checks
        assert len(z) == len(
            r
        ), "Attempted to create dataset, but z and r are not of the same size ({} vs {})!".format(
            len(z), len(r)
        )
        assert b is None or len(b) == len(
            z
        ), "Attempted to create dataset, but z and b are not of the same size ({} vs {})!".format(
            len(z), len(b)
        )
        assert len(r) > 0, "Attempted to create dataset, r has 0 length!"

        self.desc = desc
        self.z = z
        self.r = r
        self.b = b
        self.p = p
        self.splits = splits

        if name is None:
            name = compute_hash(self.z, self.r, self.b, self.p)
        self.name = name

        self.n = len(self.z)

        # lazily computed attributes
        self._report = None
        self._info = None
        self._hash = None
        self._geom_hash = None

        # compute auxiliary info that we need to convert properties
        self.aux = {}
        n_atoms = np.array([len(zz) for zz in self.z])  # count atoms in unit cell
        n_non_O = np.array(
            [len(zz[zz != 8]) for zz in self.z]
        )  # count atoms that are not Oxygen
        n_non_H = np.array(
            [len(zz[zz != 1]) for zz in self.z]
        )  # count atoms that are not Hydrogen

        self.aux["n_atoms"] = n_atoms
        self.aux["n_non_O"] = n_non_O
        self.aux["n_non_H"] = n_non_H

    def _get_config(self):

        return {
            "name": self.name,
            "desc": self.desc,
            "z": self.z,
            "r": self.r,
            "b": self.b,
            "p": self.p,
            "splits": self.splits,
        }

    def save(self, directory="", filename=None):
        """Save to disk, defaulting to the name as filename"""

        directory = Path(directory)

        if filename is None:
            filename = self.name

        save_npy(directory / filename, self.get_config())

    def __getitem__(self, idx):
        return View(self, idx)

    def prepare(self):
        """Compute all lazily computed properties."""

        return self.info, self.report, self.hash, self.geom_hash

    @property
    def info(self):
        if self._info is not None:
            return self._info
        else:
            self._info = compute_dataset_info(self)
            return self._info

    @property
    def hash(self):
        """Hash of dataset, ignoring name and description."""
        if self._hash is None:
            self._hash = compute_hash(self.z, self.r, self.b, self.p)
            return self._hash
        else:
            return self._hash

    @property
    def geom_hash(self):
        """Hash of only the geometries, ignoring properties etc."""
        if self._geom_hash is None:
            self._geom_hash = compute_hash(self.z, self.r, self.b)
            return self._geom_hash
        else:
            return self._geom_hash

    def pp(self, target, per="None"):
        return convert(self, self.p[target], per=per)

    @property
    def report(self):

        if self._report is None:
            i = self.info
            general = (
                "# {}: {} #\n\n".format(self.__class__.kind, self.name) + self.desc + "\n"
            )

            over = "\n## Overview ##\n"
            if self.b is None:
                over += (
                    " {} finite systems (molecules)".format(i["number_systems"]) + "\n"
                )
            else:
                over += (
                    " {} periodic systems (materials)".format(i["number_systems"]) + "\n"
                )
            keys = [str(k) for k in self.p.keys()]
            over += " {} different properties: {}\n".format(len(self.p.keys()), keys)

            elems = (
                " elements: {} ({})".format(
                    " ".join(
                        [qmml.element_data(el, "abbreviation") for el in i["elements"]]
                    ),
                    len(i["elements"]),
                )
                + "\n"
            )
            elems = " elements by charge: {}".format(i["elements"]) + "\n"
            elems += (
                " max #els/system: {};  max same #el/system: {};  max #atoms/system: {}".format(
                    i["max_elements_per_system"],
                    i["max_same_element_per_system"],
                    i["max_atoms_per_system"],
                )
                + "\n"
            )

            dist = (
                " min dist: {:3.2f};  max dist: {:3.2f}".format(
                    i["min_distance"], i["max_distance"]
                )
                + "\n"
            )

            g = i["geometry"]
            geom = "\n## Geometry ##"
            geom += "\n### Ranges ###\n"
            geom += " These are the ranges for various geometry properties.\n"
            geom += " count   : {} to {}".format(g["min_count"], g["max_count"]) + "\n"
            geom += (
                " dist    : {:4.4f} to {:4.4f}".format(g["min_dist"], g["max_dist"])
                + "\n"
            )
            geom += (
                " 1/dist  : {:4.4f} to {:4.4f}".format(g["min_1/dist"], g["max_1/dist"])
                + "\n"
            )
            geom += (
                " 1/dist^2: {:4.4f} to {:4.4f}".format(
                    g["min_1/dist^2"], g["max_1/dist^2"]
                )
                + "\n"
            )
            geom += "\n### Recommendations for d ###\n"
            geom += " We recommend using the intervals (-0.05*max, 1.05*max) for the parametrisation of the MBTR, i.e. a 5% padding. "
            geom += " In the following, n is the number of bins.\n"
            geom += " k=1 MBTR:\n"
            geom += (
                " count     : ({:4.2f}, {:4.2f}/n, n)".format(
                    -0.05 * g["max_count"], 1.1 * g["max_count"]
                )
                + "\n"
            )
            geom += " k=2 MBTR:\n"
            geom += (
                " 1/dist    : ({:4.2f}, {:4.2f}/n, n)".format(
                    -0.05 * g["max_1/dist"], 1.1 * g["max_1/dist"]
                )
                + "\n"
            )
            geom += (
                " 1/dot     : ({:4.2f}, {:4.2f}/n, n)".format(
                    -0.05 * g["max_1/dist^2"], 1.1 * g["max_1/dist^2"]
                )
                + "\n"
            )
            geom += " k=3 MBTR (experimental):\n"
            geom += (
                " angle     : ({:4.2f}, {:4.2f}/n, n)".format(-0.05 * np.pi, 1.1 * np.pi)
                + "\n"
            )
            geom += " cos_angle : ({:4.2f}, {:4.2f}/n, n)".format(-1.05 * 1, 2.1) + "\n"
            geom += (
                " dot/dotdot: ({:4.2f}, {:4.2f}/n, n)".format(
                    -0.05 * g["max_1/dist^2"], 1.1 * g["max_1/dist^2"]
                )
                + "\n"
            )
            geom += " It is still prudent to experiment with these settings!\n"

            p = i["properties"]
            prop = "\n## Properties ##\n"
            prop += " Mean and standard deviation of properties:\n"
            for k, v in p.items():
                prop += " {}: {:4.4f} ({:4.4f})\n".format(k, v[0], v[1])

            self._report = general + over + elems + dist + geom + prop

        return self._report


class Subset(Dataset):
    """Subset of a Dataset."""

    kind = "subset"

    def __init__(
        self, z, r, b=None, p={}, name=None, desc="", idx=None, parent_info={}, splits=[]
    ):
        # you probably want to use from_dataset in 99% of cases
        super().__init__(z, r, b, p, name=name, desc=desc, splits=splits)

        self.idx = idx
        self.parent_info = parent_info

    @classmethod
    def from_dataset(cls, dataset, idx, name=None, desc="", splits=[]):
        """From parent dataset, create subset."""

        z = dataset.z[idx]
        r = dataset.r[idx]
        if dataset.b is not None:
            b = dataset.b[idx]
        else:
            b = None

        sub_properties = {}

        for p, v in dataset.p.items():
            sub_properties[p] = v[idx]

        p = sub_properties

        if desc == "":
            desc = "Subset of dataset {} with n={} entries".format(dataset.name, len(idx))

        if name is None:
            name = dataset.name + "_subset" + str(len(idx))

        parent_info = {"desc": dataset.desc, "name": dataset.name}

        return cls(
            z,
            r,
            b=b,
            p=p,
            name=name,
            desc=desc,
            idx=idx,
            parent_info=parent_info,
            splits=splits,
        )

    def _get_config(self):

        return {
            "name": self.name,
            "desc": self.desc,
            "z": self.z,
            "r": self.r,
            "b": self.b,
            "p": self.p,
            "idx": self.idx,
            "parent_info": self.parent_info,
            "splits": self.splits,
        }


def compute_dataset_info(dataset):
    """Information about a dataset.

    Returns a dictionary containing information about a dataset.

    Args:
      dataset: dataset

    Returns:
      i: Dict with the following keys:
          elements: elements occurring in dataset
          max_elements_per_system: largest number of different elements in a system
          max_same_element_per_system: largest number of same-element atoms in a system
          max_atoms_per_system: largest number of atoms in a system
          min_distance: minimum distance between atoms in a system
          max_distance: maximum distance between atoms in a system
          geometry: additional detailed info about geometries (see below)
    """
    z = dataset.z
    r = dataset.r
    p = dataset.p

    i = {}

    i["number_systems"] = len(z)

    # elements
    i["elements"] = np.unique(
        np.asarray([a for s in z for a in s], dtype=np.int)
    )  # note that this is always sorted
    i["total_elements"] = len(i["elements"])
    i["max_elements_per_system"] = max([np.nonzero(np.bincount(s))[0].size for s in z])
    i["max_same_element_per_system"] = max([max(np.bincount(s)) for s in z])
    i["min_same_element_per_system"] = min([min(np.bincount(s)) for s in z])

    # systems
    i["max_atoms_per_system"] = max([len(s) for s in z])
    i["systems_per_element"] = np.asarray(
        [np.sum([1 for m in z if el in m]) for el in range(118)], dtype=np.int
    )

    # atoms
    i["atoms_by_system"] = np.array([len(s) for s in z], dtype=int)
    i["total_atoms"] = np.sum(i["atoms_by_system"])

    # distances
    dists = [qmml.lower_triangular_part(qmml.distance_euclidean(rr), -1) for rr in r]
    i["min_distance"] = min([min(d) for d in dists if len(d) > 0])
    i["max_distance"] = max([max(d) for d in dists if len(d) > 0])

    # geometry info
    geom = {}
    geom["max_dist"] = i["max_distance"]
    geom["min_dist"] = i["min_distance"]

    geom["max_1/dist"] = 1 / geom["min_dist"]
    geom["max_1/dist^2"] = 1 / geom["min_dist"] ** 2

    geom["min_1/dist"] = 1 / geom["max_dist"]
    geom["min_1/dist^2"] = 1 / geom["max_dist"] ** 2

    geom["max_count"] = i["max_same_element_per_system"]
    geom["min_count"] = i["min_same_element_per_system"]

    i["geometry"] = geom

    # property info
    prop = {}
    for k, v in p.items():
        prop[k] = (np.mean(v), np.std(v))

    i["properties"] = prop

    return i


def compute_incidence(dataset):
    """Compute the atomic incidence matrix of a dataset

        This is a n x total_atoms matrix which is one wherever
        an atom belongs to a given structure (needed for predictions
        with atomic contributions instead of whole structures).

        """

    total_atoms = dataset.info["total_atoms"]
    incidence = np.zeros((dataset.n, total_atoms), dtype=int)
    pos = 0
    for i, z in enumerate(dataset.z):
        n_atoms = len(z)
        incidence[i, pos : pos + n_atoms] = 1
        pos += n_atoms

    return incidence


def compute_mask(incidence, idx):
    """Generate a mask selecting atoms from structures in idx"""

    mask = np.zeros_like(incidence[0])

    for i in idx:
        mask += incidence[i]

    return np.where(mask == 1)
