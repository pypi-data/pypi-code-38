# The MIT License (MIT)
#
# Copyright (c) 2013 The Weizmann Institute of Science.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
# Copyright (c) 2018 Institute for Molecular Systems Biology,
# ETH Zurich, Switzerland.
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


"""
Manage the training data for component contributions.

References:
-----------
.. [1] Alberty (2006)
.. [2] Maden (2000)
.. [3] Thauer (1977)
.. [4] Wagman (1982)
.. [5] Dolfing (1992)
.. [6] Dolfing (1994)
.. [7] CRC biochemistry (2010)
.. [8] Prince (1987)
.. [9] Thauer (1977)
.. [10] CRC biochemistry (2010)
.. [11] Alberty (2006)
.. [12] Deppenmeier (2008)
.. [13] Saeki (1985)
.. [14] Unden (1997)

"""


import logging
import warnings
from typing import Iterable, List, Set, Tuple

import numpy as np
import pandas as pd
import quilt

from equilibrator_cache import FARADAY, Q_, R
from equilibrator_cache.exceptions import MissingDissociationConstantsException

from . import (
    DEFAULT_QUILT_PKG,
    Compound,
    ParseException,
    Reaction,
    ccache,
    create_stoichiometric_matrix_from_reactions,
)


logger = logging.getLogger(__name__)


class TrainingData(object):
    """A base class for handling Training Data."""

    def __init__(self):
        """Create a TrainingData object."""
        self.S = None  # a DataFrame containing the stoichiometric matrix
        self.reaction_df = None  # a DataFrame containing all the reaction data
        self._non_decomposable_compounds = []
        quilt.install(DEFAULT_QUILT_PKG, force=True)
        self.quilt_pkg = quilt.load(DEFAULT_QUILT_PKG)

    @property
    def stoichiometric_matrix(self) -> pd.DataFrame:
        """Get the stoichiometric matrix as a DataFrame.

        :return: a Pandas DataFrame
        """
        return self.S

    @property
    def compounds(self) -> List[Compound]:
        """Get the list of compounds.

        :return: A list of Compound objects according to their order in S.
        """
        if self.S is None:
            compounds = {ccache.proton, ccache.water}
            for rxn in self.reaction_df.reaction:
                compounds.update(rxn.keys())
            return sorted(compounds)
        else:
            return self.S.index.tolist()

    @property
    def non_decomposable_compounds(self) -> List[Compound]:
        """Get the list of non-decomposable compounds.

        :return: A list of Compound objects
        """
        return self._non_decomposable_compounds

    @property
    def decomposable_compounds(self) -> List[Compound]:
        """Get the list of decomposable compounds.

        :return: A list of Compound objects
        """
        decomposable_compounds = set(self.compounds).difference(
            self.non_decomposable_compounds
        )
        return sorted(decomposable_compounds)

    @property
    def standard_dg(self) -> pd.Series:
        """Get the standard deltaGs according to the reaction order in S.

        :return: A Pandas Series of the standard detlaGs
        """
        return self.reaction_df.standard_dg

    @property
    def weight(self) -> pd.Series:
        """Get the weights according to the reaction order in S.

        :return:A Pandas Series of the weights
        """
        return self.reaction_df.weight

    def assert_data(self):
        """Ensure all the relevant columns are in the correct units."""
        for col, dim in [
            ("standard_dg_prime", "[energy]/[substance]"),
            ("ionic_strength", "[concentration]"),
            ("temperature", "[temperature]"),
            ("p_h", None),
            ("p_mg", None),
        ]:
            assert col in self.reaction_df.columns

            for v in self.reaction_df[col].values:
                assert v.check(dim)

    def balance_reactions(self) -> None:
        """Balance the reactions.

        Use the chemical formulas from the InChIs to verify that each and
        every reaction is balanced. If it can be easily fixed with protons
        and/or water
        """
        to_remove = []
        to_balance_df = self.reaction_df[self.reaction_df.balance]
        for row in to_balance_df.itertuples(index=True):
            if not row.reaction.is_balanced(
                fix_protons=True, fix_water=True, raise_exception=False
            ):
                warnings.warn(
                    "This reaction cannot be balanced: " f"{row.reaction}"
                )
                to_remove.append(row.Index)

        logger.info(
            "After removing %d unbalanced reactions, "
            "we are left with %d reactions for training",
            len(to_remove),
            len(self.reaction_df),
        )

        self.reaction_df = self.reaction_df.drop(to_remove, axis=0)

    def create_stoichiometric_matrix_from_reactions(self) -> None:
        """Create the stoichiometric matrix for training.

        Convert the list of reactions in sparse notation into a full
        stoichiometric matrix, where the rows (compounds) are in the same
        order as in 'compounds' and the columns match the reaction indices.
        """
        self.S = create_stoichiometric_matrix_from_reactions(
            self.reaction_df.reaction, ccache.proton, ccache.water
        )
        self.S.columns = self.reaction_df.index

    @property
    def reactions(self) -> Iterable[Reaction]:
        """Get the training reactions.

        :return: an iterator for all the reactions in the training data
        """
        return self.S.apply(Reaction)

    def reverse_transform(self) -> None:
        """Reverse Legendre transform.

        Performs a Reverse Legendre transform on all the reactions in the
        training data. That means we convert them from the biochemical (
        transformed) standard deltaG' to the chemical (untransformed)
        standard deltaG.
        """
        self.reaction_df = self.reaction_df.assign(
            **{"standard_dg": list(self._reverse_transform())}
        )

    def _reverse_transform(self) -> Iterable[float]:
        """Reverse Legendre transform helper function.

        A helper function for reverse_transform()
        """
        for row in self.reaction_df.itertuples():
            standard_dg = row.standard_dg_prime
            try:
                ddg_over_rt = row.reaction.transform(
                    p_h=row.p_h,
                    ionic_strength=row.ionic_strength,
                    temperature=row.temperature,
                )
                standard_dg -= ddg_over_rt * R * row.temperature
            except MissingDissociationConstantsException as e:
                logger.warning(f"Cannot reverse transform {row.reaction}: {e}")
            yield standard_dg


class ToyTrainingData(TrainingData):
    """Toy training data class."""

    def __init__(self):
        """Create the ToyTrainingData object."""
        super().__init__()

        self.reaction_df = self.quilt_pkg.train.toy_training_data().copy()
        self.reaction_df.loc[:, "reaction"] = [
            Reaction.parse_formula(ccache.get_compound, r)
            for r in self.reaction_df["reaction"]
        ]

        # add units to the relevant columns:
        for col, unit in [
            ("standard_dg_prime", "kJ/mol"),
            ("ionic_strength", "M"),
            ("temperature", "K"),
            ("p_h", None),
            ("p_mg", None),
        ]:
            self.reaction_df[col] = self.reaction_df[col].apply(
                lambda x: Q_(x, unit)
            )

        self.assert_data()
        self.create_stoichiometric_matrix_from_reactions()
        self.reverse_transform()


class FullTrainingData(TrainingData):
    """Full training data class."""

    def __init__(self) -> object:
        """Create the FullTrainingData object."""
        super().__init__()

        logger.info("Reading the training data files")
        self.reaction_df, compounds_that_do_not_decompose = (
            self.get_all_reactions()
        )

        compounds_that_do_not_decompose.update(
            [Reaction.PROTON_COMPOUND, Reaction.WATER_COMPOUND]
        )
        self.compounds_that_do_not_decompose = list(
            compounds_that_do_not_decompose
        )

        compounds = set(self.compounds).difference(
            self.compounds_that_do_not_decompose
        )
        compounds = [cpd for cpd in compounds if cpd.atom_bag is None]

        if len(compounds) > 0:
            for compound in sorted(compounds):
                if compound.inchi is not None:
                    warnings.warn(
                        f"Compound {compound} has no atom bag, but "
                        f"does have an InChI: {compound.inchi}."
                    )
                else:
                    warnings.warn(
                        f"Compound {compound} has neither an atom "
                        f"bag nor an InChI."
                    )

        self.assert_data()

        logger.info("Balancing reactions with H2O and H+")
        self.balance_reactions()

        logger.info("Creating the training stoichiometric matrix")
        self.create_stoichiometric_matrix_from_reactions()

        logger.info("Applying reverse Legendre transform on dG' values")
        self.reverse_transform()

    def read_tecrdb(self) -> pd.DataFrame:
        """Load a data frame with information from the TECRdb (NIST).

        The component-contribution package distributes data tables with
        information on the 'thermodynamics of enzyme-catalyzed
        reactions'[1, 2]_ that are used as training data.

        :return: a Pandas DataFrame of the TECRDB reaction

        References
        ----------
        .. [1] Goldberg, Robert N., Yadu B. Tewari, and Talapady N. Bhat.
               “Thermodynamics of Enzyme-Catalyzed Reactions—a Database for
               Quantitative Biochemistry.” Bioinformatics 20, no. 16
               (November 1, 2004): 2874–77.
               https://doi.org/10.1093/bioinformatics/bth314.
        .. [2] http://xpdb.nist.gov/enzyme_thermodynamics/

        """
        tecr_df = self.quilt_pkg.train.TECRDB().copy()

        # assume a default ionic strength of 0.25 M
        tecr_df.ionic_strength.fillna(0.25, inplace=True)

        # remove rows with missing essential data
        tecr_df = tecr_df[
            ~pd.isnull(tecr_df[["K_prime", "temperature", "p_h"]]).any(axis=1)
        ]

        for col, unit in [
            ("K_prime", None),
            ("ionic_strength", "M"),
            ("temperature", "K"),
            ("p_h", None),
            ("p_mg", None),
        ]:
            tecr_df[col] = tecr_df[col].apply(lambda x: Q_(x, unit))

        # calculate the dG'0 from the Keq and T
        standard_dg_primes = [
            (-R * row.temperature * np.log(row.K_prime)).to("kJ/mol")
            for row in tecr_df.itertuples()
        ]
        tecr_df = tecr_df.assign(
            **{"standard_dg_prime": standard_dg_primes, "balance": True}
        )

        # parse the reaction
        tecr_df.loc[:, "reaction"] = tecr_df["reaction"].apply(
            Reaction.parse_formula
        )

        # skip reactions that could not be parsed
        tecr_df = tecr_df[~pd.isnull(tecr_df["reaction"])]

        tecr_df.drop(
            ["url", "method", "K", "K_prime", "eval", "EC", "enzyme_name"],
            axis=1,
            inplace=True,
        )

        logger.debug(
            "Successfully added %d reactions from TECRDB" % tecr_df.shape[0]
        )
        return tecr_df

    def read_formations(self) -> Tuple[pd.DataFrame, Set[Compound]]:
        """Read the Formation Energy data from literature.

        All the data we have for formation energies from [1-6].

        :return: a 2-tuple of the Pandas DataFrame of reactions, and the set
        of compounds that do not decompose into groups.
        """
        formation_df = (
            self.quilt_pkg.train.formation_energies_transformed().copy()
        )

        compounds = formation_df["cid"].apply(ccache.get_compound)

        if pd.isnull(compounds).any():
            missing_cids = formation_df.loc[pd.isnull(compounds), "cid"]
            raise ParseException(
                "Cannot find some of the compounds in the "
                "cache: " + str(missing_cids)
            )

        compounds_that_do_not_decompose = set(
            compounds.loc[formation_df.decompose == 0].values
        )

        # skip compounds that have no formation energy (they are in the table
        # only in order to indicate something, for example that they should
        # not be decomposed)
        formation_df = formation_df[~pd.isnull(formation_df.standard_dg_prime)]

        for col, unit in [
            ("standard_dg_prime", "kJ/mol"),
            ("ionic_strength", "M"),
            ("temperature", "K"),
            ("p_h", None),
            ("p_mg", None),
        ]:
            formation_df[col] = formation_df[col].apply(lambda x: Q_(x, unit))

        formation_df = formation_df.assign(
            **{
                "reaction": compounds.apply(lambda c: Reaction({c: 1})),
                "balance": False,
                "description": formation_df["name"] + " formation",
            }
        )
        formation_df.drop(
            ["name", "cid", "remark", "decompose"], axis=1, inplace=True
        )

        logger.debug(
            "Successfully added %d formation energies" % formation_df.shape[0]
        )
        return formation_df, compounds_that_do_not_decompose

    def read_redox(self) -> pd.DataFrame:
        """Read the Reduction potential from literature.

        All the reduction potentials we have from [7-14].

        :return: a Pandas DataFrame of the redox reactions.
        """
        redox_df = self.quilt_pkg.train.redox().copy()

        for col, unit in [
            ("standard_E_prime", "V"),
            ("ionic_strength", "M"),
            ("temperature", "K"),
            ("p_h", None),
            ("p_mg", None),
        ]:
            redox_df[col] = redox_df[col].apply(lambda x: Q_(x, unit))

        compounds_ox = redox_df["CID_ox"].apply(ccache.get_compound)
        compounds_red = redox_df["CID_red"].apply(ccache.get_compound)
        reaction = [
            Reaction({c_ox: -1, c_red: 1})
            for c_ox, c_red in zip(compounds_ox, compounds_red)
        ]

        delta_nH = redox_df.nH_red - redox_df.nH_ox
        delta_charge = redox_df.charge_red - redox_df.charge_ox
        redox_df["delta_e"] = delta_nH - delta_charge

        standard_dg_primes = [
            (-FARADAY * row.standard_E_prime * row.delta_e).to("kJ/mol")
            for row in redox_df.itertuples()
        ]

        redox_df = redox_df.assign(
            **{
                "reaction": reaction,
                "description": redox_df["name"] + " redox",
                "standard_dg_prime": standard_dg_primes,
                "balance": False,
            }
        )
        redox_df.drop(
            [
                "name",
                "CID_ox",
                "CID_red",
                "charge_ox",
                "charge_red",
                "nH_ox",
                "nH_red",
                "standard_E_prime",
                "delta_e",
            ],
            axis=1,
            inplace=True,
        )

        logger.debug(
            "Successfully added %d redox potentials" % redox_df.shape[0]
        )
        return redox_df

    def get_all_reactions(self) -> Tuple[pd.DataFrame, Set[Compound]]:
        """Get the full list of training reactions.

        :return: a 2-tuple of the Pandas DataFrame of reactions, and the set
        of compounds that do not decompose into groups.
        """
        tecr_df = self.read_tecrdb()
        tecr_df["weight"] = 1.0

        formation_df, compounds_that_do_not_decompose = self.read_formations()
        formation_df["weight"] = 1.0

        redox_df = self.read_redox()
        redox_df["weight"] = 1.0

        reaction_df = pd.concat([tecr_df, formation_df, redox_df], sort=False)
        reaction_df.reset_index(drop=True, inplace=True)

        return reaction_df, compounds_that_do_not_decompose
