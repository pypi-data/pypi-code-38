#!/usr/bin/env python

__contributor__ = "Tianshu Li, Xingang Zhao"
__revised_date__= "2017.05.01"
#==============================================================================
# choice the HubbardU from reported values by Ladan Stevanovic and Stephan Lany
#==============================================================================

default_hubbardU={\
'Ni': [3, 0, 2], \
'La': [3, 0, 2], \
'Nb': [3, 0, 2], \
'Sc': [3, 0, 2], \
'Ti': [3, 0, 2], \
'Rh': [3, 0, 2], \
'Ta': [3, 0, 2], \
'Fe': [3, 0, 2], \
'Hf': [3, 0, 2], \
'Mo': [3, 0, 2], \
'Mn': [3, 0, 2], \
'W': [3, 0, 2], \
'V': [3, 0, 2], \
'Y': [3, 0, 2], \
'Zn': [6, 0, 2], \
'Co': [3, 0, 2], \
'Ag': [5, 0, 2], \
'Ir': [3, 0, 2], \
'Cd': [5, 0, 2], \
'Zr': [3, 0, 2], \
'Cr': [3, 0, 2], \
'Cu': [5, 0, 2]}

def default_plusU(elements):
    """
       method:: first-principle calculation with LDA plus U.
                the choice of u value is based on Vladan 
                Stevanovic and Stephan Lany(2012)
    """
    U = []
    J = []
    types = []
    bubbardu = {}
    plusU = default_hubbardU
   
    for e in elements:
        if e in plusU:
            U.append(plusU[e][0])
            J.append(plusU[e][1])
            types.append(orbitalU.index(plusU[e][2]))
        else:
            U.append(0)
            J.append(0)
            types.append(2)
            
    hubbardu['ldauu'] = ' '.join(U)
    hubbardu['ldauj'] = ' '.join(J)
    hubbardu['ldautype'] = ' '.join(types)

    return hubbardu
