#!/usr/bin/env python
# encoding: utf-8

"""
Custom filter for Bopytex
"""

__all__ = ["do_calculus"]

def do_calculus(steps, name="A", sep="=", end="", joining=" \\\\ \n"):
    """Display properly the calculus

    Generate this form string:
    "name & sep & a_step end joining"

    :param steps: list of steps
    :returns: latex string ready to be endbeded


    """

    ans = joining.join([
        name + " & "
        + sep + " & "
        + str(s) + end for s in steps
        ])
    return ans


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
