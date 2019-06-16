import os
from dataclasses import dataclass
from enum import Enum
from typing import List

from prody.proteins import parsePDB

from .redirect_std_streams import RedirectStdStreams


class AminoAcid(Enum):
    ALA = 'Ala'
    ARG = 'Arg'
    ASN = 'Asn'
    ASP = 'Asp'
    CYS = 'Cys'
    GLN = 'Gln'
    GLU = 'Glu'
    GLY = 'Gly'
    HIS = 'His'
    ILE = 'Ile'
    LEU = 'Leu'
    LYS = 'Lys'
    MET = 'Met'
    PHE = 'Phe'
    PRO = 'Pro'
    SER = 'Ser'
    THR = 'Thr'
    TRP = 'Trp'
    TYR = 'Tyr'
    VAL = 'Val'
    ASX = 'Asx'
    GLX = 'Glx'
    XAA = 'Xaa'
    TERM = 'TERM'
    OTHER = 'OTHER'

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(f'!AminoAcid', node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls[node.value.upper()]


@dataclass(frozen=True)
class Residue:
    chain: str
    res_num: int
    aa_type: AminoAcid


@dataclass(frozen=True)
class Flexibility:
    is_flexible: bool = False
    include_structure_rotamer: bool = False


class ResidueModifier:
    @property
    def identity(self):
        return self._identity

    @property
    def mutable(self):
        return frozenset(self._mutable)

    def add_target_mutable(self, aa: AminoAcid):
        self._mutable.append(aa)
        for observer in self._observers:
            if hasattr(observer, 'mutability_did_change'):
                observer.mutability_did_change(self)

    def remove_target_mutable(self, aa: AminoAcid):
        self._mutable.remove(aa)
        for observer in self._observers:
            if hasattr(observer, 'mutability_did_change'):
                observer.mutability_did_change(self)

    @property
    def flexibility(self):
        return self._flexibility

    @flexibility.setter
    def flexibility(self, flex):
        self._flexibility = flex
        for observer in self._observers:
            if hasattr(observer, 'flexibility_did_change'):
                observer.flexibility_did_change(self)
            if hasattr(observer, 'use_structure_rotamer_did_change'):
                observer.use_structure_rotamer_did_change(self)

    def __init__(self, residue: Residue):
        self._identity = residue
        self._mutable = [residue.aa_type]
        self._observers = []
        self._flexibility = Flexibility()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (self.identity == other.identity and
                self.mutable == other.mutable and
                self.flexibility == other.flexibility)

    def __hash__(self):
        return hash(self.identity) + hash(self.mutable) + hash(self.flexibility)

    def is_mutable(self):
        return len(self._mutable) > 1  # More than just the identity

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)


def is_pdb_file(path: str) -> bool:
    if not os.path.exists(path):
        return False

    # This method outputs a lot to STDOUT/STDERR, we don't want that.
    with open(os.devnull) as devnull:
        with RedirectStdStreams(devnull, devnull):
            try:
                return parsePDB(path) is not None
            except (AttributeError, ValueError, IOError):  # something went wrong during parsing
                return False


def get_amino_acids(path: str) -> List[Residue]:
    structure = parsePDB(path).getHierView()

    rv = []
    for x in structure.iterResidues():
        try:
            aa_type = AminoAcid[x.getResname().upper()]
        except KeyError:
            aa_type = AminoAcid.OTHER

        rv.append(Residue(chain=x.getChid(), res_num=x.getResnum(), aa_type=aa_type))

    return rv
