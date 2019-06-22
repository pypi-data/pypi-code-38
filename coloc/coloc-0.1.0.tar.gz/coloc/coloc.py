#!/usr/bin/env python3
#===============================================================================
# coloc.py
#===============================================================================

# Imports ======================================================================

import math
import sumstats




# Functions ====================================================================

def coloc(
    trait1_lnbfs,
    trait2_lnbfs,
    prior1: float = 1e-4,
    prior2: float = 1e-4,
    prior12: float = 1e-5
):
    """Perform a Bayesian colocalization test

    Parameters
    ----------
    trait1_lnbfs
        sequence of log Bayes factors for the first trait
    trait2_lnbfs
        sequence of log Bayes factors for the second trait
    prior1
        first prior parameter for the colocalization model [1e-4]
    prior2
        second prior parameter for the colocalization model [1e-4]
    prior12=1e-5
        third prior parameter for the colocalization model [1e-5]
    
    Returns
    -------
    generator
        posterior probabilities for the five colocalization objects
    """

    log_numerators = (
        0,
        math.log(prior1) + sumstats.log_sum(trait1_lnbfs),
        math.log(prior2) + sumstats.log_sum(trait2_lnbfs),
        math.log(prior1) + math.log(prior2) + sumstats.log_sum(
            trait1_lnbf + trait2_lnbf
            for i, trait1_lnbf in enumerate(trait1_lnbfs)
            for j, trait2_lnbf in enumerate(trait2_lnbfs)
            if i != j
        ),
        math.log(prior12) + sumstats.log_sum(
            trait1_lnbf + trait2_lnbf
            for trait1_lnbf, trait2_lnbf in zip(trait1_lnbfs, trait2_lnbfs)
        )
    )
    return (
        math.exp(log_numerator - sumstats.log_sum(log_numerators))
        for log_numerator in log_numerators
    )


def ascii_bar(prob: float):
    """Draw an ascii bar to display a probability

    Parameters
    ----------
    prob
        the probability value to display
    
    Returns
    -------
    string
        the ascii bar
    """
    level = int(prob * 20)
    return '[{}{}]'.format('|' * int(level), ' ' * (20-level))


def print_coloc_result(
    title: str,
    pp0: float,
    pp1: float,
    pp2: float,
    pp3: float,
    pp4: float
):
    """Print an ascii representation of the colocalization test result

    Parameters
    ----------
    title
        a title for the ascii art
    pp0
        the posterior probability of H0: no association
    pp1
        the posterior probability of H1: association in trait 1 only
    pp2
        the posterior probability of H2: association in trait 2 only
    pp3
        the posterior probability of H3: independent associations
    pp4
        the posterior probability of H4: colocalized associations
    """
    
    print(
        '\n'.join(
            ('', title, '') + tuple(
                'PP{}: {} [ {} ]'.format(i, ascii_bar(pp), pp)
                for i, pp in enumerate((pp0, pp1, pp2, pp3, pp4))
            )
            + ('',)
        )
    )
