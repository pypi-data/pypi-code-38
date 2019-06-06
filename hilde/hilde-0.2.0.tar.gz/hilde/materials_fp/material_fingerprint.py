import re
import sqlite3
import numpy as np
import yaml
from phonopy import Phonopy
from collections import namedtuple
from ase.dft.kpoints import get_cellinfo

fp_tup = namedtuple("fp_tup", "frequencies occupancies special_pts nbins")

# Functions to define the energy bins
def get_ener(binning, frequencies, min_e, max_e, nbins):
    """
    Get the energy bins used for making a fingerprint
    Args:
        useFrequencies: bool
            if True use the band/DOS frequencies given as the bin boundaries
        frequencies: list or np.ndarray of floats
            The set of frequencies the band structure or DOS is calculated for
        min_e: float
            minimum energy mode to be included
        max_e: float
            maximum energy mode to be included
        nbins: int
            number of bins for the histogram
    Returns:
        np.ndarray of floats
            energy bin labels (energy of the band or bin center point)
        np.ndarray of floats
            energy bin boundaries
    """
    if binning:
        enerBounds = np.linspace(min_e, max_e, nbins + 1)
        return enerBounds[:-1] + (enerBounds[1] - enerBounds[0]) / 2.0, enerBounds
    else:
        return (
            np.array(frequencies),
            np.append(frequencies, [frequencies[-1] + np.abs(frequencies[-1]) / 10]),
        )


def find_min_E(bands):
    """
    Calculates the minimum energy mode in a band structure
    Args:
        bands: dict
            A dictionary describing the phonon/electronic modes at all high symmetry points
            Keys = Labels, Values = high symmetry points
    Returns: float
        The global minimum mode energy energy
    """
    return np.min(np.array([bands[pt] for pt in bands]).flatten())


def find_max_E(bands):
    """
    Calculates the maximum energy mode in a band structure
    Args:
        bands: dict
            A dictionary describing the phonon/electronic modes at all high symmetry points
            Keys = Labels, Values = high symmetry points
    Returns: float
        The global maximum mode energy energy
    """
    return np.max(np.array([bands[pt] for pt in bands]).flatten())


# Given a band structure or dos get the finger print
def get_fingerprint_bs(bands, binning, min_e, max_e, nbins):
    """
    Creates a dictionary of the band structure fingerprint at all high symmetry points, where the high symmetry point is the key
    Args:
        bands: dict
            A dictionary storing the phonon/electron mode energies at the high symmetry points, which are the keys for the dict
            Keys = Labels, Values = A list of energies at that point
        min_e : float
            The minimum mode energy to include in the fingerprint
        max_e : float
            The maximum mode energy to include in the fingerprint
        nbins: int
            Number of bins to be used in the fingerprint
    Returns:
        fingerprint: collection.namedtupele(fp_tup)
            (frequencies included in fingerprint, the number of states at that energy, names for the key points, number of bins)
    """
    freq_list = []
    n_bands = []
    special_pts = []
    for pt in bands:
        special_pts.append(pt)
        ener, enerBounds = get_ener(binning, bands[pt], min_e, max_e, nbins)
        freq_list.append(ener)
        n_bands.append(np.histogram(bands[pt], enerBounds)[0])
    return fp_tup(np.array(freq_list), np.array(n_bands), special_pts, len(freq_list[0]))


def get_fingerprint_dos(dos, binning, min_e, max_e, nbins):
    """
    Creates a dictionary of the density of states fingerprint
    Args:
        dos: np.ndarray of floats (shape=number of frequencies included, 2)
            The density of states at given energies
        min_e:
            The minimum mode energy to include in the fingerprint
        max_e:
            The maximum mode energy to include in the fingerprint
        nbins:
            Number of bins to be used in the fingerprint
    Returns:
        fingerprint: collection.namedtupele(fp_tup)
            (frequencies included in fingerprint, the density of states at that energy, "DOS", number of bins)
    """
    if dos.shape[0] < nbins:
        return fp_tup(
            dos[np.where((dos[:, 0] >= min_e) & (dos[:, 0] <= max_e)), 0],
            dos[np.where((dos[:, 0] >= min_e) & (dos[:, 0] <= max_e)), 1],
            ["DOS"],
            dos.shape[0],
        )
    ener, enerBounds = get_ener(binning, dos[:, 0], min_e, max_e, nbins)
    dos_rebin = np.zeros(ener.shape)
    for ii, e1, e2 in zip(range(len(ener)), enerBounds[0:-1], enerBounds[1:]):
        dos_rebin[ii] = np.sum(dos[np.where((dos[:,0] >= e1) & (dos[:,0] < e2))[0], 1])
    return fp_tup(np.array([ener]), dos_rebin, ["DOS"], nbins)


# Function to calculate the modes at the high symmetry points
def get_elec_bands(spectra_files, k_points):
    """
    Generates a dict describing the electronic band structure at from a list of files
    Args:
        spectra_files: list of str
            A list of filenames with the bands are defined
        k_points: dict
            A list of high symmetry points Key = labels; Values = points
    Returns:
        bands: dict
            A dictionary describing the electronic band structure with the keys being the high symmetry pints
            Key = labels, Values = Energy of the electronic modes
    """
    bands = {}
    for pt in k_points:
        for sFile in spectra_files:
            firstLine = list(filter(lambda x: x != "", open(sFile).readline().rstrip().split(" ")))
            lastLine = list(
                filter(lambda x: x != "", open(sFile).readlines()[-1].rstrip().split(" "))
            )
            if np.all(np.array(firstLine[1:4], dtype="float_") == k_points[pt]):
                bands[pt] = np.array(firstLine[5::2], dtype="float_")
            elif np.all(np.array(lastLine[1:4], dtype="float_") == k_points[pt]):
                bands[pt] = np.array(lastLine[5::2], dtype="float_")
    return bands


def get_phonon_bands_phonopy(phonon, q_points):
    """
    Generates a dict describing the phonon band structure at from a phonopy object
    Args:
        phonon: phonopy object
            The phonopy object from which the band structure calculated
        q_points: dict
            A dictionary of high symmetry points Keys=labels, Values= high symmetry point
    Returns:
        bands: dict
            A dictionary describing the phonon band structure
            Key = labels, Values = Energy of the phonon modes
    """
    bands = {}
    for pt in q_points:
        bands[pt] = phonon.get_frequencies(q_points[pt])
    return bands


def get_phonon_bands_yaml(spectra_yaml, q_points):
    """
    Generates a dict describing the phonon band structure at from a yaml file
    Args:
        spectra_yaml: str
            The phonopy generated yaml file describing the band structure
        q_points: a list of high symmetry points
    Returns:
        bands: dict
            A dictionary describing the phonon band structure with the keys being the high symmetry pints
            Key = labels, Values = Energy of the phonon modes
    """
    bands = {}
    bsSpect = yaml.load(open(spectra_yaml, "r"))
    bsLimited = []
    for bandpt in bsSpect["phonon"]:
        if "label" in bandpt:
            bsLimited.append(bandpt)
    bands = {}
    for pt in q_points:
        for bb in bsLimited:
            if np.all(bb["q-position"] == q_points[pt]):
                bands[pt] = [ff["frequency"] for ff in bb["band"]]
    return bands


# Functions to get the fingerprint from various input values
def get_phonon_bs_fingerprint_phononpy(
    phonon, q_points=None, binning=True, min_e=None, max_e=None, nbins=32
):
    """
    Generates the phonon band structure fingerprint for a bands structure stored in a phonopy object
    Args:
        phonon: phonopy Object
            The phonopy generated yaml file describing the band structure
        q_points: dict
            A dictionary of the high symmetry points Keys=labels, Values= high symmetry point
        min_e: float
            The minimum mode energy to include in the fingerprint
        max_e: float
            The maximum mode energy to include in the fingerprint
        nbins:int
            Number of bins to be used in the fingerprint
    Returns: namedtuple(fp_tup)
        The phonon band structure fingerprint
    """
    if q_points is None:
        q_points = get_cellinfo(phonon.primitive.cell).special_points

    bands = get_phonon_bands_phonopy(phonon, q_points)
    return get_fingerprint_bs(
        bands,
        binning,
        find_min_E(bands) if min_e is None else min_e,
        find_max_E(bands) if max_e is None else max_e,
        nbins,
    )


def get_phonon_bs_fingerprint_yaml(
    spectra_yaml, q_points, binning=True, min_e=None, max_e=None, nbins=32
):
    """
    Generates the phonon band structure fingerprint for a bands structure stored in a yaml file from a phonopy object
    Args:
        spectra_yaml: str
            The phonopy generated yaml file describing the band structure
        q_points: dict
            A dictionary of the high symmetry points Keys=labels, Values= high symmetry point
        min_e: float
            The minimum mode energy to include in the fingerprint
        max_e: float
            The maximum mode energy to include in the fingerprint
        nbins:int
            Number of bins to be used in the fingerprint
    Returns: namedtuple(fp_tup)
        The phonon band structure fingerprint
    """
    bands = get_phonon_bands_yaml(spectra_yaml, bands)
    if min_e is None:
        min_e = find_min_E(bands)
    if max_e is None:
        max_e = find_max_E(bands)
    return get_fingerprint_bs(bands, binning, min_e, max_e, nbins)


def get_elec_bs_fingerprint(
    spectra_files, k_points, binning=True, min_e=None, max_e=None, nbins=32
):
    """
    Generates the electronic band structure fingerprint for a bands stored in text files
    Args:
        spectra_files: list of str
            A list of filenames with the bands are defined
        q_points: dict
            A dictionary of the high symmetry points Keys=labels, Values= high symmetry point
        min_e: float
            The minimum mode energy to include in the fingerprint
        max_e: float
            The maximum mode energy to include in the fingerprint
        nbins:int
            Number of bins to be used in the fingerprint
    Returns: namedtuple(fp_tup)
        The electronic band structure fingerprint
    """
    bands = get_elec_bands(spectra_files, k_points)
    return get_fingerprint_bs(
        bands,
        binning,
        find_min_E(bands) if min_e is None else min_e,
        find_max_E(bands) if max_e is None else max_e,
        nbins,
    )


def get_dos_fingerprint(dos_file, binning=True, min_e=None, max_e=None, nbins=256):
    """
    Generates the density of states fingerprint from a file describing the density of states
    Args:
        dos_file: str
            The file where the density of states data is stored
        q_points: dict
            A dictionary of the high symmetry points Keys=labels, Values= high symmetry point
        min_e: float
            The minimum mode energy to include in the fingerprint
        max_e: float
            The maximum mode energy to include in the fingerprint
        nbins:int
            Number of bins to be used in the fingerprint
    Returns: namedtuple(fp_tup)
        The density of states fingerprint
    """
    dos = np.genfromtxt(dos_file)
    return get_fingerprint_dos(
        dos,
        binning,
        np.min(dos[:, 0]) if min_e is None else min_e,
        np.max(dos[:, 0]) if max_e is None else max_e,
        nbins,
    )


def get_phonon_dos_fingerprint_phononpy(phonon, binning=True, min_e=None, max_e=None, nbins=256):
    """
    Generates the density of states fingerprint for a bands structure stored in a phonopy object
    Args:
        phonon: phonopy Object
            The phonopy generated yaml file describing the band structure
        min_e: float
            The minimum mode energy to include in the fingerprint
        max_e: float
            The maximum mode energy to include in the fingerprint
        nbins:int
            Number of bins to be used in the fingerprint
    Returns: namedtuple(fp_tup)
        The phonon density of states fingerprint
    """
    dos = np.array(phonon.get_total_DOS()).transpose()
    return get_fingerprint_dos(
        dos,
        binning,
        np.min(dos[:, 0]) if min_e is None else min_e,
        np.max(dos[:, 0]) if max_e is None else max_e,
        nbins,
    )


def scalar_product(fp1, fp2, col=0, pt="All", normalize=False, tanimoto=False):
    """
    Calculates the dot product between two finger prints
    Args:
        fp1: namedtuple(fp_tup)
            The first fingerprint
        fp2: namedtuple(fp_tup)
            The second fingerprint
        col: int
            The item in the fingerprints to take the dot product of (either 0 or 1)
        pt: int or 'All'
            The index of the point that the dot product is to be taken, if 'All' flatten the arrays
        normalize: bool
            If True normalize the scalar product to 1
    Returns: float
        The dot product
    """
    if not isinstance(fp1, dict):
        fp1_dict = to_dict(fp1)
    else:
        fp1_dict = fp1
    if not isinstance(fp2, dict):
        fp2_dict = to_dict(fp2)
    else:
        fp2_dict = fp2

    if pt == 'All':
        vec1 = np.array([pt[col] for pt in fp1_dict.values()]).flatten()
        vec2 = np.array([pt[col] for pt in fp2_dict.values()]).flatten()
    else:
        vec1 = fp1_dict[fp1[2][pt]][col]
        vec2 = fp2_dict[fp2[2][pt]][col]

    rescale = 1.0
    if tanimoto:
        rescale = np.linalg.norm(vec1)**2 + np.linalg.norm(vec2)**2 - np.dot(vec1, vec2)
    elif normalize:
        rescale = np.linalg.norm(vec1) * np.linalg.norm(vec2)

    return np.dot(vec1, vec2) / rescale


def to_dict(fp, to_mongo=False):
    """
    Converts a fingerprint into a dictionary
    fp: namedtuple(fp_tup)
        The fingerprint to be onverted into a dictionary
    to_mongo: bool
        True if the database that this will be stored in is a mongo db
    Returns: dict
        A dictionary of the fingerprint Keys=Point lablels, Values=np.ndarray(frequencies, #of states)
    """
    fp_dict = {}
    if not to_mongo:
        if len(fp[2]) > 1:
            for aa in range(len(fp[2])):
                fp_dict[fp[2][aa]] = np.array([fp[0][aa], fp[1][aa]]).T
        else:
            fp_dict[fp[2][0]] = np.array([fp[0], fp[1]]).T
    else:
        if len(fp[2]) > 1:
            for aa in range(len(fp[2])):
                fp_dict[re.sub("[.]", "_", str(fp[2][aa]))] = np.array([fp[0][aa], fp[1][aa]]).T
        else:
            fp_dict[re.sub("[.]", "_", str(fp[2][0]))] = np.array([fp[0], fp[1]]).T
    return fp_dict


def dict2namedtuple(fp):
    """
    Converts a dictionary representation of a fingerprint into a named tuple
    Args:
        fp: dict
            The dictionary representation of the tuple
    Returns: namedtuple(fp_tup)
        The namedtuple representation of the fingerprint
    """
    freqs = [fp[pt][:, 0] for pt in fp]
    n_state = [fp[pt][:, 1] for pt in fp]
    sp_pts = [pt for pt in fp]
    return fp_tup(np.array(freqs), np.array(n_state), sp_pts, len(freqs[0]))


# Class definitions for incorporation into databases
class MaterialsFingerprint(object):
    """
    Base class describing material fingerprints
    """

    def __init__(self, is_elec, is_b, nbins=None, de=None, min_e=None, max_e=None, fp={}):
        """
        Initialize the fingerprint
        Args:
            is_elec: bool
                True if the fingerprint is of electronic modes
            is_b: bool
                True if the fingerprint is of a band structure
            nbins: int
                Number of bins in the fingerprint
            de: float
                Energy spacing between the bins
            min_e: float
                Minimum energy to be included in the fingerprint
            max_e: float
                Maximum energy to be included in the fingerprint
            fp: dict
                A dictionary of the fingerprint Keys=Point lablels, Values=np.ndarray(frequencies, #of states)
        """
        self.is_b = is_b
        self.is_elec = is_elec
        self.min_e = min_e
        self.max_e = max_e
        self.nbins = nbins
        self.de = de
        self.fingerprint = fp

    def __conform__(self, protocol):
        """
        A function to convert the fingerprint into a database readable format
        Args:
            protocol: sqlite3 protocol
                What protocol to be used to store the fingerprint
        """
        if protocol is sqlite3.PrepareProtocol:
            frmt = "%i;%r;%r" % (self.nbins, is_b, is_elec)
            for pt in self.fingerprint:
                frmt += ";%s" % (pt)
                for ff in self.fingerprint[pt]:
                    frmt += ";%f;%f" % (ff[0], ff[1])
            return frmt
        return ""

    def scalar_product(self, fp2, col=0, pt="All", normalize=True, tanimoto=False):
        """
        Calculates the dot product between the fingerprint and another fingerprint
        Args:
            fp2: namedtuple(fp_tup)
                The second fingerprint
            col: int
                The item in the fingerprints to take the dot product of (either 0 or 1)
            pt: int
                The index of the point that the dot product is to be taken
            normalize: bool
                If True normalize the scalar product to 1
        Returns: float
            The dot product
        """
        return scalar_product(self.fingerprint, fp2.fingerprint, col, pt, normalize, tanimoto)


class DOSFingerprint(MaterialsFingerprint):
    def __init__(
        self, is_elec, is_b, nbins=None, de=None, min_e=None, max_e=None, fp={}, spectra_files=[]
    ):
        """
        Initialize the DOS fingerprint
        Args:
            is_elec: bool
                True if the fingerprint is of electronic modes
            is_b: bool
                True if the fingerprint is of a band structure
            nbins: int
                Number of bins in the fingerprint
            de: float
                Energy spacing between the bins
            min_e: float
                Minimum energy to be included in the fingerprint
            max_e: float
                Maximum energy to be included in the fingerprint
            fp: dict
                A dictionary of the fingerprint Keys=Point lablels, Values=np.ndarray(frequencies, #of states)
            spectra_files: list of str size=1
                A list of a file storing the density of states
        """
        self.spectra_files = spectra_files
        self.is_elec = is_elec
        # determin_e Energy range
        dos = np.genfromtxt(self.spectra_files[0])
        binning = True if dos.shape[0] > nbins else False
        self.min_e = np.min(dos[:, 0]) if min_e is None else min_e
        self.max_e = np.max(dos[:, 0]) if max_e is None else max_e
        self.nbins = nbins
        if self.nbins is None:
            self.nbins = 256 if de is None else (self.max_e - self.min_e) / de
        self.de = de
        if self.de is None:
            self.de = (
                (self.max_e - self.min_e) / (256.0)
                if de is None
                else (self.max_e - self.min_e) / nbins
            )
        # make the fingerprint
        if fp == {}:
            fp = to_dict(get_fingerprint_dos(dos, binning, self.min_e, self.max_e, self.nbins))
        self.fingerprint = fp


class BandStructureFingerprint(MaterialsFingerprint):
    def __init__(
        self,
        is_elec,
        is_b,
        nbins=None,
        de=None,
        min_e=None,
        max_e=None,
        fp={},
        kpoints={},
        spectra_files=[],
        spectra_yaml="",
        phonon=None,
    ):
        """
        Initialize the fingerprint
        Args:
            is_elec: bool
                True if the fingerprint is of electronic modes
            is_b: bool
                True if the fingerprint is of a band structure
            nbins: int
                Number of bins in the fingerprint
            de: float
                Energy spacing between the bins
            min_e: float
                Minimum energy to be included in the fingerprint
            max_e: float
                Maximum energy to be included in the fingerprint
            fp: dict
                A dictionary of the fingerprint Keys=Point lablels, Values=np.ndarray(frequencies, #of states)
            spectra_files: list of str
                A list of a files storing information of the bands
            spectra_yaml: str
                The filename of the yaml file storing the band structure data
            phonon: phonopy object
                A phonopy object with the electronic band structure stored in it
        """
        self.kpoints = kpoints
        self.spectra_files = spectra_files
        self.spectra_yaml = spectra_yaml
        self.is_b = is_b
        self.is_elec = is_elec
        bands = {}
        # Take in band structure data
        if self.is_elec:
            bands = get_elec_bands(self.spectra_files, self.kpoints)
        else:
            if phonon == None:
                bands = get_phonon_bands_yaml(self.spectra_yaml, self.kpoints)
            else:
                bands = get_phonon_bands_phonon(self.spectra_yaml, self.kpoints)
        binning = True if list(bands.values())[0].shape[0] > nbins else False
        # Find energy bins
        self.min_e = find_min_E(bands) if min_e is None else min_e
        self.max_e = find_max_E(bands) if max_e is None else max_e
        self.nbins = nbins
        if self.nbins is None:
            self.nbins = 32 if de is None else (self.max_e - self.min_e) / de
        self.de = de
        if self.de is None:
            self.de = (
                (self.max_e - self.min_e) / (256.0)
                if de is None
                else (self.max_e - self.min_e) / nbins
            )

        # Make the fingerprint
        if fp == {}:
            fp = to_dict(get_fingerprint_bs(bands, binning, self.min_e, self.max_e, self.nbins))
        self.fingerprint = fp
