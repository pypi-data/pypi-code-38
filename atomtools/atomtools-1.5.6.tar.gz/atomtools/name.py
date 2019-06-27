"""
atomtools.name
"""


import random

def randString(num=10):
    string = 'zyxwvutsrqponmlkjihgfedcba'+\
             'zyxwvutsrqponmlkjihgfedcba'.upper()+\
             '0123456789'
    ran_str = ''.join(random.sample(string, num))
    return ran_str


def get_atoms_name(atoms, rand_length=10):
    return '{0}_{1}'.format(atoms.get_chemical_formula(),
                            randString(rand_length))




