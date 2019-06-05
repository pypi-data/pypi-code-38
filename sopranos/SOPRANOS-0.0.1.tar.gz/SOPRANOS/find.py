"""*******************************************************
This code converts redshift to distance
******************************************************"""


import numpy as np
import pdb

def fun_binsearch(Fun,Y,Range,Tol=None):
    """Description: Given a monotonic function, Y=Fun(X), and Y, search for Fun^{-1}(Y), i.e. X that satisfy Y=F(X).
    The search is done using a binary search between the values stated at X range.
 Input  : - Function [i.e., Y=Fun(X)].
          - Y value to search
          - X range [min max] in which to search for a solution.
          - Relative tolerance, default is 1e-3.
          - Additional optional parameters of Fun
 Output : - X value corresponds to the input Y value.
     By : translated from Eran O. Ofek                    Feb 2005
    URL : http://weizmann.ac.il/home/eofek/matlab/
 Example: f=lambda x:x+1
          Mid=find.fun_binsearch(f,3,[0,10],Tol=1e-6)"""
    if Tol is None:
        Tol=1e-3
    #print('Range is',Range)
    Mid=np.mean(Range)
    Y1=Fun(Range[0])
    Y2=Fun(Range[1])
    Ym=Fun(Mid)
    #print('Y1 is',Y1)
    #print('Y2 is',Y2)
    #print('Ym is ',Ym)

    if Y2>Y1:
        type='a'#ascending
    else:
        type='d'#descending or constant

    while Range[1]-Range[0]>Mid*Tol:
        if type=='a':
            if Y>Ym:
                Range=[Mid,Range[1]]
            else:
                Range=[Range[0],Mid]
        elif type=='d':
            if Y>Ym:
                Range=[Range[0],Mid]
            else:
                Range = [Mid, Range[1]]
        else:
            print('problem')
            pdb.set_trace()
        Mid=np.mean(Range)
        Y1=Fun(Range[0])
        Y2=Fun(Range[1])
        Ym=Fun(Mid)
    return Mid















