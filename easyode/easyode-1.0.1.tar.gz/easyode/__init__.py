
import numpy as np 
import scipy.integrate as inte
import matplotlib.pyplot as plt 




class Diffcoef() :
    '''Class used to create an EquaDiff object'''

    def __init__(self,norm,derivdeg) :
        '''
        Arg :
        -norm : float | Algebric norm of the coefficient
        -derivdeg : int | Derivation degree of the parameter wich the coefficient is proportional to.
            Example - Newton 2nd law : 
                mass*acceleration -> norm = -mass | derivdeg = 2 

        -------------------------------------------------------------------------------------------------
        derivdeg info :
            constant : -1
            x : 0
            dx/dt : 1
            ...

        '''


        self.Norm = norm
        self.Deg = derivdeg
        


class EquaDiff() :
    

    def __init__(self,List_of_Diffcoef,initial=None) :
        '''
        Arg :
            -List_of_Diffcoef : List of DiffCoef | List of the coefficient of the ODE
            -initial : List of float | Intial condition of the equation. Not '''
        self.Coefs = list(List_of_Diffcoef)
        self.InitialCond = initial

    def GetDeg(self) :
        '''Return the maximal derivation degree of the equation'''
        Max = -1
        for coef in self.Coefs :
            if coef.Deg > Max :
                Max = coef.Deg
        return Max

    def AddCoef(self,coef) :
        '''Used to add a new DiffCoef to the equation
        Arg :
            -coef : DiffCoef |
            '''

        self.Coefs.append(coef)
        return None

    def DerivFunc(self) :
        '''Return the function wich is used to calculate the derivate of the parameter
        This function can be used in odeint'''

        d = self.GetDeg()+1

        LF = [0 for k in range(d+1)]

        for coef in self.Coefs :
            LF[int(coef.Deg+1)] += coef.Norm

        a = np.array([[0 for k in range(1,d)] for j in range(1,d)], float)
        b = np.array([0 for k in range(1,d)], float)
        b[d-2] = LF[0]
        for k in range(1,d-1) :
            a[k-1][k] = 1
        for k in range(1,d) :
            a[d-2][k-1] = LF[k]/(-LF[d])
            

        B = b
        A = np.mat(a)


        def f(x,t0) :
            X = np.array(x)
            X = np.reshape(X,(len(x),1))
            H = np.reshape(B, (len(x),1))
            Xp = np.ravel(np.dot(A,X)+ H)
            
            
            return Xp
            
        return f

    def AddInitialCond(self,initial) :
        ''' Used to add initial condition to the ODE
        Arg :
            -initial : List of float | initial condition of the function. The len of the list has to be equal to self.GetDeg()'''

        d = self.GetDeg()
        if not len(initial) == d :
            print("Error : List of ",d," elements was expected")
            return None
        
        self.InitialCond = initial
        
        return None

    def Graph(self,T,Derivation_degree) :
        '''Used to plot graph using pyplot and odeint
        Arg :
            -T : array numpy | parameter interval where the function has to be calculated
            -Derivation_degree : List of int | derivation degree that you want to plot

        '''
        f = self.DerivFunc()
        X0 = self.InitialCond
        X = inte.odeint(f,X0,T)
        for k in Derivation_degree :

            plt.plot(T,X[:,k],label='x'+"'"*k)

        plt.grid()
        plt.legend()
        plt.show()
       

def NewEquaDiff() :
    return Equadiff([Diffcoef(0,0)])




    

