"""analyze pathways using thermodynamic models."""
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


import csv
import logging
import warnings
from io import IOBase
from typing import Callable, Iterable, List, TextIO, Tuple

import numpy as np
from sbtab import SBtab
from scipy.linalg import fractional_matrix_power

from equilibrator_cache.reaction import (
    create_stoichiometric_matrix_from_reactions,
)

from . import (
    Q_,
    Compound,
    R,
    ccache,
    default_I,
    default_pH,
    default_pMg,
    default_T,
    strip_units,
)
from .bounds import Bounds
from .component_contribution import ComponentContribution
from .phased_reaction import PhasedReaction
from .thermo_models import PathwayMDFData, PathwayThermoModel


class Pathway(object):
    """A pathway parsed from user input.

    Designed for checking input prior to converting to a stoichiometric model.
    """

    def __init__(self,
                 reactions: List[PhasedReaction],
                 fluxes: np.array,
                 standard_dg_primes: np.array = None,
                 dg_sigma: np.array = None,
                 bounds: Bounds = None,
                 p_h: float = default_pH,
                 p_mg: float = default_pMg,
                 ionic_strength: float = default_I,
                 temperature: float = default_T
                 ) -> object:
        """Initialize.

        Args:
            reactions: a list of gibbs.reaction.Reaction objects.
            fluxes: numpy.array of relative fluxes in same order as reactions.
            standard_dg_primes: reaction energies (in kJ/mol)
            dg_sigma: square root of the uncertainty covariance matrix
                (in kJ/mol)
            bounds: bounds on metabolite concentrations.
                Uses default bounds if None provided.
        """
        self.reactions = reactions
        Nr = len(reactions)

        if bounds is None:
            self._bounds = Bounds.GetDefaultBounds().Copy()
        else:
            self._bounds = bounds.Copy()

        self.S = create_stoichiometric_matrix_from_reactions(reactions,
                                                             ccache.proton,
                                                             ccache.water)

        self.fluxes = fluxes
        assert self.fluxes.shape == (Nr, )

        self.comp_contrib = None
        if standard_dg_primes is None:
            assert dg_sigma is None, ("If standard_dg_primes are not "
                                      "provided, dg_sigme must also be None")
            self.set_aqueous_params(
                p_h=p_h, p_mg=p_mg, ionic_strength=ionic_strength,
                temperature=temperature)
        else:
            assert standard_dg_primes.shape == (Nr,)
            # dGr should be orthogonal to nullspace of S
            # If not, dGr is not contained in image(S) and then there
            # is no consistent set of dGfs that generates dGr and the
            # first law of thermo is violated by the model.
            S_T = self.S.T.values
            S_inv = np.linalg.pinv(S_T)
            null_proj = np.eye(self.S.shape[1]) - S_T @ S_inv
            projected = null_proj @ standard_dg_primes.T
            assert (projected < Q_("1e-8 kJ/mol")).all(), (
                "Supplied reaction standard deltaG values are inconsistent "
                "with the stoichiometric matrix."
            )

            self.standard_dg_primes = standard_dg_primes

            if dg_sigma is None:
                self.dg_sigma = np.zeros((len(reactions), len(reactions)))
            else:
                assert dg_sigma.shape == (Nr, Nr)
                self.dg_sigma = dg_sigma

        # Set the compound names by to their default strings, these names can
        # be changed later using the same function (set_compound_names)
        self.set_compound_names(str)

    def set_aqueous_params(
        self,
        p_h: float = None,
        p_mg: float = None,
        ionic_strength: float = None,
        temperature: float = None
    ) -> None:
        """Set the aqueous conditions and recalculate the standard dG' values.

        :param p_h:
        :param p_mg:
        :param ionic_strength:
        :param temperature:
        """
        if self.comp_contrib is None:
            p_h = p_h or default_pH
            p_mg = p_mg or default_pMg
            ionic_strength = ionic_strength or default_I
            temperature = temperature or default_T
            self.comp_contrib = ComponentContribution(
                p_h=p_h, p_mg=p_mg, ionic_strength=ionic_strength,
                temperature=temperature
            )
        else:
            if p_h is not None:
                self.comp_contrib.p_h = p_h
            if p_mg is not None:
                self.comp_contrib.p_mg = p_mg
            if ionic_strength is not None:
                self.comp_contrib.ionic_strength = ionic_strength
            if temperature is not None:
                self.comp_contrib.temperature = temperature

        RT = R * self.comp_contrib.temperature

        standard_dg_primes, dg_uncertainties = \
            self.comp_contrib.standard_dg_prime_multi(self.reactions)

        self.standard_dg_primes = strip_units(standard_dg_primes / RT)

        dg_uncertainties /= RT ** 2
        dg_uncertainties = strip_units(dg_uncertainties)
        self.dg_sigma = fractional_matrix_power(dg_uncertainties, 0.5)

    def set_compound_names(
        self,
        mapping: Callable[[Compound], str]
    ) -> None:
        """Use alternative compound names for outputs such as plots.

        :param mapping: a dictionary mapping compounds to their names in the
        model
        """
        self.compound_names = list(map(mapping, self.S.index))

    @property
    def bounds(self) -> Tuple[Iterable[float], Iterable[float]]:
        """Get the concentration bounds.

        The order of compounds is according to the stoichiometric matrix index.
        :return: tuple of (lower bounds, upper bounds)
        """
        return self._bounds.GetBounds(self.S.index)

    @property
    def ln_conc_lb(self) -> np.array:
        """Get the log lower bounds on the concentrations.

        The order of compounds is according to the stoichiometric matrix index.
        :return: a NumPy array of the log lower bounds
        """
        return np.array(list(map(float,
                                 self._bounds.GetLnLowerBounds(self.S.index))))

    @property
    def ln_conc_ub(self) -> np.array:
        """Get the log upper bounds on the concentrations.

        The order of compounds is according to the stoichiometric matrix index.
        :return: a NumPy array of the log upper bounds
        """
        return np.array(list(map(float,
                                 self._bounds.GetLnUpperBounds(self.S.index))))

    @staticmethod
    def get_compounds(reactions: Iterable[PhasedReaction]) -> List[Compound]:
        """Get a unique list of all compounds in all reactions.

        :param reactions: an iterator of reactions
        :return: a list of unique compounds
        """
        compounds = set()
        for r in reactions:
            compounds.update(r.keys())

        return sorted(compounds)

    def calc_mdf(self, stdev_factor: float = 1.0) -> PathwayMDFData:
        """Calculate the Max-min Driving Force.

        :param stdev_factor: the factor by which to multiply the uncertainties
        :return: a PathwayMDFData object with the results
        """
        return PathwayThermoModel(self, stdev_factor).FindMDF()

    @property
    def reaction_ids(self) -> Iterable[str]:
        """Iterate through all the reaction IDs.

        :return: the reaction IDs
        """
        return map(lambda rxn: rxn.rid, self.reactions)

    @property
    def reaction_formulas(self) -> Iterable[str]:
        """Iterate through all the reaction formulas.

        :return: the reaction formulas
        """
        return map(str, self.reactions)

    @property
    def net_reaction(self) -> PhasedReaction:
        """Calculate the sum of all the reactions in the pathway.

        :return: the net reaction
        """
        v = np.array(list(map(float, self.fluxes)))
        net_rxn_stoich = self.S @ v
        net_rxn_stoich = net_rxn_stoich[net_rxn_stoich != 0]
        sparse = net_rxn_stoich.to_dict()
        return PhasedReaction(sparse)

    @classmethod
    def from_csv_file(cls,
                      f: TextIO,
                      bounds: Bounds = None,
                      p_h: float = default_pH,
                      p_mg: float = default_pMg,
                      ionic_strength: float = default_I,
                      temperature: float = default_T) -> object:
        """Parse a CSV file and return a Pathway object.

        Caller responsible for closing f.

        :param f: file-like object containing CSV data describing the pathway
        :param bounds: a Bounds object
        :param p_h:
        :param p_mg:
        :param ionic_strength:
        :param: temperature:
        :return: a Pathway object
        """
        reactions = []
        fluxes = []

        for row in csv.DictReader(f):
            rxn_formula = row.get('ReactionFormula')

            flux = float(row.get('Flux', 0.0))
            logging.debug('formula = %f x (%s)', flux, rxn_formula)

            rxn = PhasedReaction.parse_formula(rxn_formula)
            rxn.check_full_reaction_balancing()

            reactions.append(rxn)
            fluxes.append(flux)

        v = np.array(fluxes)
        pp = Pathway(reactions, v, bounds=bounds,
                     p_h=p_h, p_mg=p_mg, ionic_strength=ionic_strength,
                     temperature=temperature)
        return pp

    @classmethod
    def open_sbtab(cls, sbtab) -> SBtab.SBtabDocument:
        """Open an SBtabDocument.

        :param sbtab: a file name, stream, or SBtabDocument to open
        :return: an SBtabDocument object
        """
        if type(sbtab) == SBtab.SBtabDocument:
            return sbtab
        elif type(sbtab) == str:
            return SBtab.read_csv(sbtab, "pathway")
        elif isinstance(sbtab, IOBase):
            sbtab_contents = sbtab.read()
            if type(sbtab_contents) == bytes:
                sbtab_contents = sbtab_contents.decode('utf-8')
            return SBtab.SBtabDocument("pathway", sbtab_contents,
                                       "unnamed_sbtab.tsv")

        raise ValueError("sbtab must be either a file name or a Stream "
                         "object")

    @classmethod
    def from_sbtab(cls, sbtab) -> object:
        """Parse and SBtabDocument and return a Pathway.

        :param sbtab: a file name, stream, or SBtabDocument to open
        :return: a Pathway object
        """
        sbtabdoc = cls.open_sbtab(sbtab)
        table_ids = ['ConcentrationConstraint', 'Reaction', 'RelativeFlux',
                     'Parameter']
        dfs = []

        for table_id in table_ids:
            sbtab = sbtabdoc.get_sbtab_by_id(table_id)
            if sbtab is None:
                tables = ', '.join(map(lambda s: s.table_id, sbtabdoc.sbtabs))
                raise ValueError(f"The SBtabDocument must have a table "
                                 f"with the following ID: {table_id}, "
                                 f"however, only these tables were "
                                 f"found: {tables}")
            dfs.append(sbtab.to_data_frame())

        bounds_df, reaction_df, flux_df, param_df = dfs

        try:
            bounds_sbtab = sbtabdoc.get_sbtab_by_id('ConcentrationConstraint')
            bounds_unit_str = bounds_sbtab.get_attribute('Unit')
            bounds, name_to_compound = Bounds.from_dataframe(bounds_df,
                                                             bounds_unit_str)
        except SBtab.SBtabError:
            # if the unit is not defined in the header, we assume it is given
            # next to each bound individually
            bounds, name_to_compound = Bounds.from_dataframe(bounds_df)

        reactions = []
        reaction_ids = []
        for row in reaction_df.itertuples():
            rxn = PhasedReaction.parse_formula(name_to_compound.get,
                                               row.ReactionFormula)
            rxn.rid = row.ID
            if not rxn.is_balanced(ignore_atoms=("H")):
                warnings.warn(f"Reaction {rxn.rid} is not balanced")
            reactions.append(rxn)
            if row.ID in reaction_ids:
                raise KeyError(f"Reaction IDs must be unique, but you have "
                               f"{row.ID} twice")
            reaction_ids.append(row.ID)

        flux_df = flux_df[flux_df['QuantityType'] == 'flux']
        flux_df.set_index('Reaction', inplace=True)
        flux_df.Value = flux_df.Value.apply(float)
        v = flux_df.loc[reaction_ids, 'Value'].values * Q_("dimensionless")

        # grab rows containing keqs and calculate the standard Gibbs
        # reaction energies from the equilibrium constants
        keq_df = param_df[param_df['QuantityType'] == 'equilibrium constant']
        keq_df.set_index('Reaction', inplace=True)
        if not set(reaction_ids).issubset(keq_df.index):
            # TODO: change the SBtab format to make it explicit when to use
            #  the given equilibrium constants, and when to use
            #  component-contribution.
            warnings.warn("Not all reactions have Keq values in the "
                          "Parameter table. Therefore, we use "
                          "Component-Contribution to calculate all of them.")
            # TODO: read the aqueous conditions directly from the SBtab file
            p_h = default_pH
            p_mg = default_pMg
            ionic_strength = default_I
            temperature = default_T
            pp = Pathway(reactions, v, bounds=bounds,
                         p_h=p_h, p_mg=p_mg, ionic_strength=ionic_strength,
                         temperature=temperature)
        else:
            keq_df.Value = keq_df.Value.apply(float)
            keq = keq_df.loc[reaction_ids, 'Value'].values
            standard_dg_primes = -np.log(keq) * R * default_T
            pp = Pathway(reactions, v, standard_dg_primes, bounds=bounds)

        # override the compound names with the ones in the SBtab
        compound_to_name = dict(map(reversed, name_to_compound.items()))
        pp.set_compound_names(compound_to_name.get)
        return pp
