"""thermo_models contains tools for running MDF and displaying results."""
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
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from optlang.glpk_interface import Constraint, Model, Objective, Variable

from . import Q_, R, default_T, standard_concentration, ureg


class PathwayMDFData(object):
    """Handle MDF results.

    PathwayMDFData is a container class for MDF results, with plotting
    capabilities.
    """

    def __init__(
        self,
        pathway,
        B: float,
        I_dir: np.array,
        lnC: np.array,
        y: np.array,
        reaction_prices: np.array,
        compound_prices: np.array,
    ) -> object:
        """Create PathwayMDFData object.

        :param pathway: a Pathway object
        :param B: the MDF value (in units of RT)
        :param I_dir: matrix of flux directions
        :param lnC: log concentrations at MDF optimum
        :param y: uncertainty matrix coefficients at MDF optimum
        :param reaction_prices: shadow prices of reactions
        :param compound_prices: shadow prices of compound concentrations
        """
        self.mdf = B * R * default_T
        self.bounds = pathway._bounds.Copy()

        concentrations = np.exp(lnC) * standard_concentration

        standard_dg_primes = pathway.standard_dg_primes
        physiological_dg_prime = PathwayMDFData.calc_physiological_dg(pathway)
        optimized_dg_prime = PathwayMDFData.calc_dg(pathway, concentrations)

        # add the calculated error values (due to the dG'0 uncertainty)
        optimized_dg_prime += pathway.dg_sigma @ y

        # adjust dG to flux directions and convert to kJ/mol
        RT = R * pathway.comp_contrib.temperature
        standard_dg_primes = (I_dir @ standard_dg_primes) * RT
        physiological_dg_prime = (I_dir @ physiological_dg_prime) * RT
        optimized_dg_prime = (I_dir @ optimized_dg_prime) * RT

        # all dG values are in units of RT, so we convert them to kJ/mol
        reaction_data = zip(
            pathway.reaction_ids,
            pathway.reaction_formulas,
            pathway.fluxes,
            standard_dg_primes,
            physiological_dg_prime,
            optimized_dg_prime,
            reaction_prices,
        )
        self.reaction_df = pd.DataFrame(
            data=list(reaction_data),
            columns=[
                "reaction_id",
                "reaction_formula",
                "flux",
                "standard_dg_prime",
                "physiological_dg_prime",
                "optimized_dg_prime",
                "shadow_price",
            ],
        )

        compound_data = zip(
            pathway.compound_names, concentrations, compound_prices
        )

        self.compound_df = pd.DataFrame(
            data=list(compound_data),
            columns=["compound", "concentration", "shadow_price"],
        )
        lbs, ubs = pathway.bounds
        self.compound_df["lower_bound"] = list(lbs)
        self.compound_df["upper_bound"] = list(ubs)

    @staticmethod
    def calc_physiological_dg(pathway: object) -> np.array:
        """Add the effect of reactant physiological concentrations on the dG'.

        :param pathway: Pathway object
        :return: the reaction energies (in units of RT)
        """
        dg_adj = np.array(
            [float(r.physiological_dg_correction()) for r in pathway.reactions]
        )
        return pathway.standard_dg_primes + dg_adj

    @staticmethod
    @ureg.check(None, "[concentration]")
    def calc_dg(pathway: object, concentrations: np.array) -> np.array:
        """Add the effect of reactant concentrations on the dG'.

        :param pathway: Pathway object
        :param concentrations: a NumPy array of concentrations
        :return: the reaction energies (in units of RT)
        """
        log_conc = np.log(concentrations / standard_concentration)

        if np.isnan(pathway.standard_dg_primes).any():
            dg_adj = np.zeros(pathway.S.shape[1])
            for r in range(pathway.S.shape[1]):
                reactants = list(pathway.S[:, r].nonzero()[0].flat)
                dg_adj[r] = log_conc[reactants] @ pathway.S[reactants, r]
        else:
            dg_adj = pathway.S.T.values @ log_conc

        return pathway.standard_dg_primes + dg_adj

    @property
    def compound_plot(self) -> plt.Figure:
        """Plot compound concentrations.

        :return: matplotlib Figure
        """
        ureg.setup_matplotlib(True)

        data_df = self.compound_df.copy()

        data_df["y"] = np.arange(0, data_df.shape[0])
        data_df["color"] = "green"

        # a sub-DataFrame of only the metabolites with nonzero shadow prices
        data_df.loc[data_df.shadow_price != 0, "color"] = "red"

        # a sub-DataFrame of only the metabolites with fixed concentrations
        data_df.loc[
            data_df.lower_bound == data_df.upper_bound, "color"
        ] = "grey"

        compound_fig, ax = plt.subplots(1, 1, figsize=(9, 6))
        ax.xaxis.set_units(ureg.molar)
        ax.axvspan(Q_("1 nM"), self.bounds.default_lb, color="y", alpha=0.5)
        ax.axvspan(self.bounds.default_ub, Q_("10M"), color="y", alpha=0.5)

        ax.scatter(
            x=data_df.concentration.tolist(),
            y=data_df.y.tolist(),
            c=data_df.color.tolist(),
        )

        ax.set_ylabel("")
        ax.set_yticks(data_df.y)
        ax.set_yticklabels(data_df["compound"], fontsize=9)
        ax.set_xlabel("Concentration (M)")
        ax.set_xscale("log")
        ax.set_ylim(-1.5, data_df.shape[0] + 0.5)
        compound_fig.tight_layout()

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
        # Put a legend to the right of the current axis
        custom_lines = [
            Line2D([0], [0], color="green", lw=4),
            Line2D([0], [0], color="red", lw=4),
            Line2D([0], [0], color="grey", lw=4),
        ]
        ax.legend(
            custom_lines,
            [r"shadow price $=$ 0", r"shadow price $\ne$ 0", r"fixed value"],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=9,
        )

        return compound_fig

    @property
    def reaction_plot(self) -> plt.Figure:
        """Plot cumulative delta-G profiles.

        :return: matplotlib Figure
        """
        ureg.setup_matplotlib(True)

        cumulative_dgms = [Q_("0 kJ/mol")] + np.cumsum(
            self.reaction_df.physiological_dg_prime
        ).tolist()
        cumulative_dgs = [Q_("0 kJ/mol")] + np.cumsum(
            self.reaction_df.optimized_dg_prime
        ).tolist()

        # This is an ugly hack. For some reason, Pandas messes up the numpy
        # arrays with pint units, and they need to be rebuilt from scratch to
        # get the units right.
        cumulative_dgms = np.array(
            [float(x / Q_("kJ/mol")) for x in cumulative_dgms]
        ) * Q_("kJ/mol")
        cumulative_dgs = np.array(
            [float(x / Q_("kJ/mol")) for x in cumulative_dgs]
        ) * Q_("kJ/mol")

        xticks = 0.5 + np.arange(self.reaction_df.shape[0])
        xticklabels = self.reaction_df.reaction_id.tolist()

        reaction_fig, ax = plt.subplots(1, 1, figsize=(9, 6))
        ax.xaxis.set_units(Q_("kJ/mol"))
        ax.plot(
            cumulative_dgms,
            label="Physiological concentrations (1 mM)",
            color="blue",
        )
        ax.plot(
            cumulative_dgs, label="MDF-optimized concentrations", color="green"
        )
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels, rotation=45, ha="right")
        ax.grid(color="grey", linestyle="--", linewidth=1, alpha=0.2)

        ax.set_xlabel("Reaction Step")
        ax.set_ylabel(r"Cumulative $\Delta_r G^\prime$ (kJ/mol)")
        ax.legend(loc="best")
        ax.set_title(f"MDF = {self.mdf}")

        reaction_fig.tight_layout()
        return reaction_fig


class PathwayThermoModel(object):
    """Container for doing pathway-level thermodynamic analysis."""

    def __init__(self, pathway, stdev_factor: float = 1.0) -> object:
        """Create a model for running MDF analysis.

        :param pathway: a Pathway object defining the reactions and bounds
        :param stdev_factor: the factor with which we multiply the
        sqrt uncertainty matrix of the dG'0 estimates
        """
        self.pathway = pathway
        self.stdev_factor = stdev_factor
        self.Nc, self.Nr = pathway.S.shape

        # Make sure dG0_r' is the right size
        assert pathway.standard_dg_primes.shape == (
            self.Nr,
        ), "standard dG required for all reactions"
        assert pathway.dg_sigma.shape == (
            self.Nr,
            self.Nr,
        ), "uncertainty in dG required for all reactions"

        self.I_dir = np.diag(np.sign(self.pathway.fluxes))
        self.Nr_active = sum(self.pathway.fluxes.T != 0)

        # Currently unused bounds on reaction dGs.
        self.r_bounds = None

    def _MakeLnConcentratonBounds(
        self
    ) -> Tuple[Iterable[float], Iterable[float]]:
        """Make bounds on logarithmic concentrations.

        :return: A two-tuple (lower bounds, upper bounds).
        """
        return self.pathway.bounds.GetLnBounds(self.pathway.S.index)

    def _MakeDrivingForceConstraints(
        self
    ) -> Tuple[np.array, np.array, np.array]:
        """Generate parameters for LP.

        Generates the A matrix and b & c vectors that can be used in a
        standard form linear problem:
                max          c'x
                subject to   Ax <= b

        x is the vector of (y | log-conc | B)
        where y dG'0 are the reaction Gibbs energy variables, log-conc
        are the natural log of the concentrations of metabolites, and
        B is the max-min driving force variable which is being maximized
        by the LP
        :return: (A, b, c) - the parameters of the LP
        """
        inds = np.nonzero(np.diag(self.I_dir))[0].tolist()

        A11 = self.I_dir[inds] @ self.pathway.dg_sigma
        A12 = self.I_dir[inds] @ self.pathway.S.T
        A13 = np.ones((len(inds), 1))

        # covariance var ub and lb
        A21 = np.eye(self.Nr)
        A22 = np.zeros((self.Nr, self.Nc))
        A23 = np.zeros((self.Nr, 1))

        # log conc ub and lb
        A31 = np.zeros((self.Nc, self.Nr))
        A32 = np.eye(self.Nc)
        A33 = np.zeros((self.Nc, 1))

        # upper bound values
        b1 = -self.I_dir[inds] @ self.pathway.standard_dg_primes
        b2 = np.ones(self.Nr) * self.stdev_factor

        A = np.vstack(
            [
                np.hstack([A11, A12, A13]),  # driving force
                np.hstack([A21, A22, A23]),  # covariance var ub
                np.hstack([-A21, A22, A23]),  # covariance var lb
                np.hstack([A31, A32, A33]),  # log conc ub
                np.hstack([A31, -A32, A33]),
            ]
        )  # log conc lb

        b = np.hstack(
            [b1, b2, b2, self.pathway.ln_conc_ub, -self.pathway.ln_conc_lb]
        )

        c = np.zeros(A.shape[1])
        c[-1] = 1.0

        # change the constraints such that reaction that have an explicit
        # r_bound will not be constrained by B, but will be constrained by
        # their specific bounds. Note that we need to divide the bound
        # by R*T since the variables in the LP are not in kJ/mol but in units
        # of R*T.
        if self.r_bounds:
            for i, r_ub in enumerate(self.r_bounds):
                if r_ub is not None:
                    A[i, -1] = 0.0
                    b[i] += float(r_ub)

        return A, b, c

    def _GetPrimalVariablesAndConstants(
        self
    ) -> Tuple[np.array, np.array, np.array, List[Variable], List[Variable]]:

        # Create the driving force variable and add the relevant constraints
        A, b, c = self._MakeDrivingForceConstraints()

        # the dG'0 covariance eigenvariables
        y = [Variable("y%d" % i) for i in range(self.Nr)]

        # ln-concentration variables
        lnC = [Variable("l%d" % i) for i in range(self.Nc)]

        return A, b, c, y, lnC

    def _GetDualVariablesAndConstants(
        self
    ) -> Tuple[
        np.array,
        np.array,
        np.array,
        List[Variable],
        List[Variable],
        List[Variable],
        List[Variable],
    ]:
        # Create the driving force variable and add the relevant constraints
        A, b, c = self._MakeDrivingForceConstraints()

        w = [Variable("w%d" % i, lb=0) for i in range(self.Nr_active)]
        g = [Variable("g%d" % i, lb=0) for i in range(2 * self.Nr)]
        z = [Variable("z%d" % i, lb=0) for i in range(self.Nc)]
        u = [Variable("u%d" % i, lb=0) for i in range(self.Nc)]

        return A, b, c, w, g, z, u

    def _MakeMDFProblem(
        self
    ) -> Tuple[Model, List[Variable], List[Variable], Variable]:
        """Create primal LP problem for Min-max Thermodynamic Driving Force.

        Does not set the objective function... leaves that to the caller.

        :return: the linear problem object, and the three types of variables
        as arrays.
        """
        A, b, c, y, lnC = self._GetPrimalVariablesAndConstants()

        B = Variable("mdf")
        x = y + lnC + [B]
        lp = Model(name="MDF_PRIMAL")

        cnstr_names = (
            [f"driving_force_{j:02d}" for j in range(self.Nr_active)]
            + [f"covariance_var_ub_{j:02d}" for j in range(self.Nr)]
            + [f"covariance_var_lb_{j:02d}" for j in range(self.Nr)]
            + [f"log_conc_ub_{j:02d}" for j in range(self.Nc)]
            + [f"log_conc_lb_{j:02d}" for j in range(self.Nc)]
        )

        constraints = []
        for j in range(A.shape[0]):
            row = [A[j, i] * x[i] for i in range(A.shape[1])]
            constraints.append(
                Constraint(sum(row), ub=b[j], name=cnstr_names[j])
            )

        lp.add(constraints)

        row = [c[i] * x[i] for i in range(c.shape[0])]
        lp.objective = Objective(sum(row), direction="max")

        return lp, y, lnC, B

    def _MakeMDFProblemDual(
        self
    ) -> Tuple[
        Model, List[Variable], List[Variable], List[Variable], List[Variable]
    ]:
        """Create dual LP problem for Min-max Thermodynamic Driving Force.

        Does not set the objective function... leaves that to the caller.

        :return: the linear problem object, and the four types of variables
        as arrays.
        """
        A, b, c, w, g, z, u = self._GetDualVariablesAndConstants()
        x = w + g + z + u
        lp = Model(name="MDF_DUAL")

        cnstr_names = (
            ["y_%02d" % j for j in range(self.Nr)]
            + ["l_%02d" % j for j in range(self.Nc)]
            + ["MDF"]
        )

        constraints = []
        for i in range(A.shape[1]):
            row = [A[j, i] * x[j] for j in range(A.shape[0])]
            constraints.append(
                Constraint(sum(row), lb=c[i], ub=c[i], name=cnstr_names[i])
            )

        lp.add(constraints)

        row = [b[i] * x[i] for i in range(A.shape[0])]
        lp.objective = Objective(sum(row), direction="min")

        return lp, w, g, z, u

    def FindMDF(self) -> PathwayMDFData:
        """Find the MDF.

        :return: a PathwayMDFData object with the results of MDF analysis.
        """

        def get_primal_array(l):
            return np.array([v.primal for v in l], ndmin=1)

        lp_primal, y, lnC, B = self._MakeMDFProblem()

        if lp_primal.optimize() != "optimal":
            logging.warning("LP status %s", lp_primal.status)
            raise Exception("Cannot solve MDF primal optimization problem")

        y = get_primal_array(y)  # covariance eigenvalue prefactors
        lnC = get_primal_array(lnC)  # log concentrations
        B = lp_primal.variables["mdf"].primal

        lp_dual, w, g, z, u = self._MakeMDFProblemDual()
        if lp_dual.optimize() != "optimal":
            raise Exception("cannot solve MDF dual")

        primal_obj = lp_primal.objective.value
        dual_obj = lp_dual.objective.value
        if abs(primal_obj - dual_obj) > 1e-3:
            raise Exception(
                f"Primal != Dual ({primal_obj:.5f} != " f"{dual_obj:.5f}"
            )

        w = get_primal_array(w)
        z = get_primal_array(z)
        u = get_primal_array(u)
        reaction_prices = w
        compound_prices = z - u

        return PathwayMDFData(
            self.pathway,
            B,
            self.I_dir,
            lnC,
            y,
            reaction_prices,
            compound_prices,
        )
