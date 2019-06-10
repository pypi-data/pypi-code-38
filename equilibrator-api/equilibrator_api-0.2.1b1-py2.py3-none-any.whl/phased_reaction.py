"""inherit from equilibrator_cache.reaction.Reaction an add phases."""
# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science
# Copyright (c) 2018 Institute for Molecular Systems Biology,
# ETH Zurich
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import logging
from typing import Dict, List, Tuple

import numpy as np

from equilibrator_cache.reaction import Reaction

from . import Q_, Compound, ccache, ureg
from .phased_compound import PhasedCompound


class PhasedReaction(Reaction):
    """A daughter class of Reaction that adds phases and abundances."""

    REACTION_COUNTER = 0

    def __init__(
            self,
            sparse: Dict[Compound, float],
            arrow: str = "<=>",
            rid: str = None,
            sparse_with_phases: Dict[PhasedCompound, float] = None
    ):
        """Create a PhasedReaction object.

        :param sparse: a dictionary of Compounds to stoichiometric coefficients
        :param arrow: a string representing the arrow in the chemical formula
        :param rid: a string of the reaction ID
        """
        super(PhasedReaction, self).__init__(sparse, arrow, rid)

        if sparse_with_phases is not None:
            self.sparse_with_phases = sparse_with_phases
        else:
            self.sparse_with_phases = \
                {PhasedCompound(cpd): coeff for cpd, coeff in sparse.items()}

        if self.rid is None:
            self.rid = 'COCO:R%05d' % PhasedReaction.REACTION_COUNTER
            PhasedReaction.REACTION_COUNTER += 1

    def clone(self):
        """Clone this reaction object."""
        return PhasedReaction(self.sparse.copy(), self.arrow, self.rid,
                              self.sparse_with_phases.copy())

    def reverse(self):
        """Return a PhasedReaction with the reverse reaction."""
        sparse = {
            cpd: -coeff for (cpd, coeff) in self.sparse.items()
        }

        sparse_with_phases = {
            cpd: -coeff for (cpd, coeff) in self.sparse_with_phases.items()
        }

        return PhasedReaction(sparse, self.arrow, self.rid,
                              sparse_with_phases)

    @staticmethod
    def _hashable_reactants(
        sparse_with_phases: Dict[Compound, float]
    ) -> Tuple[Tuple[int, str, float]]:
        """Return a unique list of number pairs representing phased reaction.

        The list fully identifies the biochemical reaction.
        If it is equal to another reaction's string, then they have identical
        stoichiometry.

        :param sparse_with_phases: a dictionary whose keys are phasedcompounds
        and values are stoichiometric coefficients
        :return: a unique list of pairs (compound.id, coefficient, phase)
        """
        if len(sparse_with_phases) == 0:
            return []

        # sort according to compound ID and normalize the stoichiometric
        # coefficients such that the coeff of the reactant with the lowest
        # ID will be 1
        sorted_compound_list = sorted(sparse_with_phases.keys(),
                                      key=lambda c: c.id)
        max_coeff = max(map(abs, sparse_with_phases.values()))
        if max_coeff == 0:
            raise Exception("All stoichiometric ceofficients are 0")
        norm_factor = 1.0 / max_coeff
        r_list = [
            (cpd.id, cpd.phase, norm_factor * sparse_with_phases[cpd])
            for cpd in sorted_compound_list
        ]
        return tuple(r_list)

    def __hash__(self) -> int:
        """Return a hash of the PhasedReaction.

        This hash is useful for finding reactions with the exact same
        stoichiometry. We create a unique formula string based on the
        Compound IDs and coefficients.

        :return: a hash of the Reaction.
        """
        reactants = PhasedReaction._hashable_reactants(self.sparse_with_phases)
        return hash(reactants)

    def __eq__(self, other: "PhasedReaction") -> bool:
        """Check if two reactions are equal.

        Ignores differences in reaction direction, or a multiplication of all
        coefficients by a scalar.
        """
        reactants = PhasedReaction._hashable_reactants(self.sparse_with_phases)
        other_reactants = PhasedReaction._hashable_reactants(
            other.sparse_with_phases)
        return reactants == other_reactants

    def __lt__(self, other: "PhasedReaction") -> bool:
        """Create an ordering of reactions.

        Used mainly for using reactions as dictionary keys.
        """
        reactants = PhasedReaction._hashable_reactants(self.sparse_with_phases)
        other_reactants = PhasedReaction._hashable_reactants(
            other.sparse_with_phases)
        return reactants < other_reactants

    def set_abundance(self, compound: Compound, abundance: ureg.Quantity):
        """Set the abundance of the compound."""
        for phased_compound in self.sparse_with_phases.keys():
            if phased_compound.compound == compound:
                phased_compound.abundance = abundance

    def reset_abundances(self):
        """Reset the abundance to standard levels."""
        for phased_compound in self.sparse_with_phases.keys():
            phased_compound.reset_abundance()

    def set_phase(self, compound: Compound, phase: str):
        """Set the phase of the compound."""
        for phased_compound in self.sparse_with_phases.keys():
            if phased_compound.compound == compound:
                phased_compound.phase = phase

    def get_phased_compound(
        self,
        compound: Compound
    ) -> Tuple[PhasedCompound, float]:
        """Get the PhasedCompound object by the Compound object."""
        # TODO: This is not ideal. We should try to not keep to dictionaries (
        #  one with Compounds and one with PhasedCompounds).
        for phased_compound, coeff in self.sparse_with_phases.items():
            if phased_compound.compound == compound:
                return phased_compound, coeff
        return None, 0

    def get_phase(self, compound: Compound) -> str:
        """Get the phase of the compound."""
        phased_compound, _ = self.get_phased_compound(compound)
        if phased_compound is None:
            return ""
        else:
            return phased_compound.phase

    def get_abundance(self, compound: Compound) -> ureg.Quantity:
        """Get the abundance of the compound."""
        phased_compound, _ = self.get_phased_compound(compound)
        if phased_compound is None:
            return None
        else:
            return phased_compound.abundance

    @property
    def is_physiological(self) -> bool:
        """Check if all concentrations are physiological.

        This function is used by eQuilibrator to know if to present the
        adjusted dG' or not (since the physiological dG' is always
        displayed and it would be redundant).

        :return: True if all compounds are at physiological abundances.
        """
        for phased_compound in self.sparse_with_phases.keys():
            if not phased_compound.is_physiological:
                return False
        return True

    def get_stoichiometry(self, compound: Compound) -> float:
        """Get the abundance of the compound."""
        for phased_compound, coeff in self.sparse_with_phases.items():
            if phased_compound.compound == compound:
                return coeff
        return 0.0

    def add_stoichiometry(self,
                          compound: Compound,
                          coeff: float) -> None:
        """Add to the stoichiometric coefficient of a compound.

        If this compound is not already in the reaction, add it.
        """
        super(PhasedReaction, self).add_stoichiometry(compound, coeff)

        for phased_compound in self.sparse_with_phases.keys():
            if phased_compound.compound == compound:
                if self.sparse_with_phases[phased_compound] == -coeff:
                    self.sparse_with_phases.pop(phased_compound)
                else:
                    self.sparse_with_phases[phased_compound] += coeff
                return

        self.sparse_with_phases[PhasedCompound(compound)] = coeff

    @ureg.check(None, None, "[concentration]", "[temperature]")
    def separate_stored_dg_prime(
        self,
        p_h: ureg.Quantity,
        ionic_strength: ureg.Quantity,
        temperature: ureg.Quantity
    ) -> Tuple[Reaction, ureg.Quantity]:
        """Split the PhasedReaction to aqueous phase and all the rest.

        :param p_h:
        :param ionic_strength:
        :param temperature:
        :return: a tuple (residual_reaction, stored_dg_prime) where
        residual_reaction is a Reaction object (excluding the compounds that
        had stored values), and stored_dg_prime is the total dG' of the
        compounds with stored values (in kJ/mol).
        """
        stored_dg_prime = 0
        sparse = {}  # all compounds without stored dgf values
        for phased_compound, coeff in self.sparse_with_phases.items():
            dgf_prime = phased_compound.get_stored_standard_dgf_prime(
                p_h=p_h, ionic_strength=ionic_strength, temperature=temperature)

            if dgf_prime is None:
                sparse[phased_compound.compound] = coeff
            else:
                stored_dg_prime += coeff * dgf_prime

        return Reaction(sparse, arrow=self.arrow, rid=self.rid), stored_dg_prime

    def separate_stored_dg(
        self,
    ) -> Tuple[Reaction, ureg.Quantity]:
        """Split the PhasedReaction to aqueous phase and all the rest.

        :return: a tuple (residual_reaction, stored_dg) where
        residual_reaction is a Reaction object (excluding the compounds that
        had stored values), and stored_dg is the total dG of the
        compounds with stored values (in kJ/mol).
        """
        stored_dg_prime = 0
        sparse = {}  # all compounds without stored dgf values
        for phased_compound, coeff in self.sparse_with_phases.items():
            dgf_prime = phased_compound.get_stored_standard_dgf()

            if dgf_prime is None:
                sparse[phased_compound.compound] = coeff
            else:
                stored_dg_prime += coeff * dgf_prime

        return Reaction(sparse, arrow=self.arrow, rid=self.rid), stored_dg_prime

    def dg_correction(self) -> float:
        """Calculate the concentration adjustment in the dG' of reaction.

        :return: the correction for delta G in units of RT
        """
        # here we check that each concentration is in suitable units,
        # depending on the phase of that compound
        ddg_over_rt = Q_(0.0)
        for phased_compound, coeff in self.sparse_with_phases.items():
            ddg_over_rt += coeff * phased_compound.ln_abundance
        return ddg_over_rt

    def physiological_dg_correction(self) -> float:
        """Calculate the concentration adjustment in the dG' of reaction.

        Assuming all reactants are in the default physiological
        concentrations (i.e. 1 mM)

        :return: the correction for delta G in units of RT
        """
        ddg_over_rt = Q_(0.0)
        for phased_compound, coeff in self.sparse_with_phases.items():
            ddg_over_rt += coeff * phased_compound.ln_physiological_abundance
        return ddg_over_rt

    def balance_by_oxidation(self):
        """Convert an unbalanced reaction into oxidation.

        By adding H2O, O2, Pi, CO2, and NH4+ to both sides.
        """
        # We need to make sure that the number of balancing compounds is the
        # same as the number of elements we are trying to balance. Here both
        # numbers are 6, i.e. the elements are (e-, H, O, P, C, N)
        balancing_inchis = [
            "InChI=1S/p+1",  # H+
            "InChI=1S/H2O/h1H2",  # H2O
            "InChI=1S/O2/c1-2",  # O2
            "InChI=1S/H3O4P/c1-5(2,3)4/h(H3,1,2,3,4)/p-2",  # Pi
            "InChI=1S/CO2/c2-1-3",  # CO2
            "InChI=1S/H3N/h1H3/p+1",  # NH4+
        ]
        compounds = list(map(ccache.get_compound_by_inchi, balancing_inchis))
        print(compounds)

        S = ccache.get_element_data_frame(compounds)
        balancing_atoms = S.index

        atom_bag = self._get_reaction_atom_bag()
        if atom_bag is None:
            logging.warning('Cannot balance this reaction due to'
                            ' missing chemical formulas')
            return self
        atom_vector = np.array(
            list(map(lambda a: atom_bag.get(a, 0), balancing_atoms)))

        other_atoms = set(atom_bag.keys()).difference(balancing_atoms)
        if other_atoms:
            raise ValueError(f"Cannot oxidize {self} only with these atoms: "
                             f"{other_atoms}")

        # solve the linear equation S * i = a,
        # and ignore small coefficients (< 1e-3)
        imbalance = (-np.linalg.inv(S.values) @ atom_vector).round(3)

        for compound, coeff in zip(S.columns, imbalance.flat):
            self.add_stoichiometry(compound, coeff)

        return self

    @classmethod
    def get_oxidation_reaction(cls, compound: Compound):
        """Generate an oxidation Reaction for a single compound.

        Generate a Reaction object which represents the oxidation reaction
        of this compound using O2. If there are N atoms, the product must
        be NH3 (and not N2) to represent biological processes.
        Other atoms other than C, N, H, and O will raise an exception.
        """
        return cls({compound: -1}).balance_by_oxidation()

    def serialize(self) -> List[dict]:
        """Return a serialized version of all the reaction thermo data."""
        list_of_compounds = []
        for phased_compound, coeff in self.sparse_with_phases.items():
            compound_dict = phased_compound.serialize()
            compound_dict["coefficient"] = coeff
            list_of_compounds.append(compound_dict)
        return list_of_compounds
