#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

from libprot.pdb import ResidueModifier, Residue, AminoAcid, Flexibility
from osprey_design.designs.stability_design import StabilityDesign


def test_serialization_of_default_stability_design():
    design = StabilityDesign()
    yaml = design.serialize()
    instance = StabilityDesign.deserialize(yaml)

    assert instance == design


def test_serialization_of_stability_design():
    design = StabilityDesign()
    design.epsilon = 0.63
    design.design_name = 'Fancy design name'
    design.osprey_version = 'Osprey 3.0 <hash here>'

    with open('tests/resources/KE07.pdb') as f:
        pdb_literal = f.read()

    design.set_molecule(pdb_literal)

    valine = Residue('A', 1, AminoAcid.VAL)
    alanine = Residue('A', 2, AminoAcid.ALA)

    valine_mod = ResidueModifier(valine)

    for aa in (AminoAcid.ALA, AminoAcid.PHE, AminoAcid.TYR):
        valine_mod.add_target_mutable(aa)

    valine_mod.flexibility = Flexibility(True, True)

    alanine_mod = ResidueModifier(alanine)

    design.residue_configurations = [valine_mod, alanine_mod]

    yaml = design.serialize()
    instance = StabilityDesign.deserialize(yaml)

    assert instance == design


def test_stability_design_copy_works():
    with open('tests/resources/KE07.pdb') as f:
        pdb_literal = f.readlines()

    design = StabilityDesign()
    design.epsilon = 0.63
    design.design_name = 'Fancy design name'
    design.osprey_version = 'Osprey 3.0 <hash here>'
    design.molecule = pdb_literal

    cpy = copy.copy(design)

    assert cpy == design


def test_stability_design_does_not_serialize_private_fields():
    design = StabilityDesign()
    valine_mod = ResidueModifier(Residue('A', 1, AminoAcid.VAL))

    for aa in (AminoAcid.ALA, AminoAcid.PHE, AminoAcid.TYR):
        valine_mod.add_target_mutable(aa)

    valine_mod.flexibility = Flexibility(True, True)
    valine_mod.add_observer(object()) # the observer field is a private, non-serializable field
    design.residue_configurations = {valine_mod}
    yaml = design.serialize()
    instance = StabilityDesign.deserialize(yaml)
    assert instance == design
