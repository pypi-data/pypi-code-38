from numpy import  matrix 

"""
Some statistics functions
"""

def matrix_VCV(Vxx,Vyy,Vzz,Vxy,Vxz,Vyz):
    a=[Vxx,Vxy,Vxz]
    b=[Vxy,Vyy,Vyz]
    c=[Vxz,Vyz,Vzz]
    VCV=matrix([a,b,c])
    return VCV

def rotate(R,VCV):
    return R.dot(VCV.dot(R.transpose()))
