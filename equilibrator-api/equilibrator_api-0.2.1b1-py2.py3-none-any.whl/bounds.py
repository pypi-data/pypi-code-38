"""Define lower and upper bounds on compounds."""
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


from typing import Dict, Iterable, TextIO, Tuple

import pandas as pd
import pkg_resources
from numpy import log

from . import (
    Q_,
    Compound,
    ccache,
    default_conc_lb,
    default_conc_ub,
    standard_concentration,
    ureg,
)


class BaseBounds(object):
    """A base class for declaring bounds on things."""

    def Copy(self):
        """Return a (deep) copy of self."""
        raise NotImplementedError

    def GetLowerBound(self, compound: Compound):
        """Get the lower bound for this key.

        Args:
            key: a compound
        """
        raise NotImplementedError

    def GetUpperBound(self, compound: Compound):
        """Get the upper bound for this key.

        Args:
            key: a compound
        """
        raise NotImplementedError

    def GetLowerBounds(self, compounds: Iterable[Compound]) -> Iterable[float]:
        """Get the bounds for a set of keys in order.

        :param compounds: an iterable of Compounds
        :return:  an iterable of the lower bounds
        """
        return map(self.GetLowerBound, compounds)

    def GetUpperBounds(self, compounds: Iterable[Compound]) -> Iterable[float]:
        """Get the bounds for a set of keys in order.

        :param compounds: an iterable of Compounds
        :return:  an iterable of the upper bounds
        """
        return map(self.GetUpperBound, compounds)

    def GetBoundTuple(self, compound: Compound) -> Tuple[float, float]:
        """Get both upper and lower bounds for this key.

        :param compound: a Compound object
        :return: a 2-tuple (lower bound, upper bound)
        """
        return self.GetLowerBound(compound), self.GetUpperBound(compound)

    def GetBounds(
        self, compounds: Iterable[Compound]
    ) -> Tuple[Iterable[float], Iterable[float]]:
        """Get the bounds for a set of compounds.

        :param compounds: an iterable of Compounds
        :return: a 2-tuple (lower bounds, upper bounds)
        """
        bounds = map(self.GetBoundTuple, compounds)
        lbs, ubs = zip(*bounds)
        return lbs, ubs

    @staticmethod
    @ureg.check("[concentration]")
    def conc2ln_conc(b: float) -> float:
        """Convert a concentration to log-concentration.

        :param b: a concentration
        :return: the log concentration
        """
        return log(b / standard_concentration)

    def GetLnBounds(
        self, compounds: Iterable[Compound]
    ) -> Tuple[Iterable[float], Iterable[float]]:
        """Get the log-bounds for a set of compounds.

        :param compounds: an iterable of Compounds
        :return: a 2-tuple (log lower bounds, log upper bounds)
        """
        lbs, ubs = self.GetBounds(compounds)

        return map(self.conc2ln_conc, lbs), map(self.conc2ln_conc, ubs)

    def GetLnLowerBounds(
        self, compounds: Iterable[Compound]
    ) -> Iterable[float]:
        """Get the log lower bounds for a set of compounds.

        :param compounds: an iterable of Compounds
        :return: an iterable of log lower bounds
        """
        lbs = self.GetLowerBounds(compounds)
        return map(self.conc2ln_conc, lbs)

    def GetLnUpperBounds(
        self, compounds: Iterable[Compound]
    ) -> Iterable[float]:
        """Get the log upper bounds for a set of compounds.

        :param compounds: an iterable of Compounds
        :return: an iterable of log upper bounds
        """
        ubs = self.GetUpperBounds(compounds)
        return map(self.conc2ln_conc, ubs)

    @ureg.check(None, None, "[concentration]", "[concentration]")
    def SetBounds(self, compound: Compound, lb: float, ub: float):
        """Set bounds for a specific key.

        Args:
            key: a string representation of a KEGG compound ID,
                 i.e. C00001 for water
            lb: the lower bound value
            ub: the upper bound value
        """
        assert lb <= ub
        self.lower_bounds[compound] = lb
        self.upper_bounds[compound] = ub


class Bounds(BaseBounds):
    """Contains upper and lower bounds for various keys.

    Allows for defaults
    """

    @ureg.check(None, None, None, "[concentration]", "[concentration]")
    def __init__(
        self,
        lower_bounds: Dict[Compound, float] = None,
        upper_bounds: Dict[Compound, float] = None,
        default_lb: float = default_conc_lb,
        default_ub: float = default_conc_ub,
    ) -> object:
        """Initialize the bounds object.

        Args:
            lower_bounds: a dictionary mapping keys to float lower bounds
            upper_bounds: a dictionary mapping keys to float upper bounds
            default_lb: default lower bound to if no specific one is provided
            default_lb: default upper bound to if no specific one is provided
        """
        self.lower_bounds = lower_bounds or dict()
        self.upper_bounds = upper_bounds or dict()
        for b in self.lower_bounds.values():
            assert b.check("[concentration]")
        for b in self.upper_bounds.values():
            assert b.check("[concentration]")

        self.default_lb = default_lb
        self.default_ub = default_ub

    @classmethod
    @ureg.check(None, None, "[concentration]", "[concentration]")
    def from_csv(
        cls,
        f: TextIO,
        default_lb: float = default_conc_lb,
        default_ub: float = default_conc_ub,
    ) -> object:
        """Read bounds from a .csv file.

        Assume that all the concentrations are given in units of molar.

        :param f: an open .csv file stream
        :param default_lb: default lower bound to if no specific one is
        provided
        :param default_ub: default upper bound to if no specific one is
        provided
        :return: a Bounds object
        """
        lbs: Dict[Compound, float] = dict()
        ubs: Dict[Compound, float] = dict()
        bounds_df = pd.read_csv(f)

        for row in bounds_df.itertuples():
            compound = ccache.get_compound(row.compound_id)
            lbs[compound] = row.lb * ureg.molar
            ubs[compound] = row.ub * ureg.molar

        bounds = Bounds(lbs, ubs, default_lb, default_ub)
        bounds._check_bounds()
        return bounds

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the list of bounds to a Pandas DataFrame.

        :return: a Pandas DataFrame of all bounds
        """
        data = []
        for c in self.lower_bounds.keys():
            data.append((str(c), self.GetLowerBound(c), self.GetUpperBound(c)))
        compound_df = pd.DataFrame(data=data, columns=["compound", "lb", "ub"])
        return compound_df

    @classmethod
    @ureg.check(None, None, None, "[concentration]", "[concentration]")
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        bounds_unit: str = None,
        default_lb: float = default_conc_lb,
        default_ub: float = default_conc_ub,
    ) -> Tuple[object, Dict[Compound, str]]:
        """Read bounds from a Pandas DataFrame.

        :param df: a pandas.DataFrame with the bounds
        :param bounds_unit: optional string of the units. If None, assume
        the units provided in each cell in the DataFrame.
        :param default_lb: default lower bound to if no specific one is
        provided
        :param default_ub: default upper bound to if no specific one is
        provided
        :return:
        """
        df.set_index("Compound", inplace=True)

        # legacy code, before we always assumed that the compound IDs are
        # from KEGG
        if "Compound:Identifiers:kegg.compound" in df.columns:
            df["Compound:Identifiers"] = (
                "KEGG:" + df["Compound:Identifiers:kegg.compound"]
            )

        # now, by default, we assume the namespaces are provided as part of the
        # reaction formulas
        if "Compound:Identifiers" not in df.columns:
            raise KeyError(
                "Could not find a column of Compound:Identifiers "
                "in the ConcentrationConstraints table"
            )

        df["Compound"] = df["Compound:Identifiers"].apply(ccache.get_compound)

        if pd.isnull(df.Compound).any():
            accessions_not_found = df.loc[
                pd.isnull(df.Compound), "Compound:Identifiers"
            ]
            error_msg = str(accessions_not_found.to_dict())
            raise KeyError(
                f"Some compounds not found in equilibrator-cache: "
                f"{error_msg}"
            )
        name_to_compound = df.Compound.to_dict()

        df.set_index("Compound", inplace=True)

        if bounds_unit is not None:
            lbs = df["Concentration:Min"].apply(
                lambda x: Q_(float(x), bounds_unit)
            )
            ubs = df["Concentration:Max"].apply(
                lambda x: Q_(float(x), bounds_unit)
            )
        else:
            lbs = df["Concentration:Min"].apply(Q_)
            ubs = df["Concentration:Max"].apply(Q_)

        bounds = Bounds(lbs.to_dict(), ubs.to_dict(), default_lb, default_ub)
        bounds._check_bounds()

        return bounds, name_to_compound

    def _check_bounds(self) -> None:
        assert self.default_lb <= self.default_ub, (
            f"default lower bound ({self.default_lb}) is higher than the "
            f"default upper bound ({self.default_ub})"
        )

        for compound in self.upper_bounds:
            lb = self.GetLowerBound(compound)
            ub = self.GetUpperBound(compound)
            assert lb <= ub, (
                f"lower bound ({self.default_lb}) for {compound} is higher "
                f"than the upper bound ({self.default_ub})"
            )

    def Copy(self) -> object:
        """Return a deep copy of self."""
        new_lb = dict(self.lower_bounds.items())
        new_ub = dict(self.upper_bounds.items())
        return Bounds(new_lb, new_ub, self.default_lb, self.default_ub)

    def GetLowerBound(self, compound: Compound) -> float:
        """Get the lower bound for this key.

        :param compound: a compound
        :return: the lower bound
        """
        return self.lower_bounds.get(compound, self.default_lb)

    def GetUpperBound(self, compound: Compound):
        """Get the upper bound for this key.

        :param compound: a compound
        :return: the upper bound
        """
        return self.upper_bounds.get(compound, self.default_ub)

    # the default is generated only at the first call of GetDefaultBounds()
    # the reason to do this, is because looking up all the cofactor compounds
    # in the cache takes about 20 seconds
    DEFAULT_BOUNDS = None

    @staticmethod
    def GetDefaultBounds() -> object:
        """Return the default lower and upper bounds for a pre-determined list.

        :return: a Bounds object with the default values
        """
        if Bounds.DEFAULT_BOUNDS is None:
            COFACTORS_FNAME = pkg_resources.resource_filename(
                "equilibrator_api", "data/cofactors.csv"
            )
            with open(COFACTORS_FNAME, "r") as fp:
                Bounds.DEFAULT_BOUNDS = Bounds.from_csv(fp)
        return Bounds.DEFAULT_BOUNDS
