import cProfile

#import custommgf as mgf
from pyteomics import mgf

cProfile.run('''
with mgf.read('/home/lev/swedcad.mgf', skip_charges=True) as f:
    for s in f:
        pass
    ''', 'mgf_profile.out')