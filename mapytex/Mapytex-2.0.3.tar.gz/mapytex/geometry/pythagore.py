#!/usr/bin/env python
# encoding: utf-8


from random import randint


def random_pythagore(v_min = 1, v_max = 10, nbr_format = lambda x : x) :
    """ Generate a pythagore triplet
    :returns: (a,b,c) such that a^2 = b^2 + c^2

    """
    u, v = randint(v_min, v_max), randint(v_min, v_max)
    while u == v:
        u, v = randint(v_min, v_max), randint(v_min, v_max)
    u, v = max(u, v), min(u, v)
    triplet = (u**2+v**2, 2*u*v, u**2-v**2)
    formated_triplet = [nbr_format(i) for i in triplet]
    return formated_triplet

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
