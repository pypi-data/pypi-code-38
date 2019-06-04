import numpy as np
import pandas as pd

__all__ = ['_BaseErrorSolver']


class _BaseErrorSolver(object):
    def get_equations(self, combo=None):
        """
        Returns a list of equations for the specified combination.
        If `combo` is None, a list of all equations will be returned.

        Parameters
        ----------
        combo : str
            The name of the equation combination to be applied.
        """
        if combo is None:
            return self._equations
        else:
            return [self._equations[i] for i in self.combos[combo]]

    def get_partials(self, combo=None):
        """
        Returns a list of partial derivatives for the specified combination.
        If `combo` is None, a list of all partial derivatives will be returned.

        Parameters
        ----------
        combo : str
            The name of the equation combination to be applied.
        """
        if combo is None:
            return self._partials
        else:
            return [self._partials[i] for i in self.combos[combo]]

    def used_vars(self, values, errors, combo=None):
        """
        Returns a lists of (1) variables present in both the equations and
        input values dictionary and (2) variables present in both the equations
        and input errors dictionary.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        combo : str
            The name of the equation combination to be applied.
        """
        var = self.equation_vars(combo)
        err = var.intersection(errors)
        val = var.intersection(values) - err
        return sorted(val), sorted(err)

    def _check_determinancy(self, values, errors, combo):
        """
        Checks that the system of equations is determinant, i.e. that the
        number of unknown errors equals the number of equations.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        combo : str
            The name of the equation combination to be applied.
        """
        val, err = self.used_vars(values, errors, combo)
        n, m = len(val), len(self.get_equations(combo))

        if n != m:
            if m > n:
                s = '>'
                t = 'remove'
                v = err
            else:
                s = '<'
                t = 'add'
                v = val

            a = abs(n - m)

            raise ValueError('Indeterminant system:: Number of equations ({}) '
                '{} number of unknowns ({}). To correct, {} ({}) errors in {} '
                'or adjust the input equations.'.format(m, s, n, t, a, v))

    def solve(self, values, errors, const={}, combo=None, check=True, stdev=False):
        """
        Solves for the propagation errors of the system of equations and
        returns a Data Frame of the results.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        const : dict
            A dictionary mapping variable names to constant errors.
        combo : str
            The name of the equation combination to be applied.
        check : bool
            If True, value and other analysis checks will be performed
            prior to calculating the solution.
        stdev : bool
            If True, error values input are for standard deviations. Otherwise,
            the values represent error tolerances or variances.
        """
        if check:
            self.check(values, errors, combo)

        val, err = self.used_vars(values, errors, combo)
        n, m = len(val), len(err)

        xk = np.array([errors[k] for k in err], dtype='float').reshape(-1, 1)
        jac = self.jacobian(values, errors, combo)
        ju, jk = jac[:,:n], jac[:,n:n+m]
        jui = np.abs(np.linalg.inv(ju))
        ju, jk = np.abs(ju), np.abs(jk)

        if const:
            ck = np.array([const.get(k, 0) for k in err], dtype='float').reshape(-1, 1)
            cu = np.array([const.get(k, 0) for k in val], dtype='float').reshape(-1, 1)

            if stdev:
                xk **= 2
                ck **= 2
                cu **= 2
                xk += ck
            else:
                xk = np.abs(xk)
                ck = np.abs(ck)
                cu = np.abs(cu)
                xk += ck

            xu = jui.dot(jk.dot(xk) + ju.dot(cu))
            del jac, jui, ju, jk, cu, ck

        else:
            if stdev:
                xk **= 2
            else:
                xk = np.abs(xk)

            xu = jui.dot(jk.dot(xk))
            del jac, jui, ju, jk

        if stdev:
            xu **= 0.5
            xk **= 0.5

        xu = xu.ravel()
        xk = xk.ravel()

        # Create data frame of results
        df = pd.DataFrame()
        df['var'] = val + err
        df['value'] = [values[k] for k in df['var']]
        df['error'] = np.concatenate([xu, xk])
        df['pct_error'] = 100 * abs(df['error'] / df['value'])
        df['is_calc'] = np.concatenate([np.ones(n), np.zeros(m)]).astype('bool')

        df.sort_values('var', inplace=True)
        df.replace(float('inf'), np.nan, inplace=True)
        df.set_index('var', inplace=True)

        return df
