from __future__ import (absolute_import, division, print_function, unicode_literals)

import string


def get_data(length, nbr):
    step = 1
    alpha = list(string.ascii_letters[:length])
    numeric = [i for i in range(1, length + 1)]
    subalpha = []
    for x in alpha:
        subalpha.append([x + str(i) for i in range(1, nbr + 1)])
    subnumeric = []
    for _ in alpha:
        subnumeric.append([i for i in range(step, step + nbr + 1)])
        step += nbr + 1
    alpha_dict = []
    for x in alpha:
        alpha_dict.append({x + str(i): str(i) for i in range(1, nbr + 1)})
    return alpha, numeric, subalpha, alpha_dict, subnumeric


class Sample(object):
    @classmethod
    def dict(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return dict(zip(alpha, numeric))

    @classmethod
    def list(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return alpha[:int(length / 2)] + numeric[:(length - int(length / 2))]

    @classmethod
    def list_of_alpha(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return alpha

    @classmethod
    def list_of_digits(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return numeric

    @classmethod
    def list_of_dicts(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return alpha_dict

    @classmethod
    def dict_of_lists(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return dict(zip(alpha, subalpha))

    @classmethod
    def dict_of_ints(cls, length=6, nbr=4):
        alpha, numeric, subalpha, alpha_dict, subnumeric = get_data(length, nbr=nbr)
        return dict(zip(alpha, subnumeric))
