# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
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
import re
import sys
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import PROTON_INCHI, WATER_INCHI
from .exceptions import ParseException
from .models import Compound
from .thermodynamic_constants import Q_, ureg


__all__ = ("POSSIBLE_REACTION_ARROWS", "Reaction")


POSSIBLE_REACTION_ARROWS = (
    # Three-character arrows.
    "<=>",
    "<->",
    "-->",
    "<--",
    # Two-character arrows.
    "=>",
    "<=",
    "->",
    "<-",
    # Single character unicode arrows.
    "=",
    "⇌",
    "⇀",
    "⇋",
    "↽",
)


class Reaction:
    def __init__(
        self,
        sparse: Dict[Compound, float],
        arrow: Optional[str] = None,
        rid: Optional[str] = None,
    ):
        self.sparse = {k: v for k, v in sparse.items() if v != 0}
        self.arrow = arrow or POSSIBLE_REACTION_ARROWS[0]
        self.rid = rid

    def __len__(self) -> int:
        return len(self.sparse)

    def clone(self) -> "Reaction":
        return Reaction(self.sparse, self.arrow, self.rid)

    def keys(self, protons=True, water=True) -> Iterable[Compound]:
        gen = self.sparse.keys()
        if water and protons:
            return gen
        elif water:
            return (c for c in gen if c.inchi != PROTON_INCHI)
        elif protons:
            return (c for c in gen if c.inchi != WATER_INCHI)
        else:
            return (
                c
                for c in gen
                if c.inchi != PROTON_INCHI and c.inchi != WATER_INCHI
            )

    def items(self, protons=True, water=True) -> Iterable[Tuple[Compound, int]]:
        gen = self.sparse.items()
        if water and protons:
            return gen
        elif water:
            return ((c, i) for c, i in gen if c.inchi != PROTON_INCHI)
        elif protons:
            return ((c, i) for c, i in gen if c.inchi != WATER_INCHI)
        else:
            return (
                (c, i)
                for c, i in gen
                if c.inchi != PROTON_INCHI and c.inchi != WATER_INCHI
            )

    def get_coeff(self, compound: Compound) -> float:
        return self.sparse.get(compound, 0.0)

    def reverse(self) -> "Reaction":
        """
            reverse the direction of the reaction by negating all
            stoichiometric coefficients
        """
        sparse = dict((k, -v) for (k, v) in self.sparse.items())
        return Reaction(sparse, self.arrow, self.rid)

    def __eq__(self, other: "Reaction") -> bool:
        cpds = set(self.keys(protons=False)).union(other.keys(protons=False))
        for c in cpds:
            if self.get_coeff(c) != other.get_coeff(c):
                return False
        return True

    @staticmethod
    def parse_formula_side(
        s: str, str_to_compound: Callable[[str], Compound]
    ) -> Dict[Compound, float]:
        """
            Parses the side formula, e.g.
            '2 KEGG:C00001 + KEGG:C00002 + 3 KEGG:C00003'
            Ignores stoichiometry.

            Returns:
                The set of CIDs.
        """
        if s.strip() == "null":
            return {}

        compound_bag = {}
        for member in re.split(r"\s+\+\s+", s):
            tokens = member.split(None, 1)
            if len(tokens) == 0:
                continue
            if len(tokens) == 1:
                amount = 1.0
                compound = str_to_compound(member)
            else:
                try:
                    amount = float(tokens[0])
                except ValueError:
                    raise ParseException(f"Non-specific reaction: {s}")
                compound = str_to_compound(tokens[1])

            if compound is None:
                raise ParseException(
                    f"{member} was not found in the " "compound cache"
                )

            compound_bag[compound] = compound_bag.get(compound, 0.0) + amount

        return compound_bag

    @classmethod
    def parse_formula(
        cls,
        str_to_compound: Callable[[str], Compound],
        formula: str,
        rid: Optional[str] = None,
    ) -> object:
        """
        Parse a two-sided reaction definition.

        Parameters
        ----------
        str_to_compound : Callable[[str], Compound]
            A function that returns a compound instance from a string,
            for example, from a database identifier.
        formula : str
            A string representation of the reaction.
        rid : str, optional
            An identifier for the resulting reaction object.

        Returns
        -------
        Reaction
            An object representation of the substrates, products and the
            reaction direction.

        Examples
        --------
        >>> from  equilibrator_cache import Reaction
        >>> Reaction.parse_formula(parse_compound, '2 C00001 = C00002 + C00003')

        """
        tokens = []
        arrow = None
        for arrow in POSSIBLE_REACTION_ARROWS:
            if formula.find(arrow) != -1:
                tokens = formula.split(arrow, 2)
                break

        if len(tokens) < 2:
            raise ValueError(
                f"Reaction does not contain an allowed arrow sign ({arrow}): "
                f" {formula}"
            )

        left = tokens[0].strip()
        right = tokens[1].strip()

        sparse_reaction = {}
        left_dict = Reaction.parse_formula_side(left, str_to_compound)
        right_dict = Reaction.parse_formula_side(right, str_to_compound)
        for cid, count in left_dict.items():
            sparse_reaction[cid] = sparse_reaction.get(cid, 0) - count

        for cid, count in right_dict.items():
            sparse_reaction[cid] = sparse_reaction.get(cid, 0) + count

        # remove compounds that are balanced out in the reaction,
        # i.e. their coefficient is 0
        sparse_reaction = dict(
            filter(lambda x: x[1] != 0, sparse_reaction.items())
        )
        return cls(sparse_reaction, arrow=arrow, rid=rid)

    @staticmethod
    def write_compound_and_coeff(compound: Compound, coeff: float) -> str:
        if np.abs(coeff - 1) < sys.float_info.epsilon:
            return str(compound)
        else:
            return "%g %s" % (coeff, str(compound))

    def __str__(self) -> str:
        """String representation."""
        left = []
        right = []
        for compound, coeff in sorted(self.sparse.items()):
            if coeff < 0:
                left.append(Reaction.write_compound_and_coeff(compound, -coeff))
            elif coeff > 0:
                right.append(Reaction.write_compound_and_coeff(compound, coeff))
        return f"{' + '.join(left)} {self.arrow} {' + '.join(right)}"

    def get_element_data_frame(self) -> pd.DataFrame:
        """
        Tabulate the elemental composition of all reactants.

        Returns
        -------
        pandas.DataFrame
            A data frame where the columns are the compounds and the
            indexes are atomic elements.

        """
        atom_bags = {
            compound: compound.atom_bag or {} for compound in self.keys()
        }

        # create the elemental matrix, where each row is a compound and each
        # column is an element (or e-)
        return pd.DataFrame.from_dict(
            atom_bags, orient="columns", dtype=int
        ).fillna(0)

    def _get_reaction_atom_bag(
        self, raise_exception: bool = False, minimal_stoichiometry: float = None
    ) -> Dict[str, int]:
        """
            Use for checking if all elements are conserved.

            :param raise_exception: if True, raises exception if any of the
            compounds does not have a proper formula
            :param minimal_stoichiometry: if not None, sets the minimal value
            for a non-zero stoichiometry
            Returns:
                An atom_bag of the differences between the sides of the
                reaction. E.g. if there is one extra C on the left-hand
                side, the result will be {'C': -1}.
        """
        element_df = self.get_element_data_frame()

        if np.any((element_df == 0).all(axis=0)):
            warning_str = (
                "cannot generate the reaction atom bag because "
                + "compounds have unspecific formulas: "
                + "%s" % str(self)
            )
            if raise_exception:
                raise ValueError(warning_str)
            else:
                logging.warning(warning_str)
                return None

        stoichiometry = np.array(list(element_df.columns.map(self.get_coeff)))
        unbalanced = element_df @ stoichiometry
        unbalanced = unbalanced[unbalanced != 0]
        atom_bag = unbalanced.to_dict()

        if minimal_stoichiometry is not None:
            # ignore the differences if they are very close to 0
            atom_bag = {
                k: v
                for k, v in atom_bag.items()
                if abs(v) > minimal_stoichiometry
            }

        if len(atom_bag) > 0:
            logging.debug("unbalanced reaction: %s" % str(self))
            for elem, imbalance in atom_bag.items():
                logging.debug(
                    "there are %d more %s atoms on the "
                    "right-hand side" % (imbalance, elem)
                )

        return atom_bag

    def add_stoichiometry(self, cpd: Compound, coeff: float) -> None:
        """Add to an existing stoichiometric coefficient.

        If the compound is not part of the reaction, add it as a new reactant.
        """
        if cpd in self.sparse:
            if self.sparse[cpd] == -coeff:
                self.sparse.pop(cpd)
            else:
                self.sparse[cpd] += coeff
        else:
            self.sparse[cpd] = coeff

    def is_balanced(
        self, ignore_atoms: Tuple[str] = ("H"), raise_exception: bool = False
    ) -> bool:
        """Check if a reaction is balanced

        :param ignore_atoms: tuple containing atoms to ignore
        :param raise_exception: raise Exception if formulas are missing
        :return:
        """
        reaction_atom_bag = self._get_reaction_atom_bag(
            raise_exception=raise_exception
        )

        if reaction_atom_bag is None:
            # this means some compound formulas are missing
            return False

        for atom in ignore_atoms:
            if atom in reaction_atom_bag:
                reaction_atom_bag.pop(atom)

        return len(reaction_atom_bag) == 0

    def balance_with_compound(
        self,
        compound: Compound,
        ignore_atoms: Tuple[str] = ("H"),
        raise_exception: bool = False,
    ):
        """Try to balance the reaction using a specified compound

        :param compound: the compound to use for balancing
        :param ignore_protons: if True, do not try to balance the 'H' atoms
        :param raise_exception: raise Exception if formulas are missing
        :return: A balanced reaction. If the original reaction is already
        balanced, returns it back. Otherwise, return a new balanced reaction,
        or None if the reaction cannot be balanced.
        """

        def get_pivot_atom(compound: Compound) -> Tuple[str, float]:
            # select one atom from the given compound and try to balance it
            # (skip protons if we decided to ignore them)
            if compound.atom_bag is None:
                raise Exception(
                    f"Cannot balance using this compound, it has no "
                    f"formula: {compound.formula}"
                )

            for atom, count in compound.atom_bag.items():
                if atom not in ignore_atoms:
                    return atom, count
            raise Exception(
                f"Cannot balance using this compound, it has no "
                f"relevant atoms: {compound.formula}"
            )

        if self.is_balanced(ignore_atoms, raise_exception):
            return self

        reaction_atom_bag = self._get_reaction_atom_bag(
            raise_exception=raise_exception
        )

        if reaction_atom_bag is None:
            # this means some compound formulas are missing
            return None

        pivot_atom, count = get_pivot_atom(compound)

        new_reaction = self.clone()
        if pivot_atom in reaction_atom_bag:
            new_reaction.add_stoichiometry(
                compound, -reaction_atom_bag[pivot_atom] / float(count)
            )

        if new_reaction.is_balanced(ignore_atoms, raise_exception):
            return new_reaction

    def is_empty(self):
        return len(self.sparse) == 0

    def dense(self, cids):
        s = np.zeros((len(cids), 1))
        for cid, coeff in self.items():
            s[cids.index(cid), 0] = coeff
        return s

    @ureg.check(None, None, "[concentration]", "[temperature]")
    def transform(
        self, p_h: float, ionic_strength: float, temperature: float
    ) -> float:
        """Use the Legendre transform to convert the ddG_over_RT to the
        difference in the transformed energies of this MS and the major MS

        :param p_h:
        :param ionic_strength:
        :param temperature:
        :return: the transformed relative deltaG (in units of RT)
        """
        ddg_over_rt = Q_(0.0)
        # Protons are ignored in the Legendre transform.
        for compound, coeff in self.items(protons=False):
            ddg_over_rt += coeff * compound.transform(
                p_h, ionic_strength, temperature
            )
        return ddg_over_rt

    def _sum_coefficients(self) -> float:
        """
        Calculate the sum of all coefficients (excluding water).

        This is useful for shifting the dG'0 to another set of standard
        concentrations (e.g. 1 mM)

        """
        return sum(c for _, c in self.items(protons=False, water=False))

    def _sum_absolute_coefficients(self) -> float:
        """
            Calculate the sum of all coefficients (excluding water) in
            absolute value.
            This is useful for calculating the reversibility index.
        """
        return sum(abs(c) for _, c in self.items(protons=False, water=False))

    def check_half_reaction_balancing(self):
        """
            :return: The number of electrons that are 'missing' in the
            half-reaction or None if the reaction is not atomwise-balanced.
        """
        atom_bag = self._get_reaction_atom_bag()
        if atom_bag is None:
            return None

        # we ignore proton balancing
        atom_bag.pop("H", 0)

        n_e = atom_bag.pop("e-", 0)
        if len(atom_bag) > 0:
            return None
        else:
            return n_e

    @staticmethod
    def _hashable_reactants(
        sparse: Dict[Compound, float]
    ) -> Tuple[Tuple[int, float]]:
        """Return a unique list of number pairs representing reaction.

        The list fully identifies the biochemical reaction.
        If it is equal to another reaction's string, then they have identical
        stoichiometry.

        :param sparse: a dictionary whose keys are compounds and values are
        stoichiometric coefficients
        :return: a unique list of pairs (compound.id, coefficient)
        """
        if len(sparse) == 0:
            return []

        # sort according to compound ID and normalize the stoichiometric
        # coefficients such that the coeff of the reactant with the lowest
        # ID will be 1
        sorted_compound_list = sorted(sparse.keys(), key=lambda c: c.id)
        sorted_cpd_coeff_list = zip(sorted_compound_list,
                                    map(sparse.get, sorted_compound_list))

        # filter out compounds with zero coefficients
        sorted_cpd_coeff_list = list(filter(lambda x: x[1] != 0,
                                            sorted_cpd_coeff_list))
        if len(sorted_cpd_coeff_list) == 0:
            raise Exception("All stoichiometric ceofficients are 0")
        norm_factor = 1.0 / sorted_cpd_coeff_list[0][1]
        r_list = [
            (cpd.id, norm_factor * coeff)
            for cpd, coeff in sorted_cpd_coeff_list
        ]
        return tuple(r_list)

    def __hash__(self) -> int:
        """Return a hash of the Reaction.

        This hash is useful for finding reactions with the exact same
        stoichiometry. We create a unique formula string based on the
        Compound IDs and coefficients.

        :return: a hash of the Reaction.
        """
        reactants = Reaction._hashable_reactants(self.sparse)
        return hash(reactants)


def create_stoichiometric_matrix_from_reactions(
    reactions: Iterable[Reaction], proton: Compound, water: Compound
) -> pd.DataFrame:
    """Builds a stoichiometric matrix.

    Parameters
    ----------
    reactions : iterable
        The collection of reactions to build a stoichiometric matrix from.
    proton : Compound
        The proton compound.
    water : Compound
        The water compound.

    Returns
    -------
    pandas.DataFrame
        The stoichiometric matrix as a DataFrame whose indexes are the
        compounds and its columns are the reactions (in the same order as
        the input).
    """
    compounds = {c for r in reactions for c in r.sparse}
    # Now get rid of the protons, since we are applying Alberty's
    # framework where their potential is set to 0, and the pH is held
    # as a controlled parameter.
    if proton in compounds:
        compounds.remove(proton)
    if water not in compounds:
        compounds.add(water)

    stoichiometry = pd.DataFrame(0, index=sorted(compounds), columns=reactions)
    for rxn in reactions:
        for met, coef in rxn.items(protons=False):
            # FIXME (Moritz): There can be duplicated reactions (bug?) so we
            #  need to use `.loc` rather than `.at` for now.
            stoichiometry.loc[met, rxn] = coef
    return stoichiometry
