"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""

import numpy as np
from scipy import stats as st


class ConfidenceInterval:

    @staticmethod
    def proportion_ci_wilson_2(p_hat, n, conf_level=0.95):
        alpha = 1 - conf_level
        z = st.norm.ppf(1 - alpha / 2)
        t = np.power(z, 2) / n

        p_tilde = (p_hat + t / 2.) / (1 + t)
        see = np.sqrt((p_hat * (1 - p_hat) / n) + (t / (4. * n))) / (1 + t)
        # see = np.sqrt((p_hat * (1 - p_hat) / n))

        ci_l = p_tilde - z * see
        ci_u = p_tilde + z * see
        return p_tilde, ci_l, ci_u

    @staticmethod
    def proportion_ci_wilson(nx, n, conf_level=0.95):
        alpha = 1 - conf_level
        nx = float(nx)
        n = float(n)
        # if n == 0 or nx == 0:
        if n == 0:
            return np.nan, np.nan, np.nan
        p_hat = nx / n

        z = st.norm.ppf(1 - alpha / 2)
        t = np.power(z, 2) / n

        p_tilde = (p_hat + t / 2.) / (1 + t)
        see = np.sqrt((p_hat * (1 - p_hat) / n) + (t / (4. * n))) / (1 + t)
        # see = np.sqrt((p_hat * (1 - p_hat) / n))

        ci_l = p_tilde - z * see
        ci_u = p_tilde + z * see
        return p_tilde, ci_l, ci_u

    @staticmethod
    def calculate_ci(row):
        nx = row['X>x,Y<=y']
        n = row['X>x']
        (p, l, u) = ConfidenceInterval.proportion_ci_wilson(nx, n)
        row['p_tilde'] = p
        row['ci'] = '%.02f (%.02f, %.02f)' % (round(p * 100, 2), round(l * 100, 2), round(u * 100, 2))
        return row