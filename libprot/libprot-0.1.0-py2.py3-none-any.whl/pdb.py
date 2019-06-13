import os
from dataclasses import dataclass
from enum import Enum
from typing import List

from prody import confProDy
from prody.proteins import parsePDB

from .redirect_std_streams import RedirectStdStreams

confProDy(verbosity='none')

AminoAcid = Enum('AminoAcid',
                 'Ala Arg Asn Asp Cys Gln Glu Gly His Ile Leu Lys Met Phe Pro Ser Thr Trp Tyr Val Asx Glx Xaa TERM other'.upper())


@dataclass
class Residue:
    chain: str
    res_num: int
    aa_type: AminoAcid


@dataclass
class Flexibility:
    is_flexible: bool = False
    include_structure_rotamer: bool = False


class ResidueModifier:
    @property
    def identity(self):
        return self._identity

    @property
    def mutable(self):
        return list(self._mutable)

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
            aa_type = AminoAcid[x.getResname()]
        except KeyError:
            aa_type = AminoAcid.OTHER

        rv.append(Residue(chain=x.getChid(), res_num=x.getResnum(), aa_type=aa_type))

    return rv
