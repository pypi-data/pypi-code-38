import pytest 
from nuphy import main
import nuphy.nubase as nubase
from nuphy.nubase import isotope

def test_1():    
    assert main.mainfunc()==True



    
def test_2():
    assert nubase.unitfunc()==True
    nubase.DEBUG=True
    n14=isotope( 14,7 )
    n15=isotope( 15,'N' )
    o18=isotope( 'o18' )
    print("----------------------------------- AMU:")
    print("I... name, AMU n14:", n14.name, n14.amu )
    print("I... name AMU n15:", n15.name, n15.amu )
    
    print( 'n14 half, spin, parity IS  ', n14.halflife , n14.spin , n14.parity , n14.IS )
    print( 'n15 half, spin, parity IS  ', n15.halflife , n15.spin , n15.parity , n15.IS )
    print( 'o18 half, spin, parity IS   ', o18.halflife , o18.spin , o18.parity , o18.IS )
    #print( 'i... o15 halfl/spin/parity/mex/abund', o15.halflife , o15.spin , o15.parity , o15.mex, o15.IS)
#for a in range(260):
#        for z in range(200):
#                he3=isotope(a,z)
        ###print( he3.mex   )
        ###print( he3.mex, he3.dmex, he3.halflife )
        ###if (he3.name):print( he3.name, he3.mex, he3.dmex, he3.halflife, he3.IS , he3.A, he3.Z, he3.N , he3.spinfull, he3.spin, '*')
#                if (he3.name):print( he3.name, he3.spinfull, he3.spin, he3.parity, '*')
        ###print( he3.mex, he3.dmex, he3.halflife, he3.IS()  )
    print("----------------------------------------------- end")
    assert n14.spin==1
    assert n15.spin==0.5
    assert o18.spin==0
    assert nubase.elements[0]=='n'
    assert nubase.densities[5]==2.34
    assert nubase.molarweights[1]==1.0079
