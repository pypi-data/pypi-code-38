#===============================================================================
# sumstats.py
#===============================================================================

# Imports ======================================================================

import math
import scipy.stats




# Functions ====================================================================

def zsq_from_pval(pval):
    """Convert a p-value to a squared z-score

    Parameters
    ----------
    pval
        a p-value
    
    Returns
    -------
    float
        a squared z-score
    """

    return scipy.stats.norm.ppf(1 / 2 * pval) ** 2


def approx_lnbf(
    beta=None,
    se_beta=None,
    pval=None,
    freq=None,
    sample_size=None,
    cases=None,
    controls=None,
    prior_variance=None
):
    """Compute an approximate bayes factor from other summary statistics.
    Preferentially uses beta/se approximation.

    Parameters
    ----------
    beta
        effect size from an association test
    se_beta
        standard error from an association test
    pval
        p-value from an association test
    sample_size
        sample size for an association test (quantitative trait)
    cases
        number of cases for an association test (case-control)
    controls
        number of controls for an association test (case-control)
    prior_variance
        set the prior variance for bayes factor computation
    
    Returns
    -------
    float
        a (natural) log bayes factor
    """
    
    prior_variance = (
        (0.0225 if (beta and not se_beta) else 0.04)
        if not prior_variance else prior_variance
    )
    if (beta is not None) and se_beta:
        estimated_variance = se_beta ** 2
        z_squared = (beta / se_beta) ** 2
    else:   
        if cases and controls and freq:
            estimated_variance = 1 / (
                2
                * (cases + controls)
                * freq
                * (1 - freq)
                * (cases / controls)
                * (1 - cases / controls)
            )
        elif sample_size and freq:
            estimated_variance = 1 / (2 * sample_size * freq * (1 - freq))
        else:
            raise BadArgumentError(
                'Please provide beta and se_beta, sample_size and freq, or '
                'cases, controls and freq'
            )
        if beta:
            z_squared = (beta ** 2) / estimated_variance
        elif pval:
            z_squared = zsq_from_pval(pval)
        else:
            raise BadArgumentError(
                'Please provide beta and se_beta or pval, maf, and sample_size'
            )
    shrinkage_factor = prior_variance / (estimated_variance + prior_variance)
    lnbf = (
        1 / 2 * (math.log(1 - shrinkage_factor) + z_squared * shrinkage_factor)
    )
    return lnbf


def log_sum(lnbfs, weights=None):
    """Sum of a sequence of bayes factors in logarithmic space
    
    Parameters
    ----------
    lnbfs
        sequence of (natural) log bayes factors
    weights
        sequence of weights for `lnbfs`
    
    Returns
    -------
    float
        the logarithm of the sum of the bayes factors
    """
    
    lnbfs = tuple(lnbfs)
    if not weights:
        weights = (1,) * len(lnbfs)
    max_lnbf = max(lnbfs)
    try:
        return (
            max_lnbf + math.log(
                math.fsum(
                   math.exp(lnbf - max_lnbf) * weight
                   for lnbf, weight in zip(lnbfs, weights)
                )
            )
        )
    except ValueError:
        if len(lnbfs) == 2:
            return min(lnbfs)
        else:
            raise RuntimeError(
                'The sum of absolute bayes factors may have been rounded to '
                'zero due to a pathalogically high maximum'
            )




# Errors =======================================================================

class Error(Exception):
   """Base class for other exceptions"""
   pass


class BadArgumentError(Error):
    """Bad argument error"""
    pass
