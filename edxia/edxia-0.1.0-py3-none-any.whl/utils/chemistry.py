# Copyright (c) 2019 Fabien Georget <fabien.georget@epfl.ch>, EPFL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np

# some molar masses (kg/mol)
molar_masses = {
        "H": 1.0079,
        "Ca": 40.078,
        "Si": 28.0855,
        "Al": 26.9815,
        "S": 32.067,
        "Fe": 55.8473,
        "Mg": 24.305,
        "Na": 22.989769,
        "K": 39.0983,
        "Ti": 47.867,
        "O":  15.9994,
        "P": 30.9738,
        "Mn": 54.938,
        "Zn": 65.392,
        "Cl": 35.4528
        }

oxides = {
    "Ca": "CaO",
    "Si": "SiO2",
    "Al": "Al2O3",
    "S": "SO3",
    "Fe": "Fe2O3",
    "Mg": "MgO",
    "Na": "Na2O",
    "K": "K2O",
    "Ti": "TiO2",
    "P": "P2O5",
    "Mn": "MnO2",
    "Zn": "ZnO"
}

def find_number(formula, current_ind):
    """Returns the stoichiometry of an element from a formula

    :param formula: a string of the formula
    :param current_ind: the current parsing index
    :returns: a tuple: new parsing index, stoichiometry coefficient
    """
    k = current_ind;
    while (k<len(formula)) and (formula[k].isdigit() or formula[k]=="."):
        k += 1
    if k>len(formula):
        stoech = 1
    else:
        if formula[current_ind:k]:
            stoech = float(formula[current_ind:k])
        else:
            stoech=1
    return (k,stoech)

def formula_to_composition(formula):
    """Returns the composition from a chemical formula

    :param formula: a string containing a chemical formula
    :returns: a dict where keys are elements and values their stoichiometries
    """
    comp = {}
    ind = 0
    while ind<len(formula):
        # subformula
        if formula[ind] == "(":
            k=ind+1;
            while k<len(formula):
                if formula[k] == ")":
                    k+=1
                    break
                k += 1
            if k > len(formula):
                raise RuntimeError("missing )")
            subformula = formula[ind+1:k-1]
            ind, stoech = find_number(formula,k)
            to_add = formula_to_composition(subformula);
            for (key, value) in to_add.items():
                if key in comp:
                    comp[key] += stoech*value
                else:
                    comp[key] = stoech*value;
        #
        else:
            k=ind+1
            while (k<len(formula)) \
                    and (not formula[k].isdigit()) \
                    and (not formula[k].isupper()) \
                    and (not formula[k] == "("):
                k += 1
            element = formula[ind:k]
            ind, stoech=find_number(formula,k)
            if element in comp:
                comp[element] += stoech
            else:
                comp[element] = stoech;
    return comp

# fill the molar masses
new_oxides = {}
for elem, oxide in oxides.items():
    comp = formula_to_composition(oxide)
    molar_masses[oxide] = sum([val*molar_masses[elem] for elem, val in comp.items()])
    new_oxides[elem] = (oxide, comp[elem])
oxides = new_oxides


def normalize_composition(comp):
    """Normalize stoichiometry so the sum of the coefficients is one."""
    tsum = sum(comp.values())
    for key, value in comp.items():
        comp[key] = value/tsum


def mass_of_oxide_from_composition(comp):
    """Compute the mass of oxide from atomic composition."""
    mass_oxide = 0
    for (elem, val) in comp.items():
        if elem != "O":
            mass_oxide += val*molar_masses[oxides[elem][0]]
    return mass_oxide

def mass_of_oxide_from_mass_composition(comp):
    """Compute the mass of oxide from mass composition."""
    mass_oxide = 0
    for (elem, val) in comp.items():
        if elem in oxides.keys():
            mass_oxide += val*molar_masses[oxides[elem][0]]/(oxides[elem][1]*molar_masses[elem])
    return mass_oxide

def relative_mass_of_oxide_from_mass_composition(comp):
    """Compute the relative mass of oxide from mass composition."""
    return mass_of_oxide_from_mass_composition(comp)/sum(comp.values())