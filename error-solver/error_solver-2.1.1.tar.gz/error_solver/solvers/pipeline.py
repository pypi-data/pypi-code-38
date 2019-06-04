"""
Copyright (c) 2019, Matt Pewsey
"""

import pandas as pd

__all__ = ['SolverPipeline']


class SolverPipeline(object):
    """
    A class for performing propagation error analysis for multiple
    :class:`.ErrorSolver` or :class:`.ErrorSolverPy` solvers in series.

    Parameters
    ----------
    solvers : list
        A list of :class:`.ErrorSolver` of :class:`.ErrorSolverPy` to be solved
        in sequence.
    links : list
        A list of dictionaries with error variables to be passed from one
        solver to the next.
    combos : list
        A list of equation combinations to use for each solver. If None,
        all equations will be applied.

    Examples
    --------
    .. literalinclude:: ../../examples/pipeline_ex1.py
    """
    def __init__(self, solvers, links, combos=None):
        self.solvers = solvers
        self.links = links
        self.combos = combos

    def solve(self, values, errors, consts=None, check=True, stdev=False):
        """
        Solves for the propagation errors of the pipeline and returns a
        Data Frame of the results.

        Parameters
        ----------
        values : list
            A list of dictionaries of variable values to be applied to each
            solver.
        errors : list
            A list of dictionaries of variable errors to be applied to each
            solver.
        check : bool
            If True, checks will be performed prior to performing each solver
            analysis.
        stdev : bool
            If True, error values input are for standard deviations. Otherwise,
            the values represent error tolerances or variances.
        """
        results = []

        for i, solver in enumerate(self.solvers):
            const = {} if consts is None else const[i]
            combo = None if self.combos is None else self.combos[i]

            if i == 0:
                err = errors[i]
            else:
                err = errors[i].copy()
                df = results[-1]['error']

                for k, x in self.links[i-1].items():
                    err[x] = df[k]

            df = solver.solve(
                values=values[i],
                errors=err,
                const=const,
                combo=combo,
                check=check,
                stdev=stdev
            )

            df['solver'] = [i+1] * df.shape[0]
            results.append(df)

        results = pd.concat(results)

        return results
