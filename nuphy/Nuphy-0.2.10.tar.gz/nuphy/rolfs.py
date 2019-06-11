#!/usr/bin/env python3
from math import pow, sqrt, exp

# used only in other expressions   #  r in [cm]
def CoulombPotential(Z1,Z2,r):
    '''
    Z1 Z2/r  ...  units  keV cm
    '''
    e2=1.44e-10;  #keV cm
    return 1.0/r *Z1 * Z2 *e2;


# used in   CoulAZ / CoulombBarrier //  r0 in [cm]
def NuclearDistance(A1,Z1,A2,Z2, r0=1.3e-13):
    '''
    sum of the two nuclear radii by A^1/3
    ...  units -  cm  if r0=1.3e-13 cm
    '''
    return r0*pow(A1,0.3333) + r0*pow(A2,0.3333)


# Barrier in keV        r in [cm]
def CoulombBarrier(A1,Z1,A2,Z2, r0=1.3e-13):
    '''
    Coulomb potential at a closest distance of two nuclei
    ... units  keV cm
    '''
    e2=1.44e-10;  #//keV cm
    #//  double k= 8.617343E-11; //MeV
    k= 8.617343E-8; # //keV
    #//  double r=pow(A1,0.3333)*r0 + pow(A2,0.3333)*r0 ;
    r=NuclearDistance(A1,Z1,A2,Z2, r0)
    #EC=1.0/r *Z1 * Z2 *e2
    EC=CoulombPotential(Z1,Z2,r)
    T=EC/k  # QUESTION: k or k 2/3 3/2 or so?
    #print('   {:.4g} keV,   {:.3f} T6'.format(EC, T/1e+6,'K' ) )
    return EC #; //in keV



def Sommerfield(A1,Z1,A2,Z2,Ecmskev):
    '''
    Sommerfield factor e^(-2 pi nu), depends on Z1Z2, Ecm and reduced mass
    just A1A2 here, not with mass excess
    ... units  Ecm in keV
    '''
    amu=A1*A2/(A1+A2)
    e2=1.44e-10   #  //keV cm//
    hbar=6.5821195e-16  #;   //  eV s
    hbarkev=hbar/1000.  #;   //  keV s
    #   double nu=Z1 * Z2* e2 /hbarkev/ v ;
    twopinu= 31.29 * Z1 * Z2  * sqrt(amu/Ecmskev);
    # approximation at low energies, where E<< Ec
    P=exp(-1.0 * twopinu);
    print( '   2Pinu={}  P={:.4g} '.format(twopinu, P )  );
    return P


def GamowEnergy(A1,Z1,A2,Z2,T6,Skevb):
    '''
     effective mean energy
    ... temperature in T6
    ... rate is calculated based on S in keVb 
    '''
    #  T6 is temperature in T6 Kelvins
    #  AMU =   A1 * A2 / ( A1 + A2 )
    amu=A1*A2/(A1+A2)
    k= 8.617343E-8  #; //keV
    Eg=0.989*Z1*Z2*pow(amu,0.5)
    Eg=Eg*Eg # b^2  (4.18)
    #print(Eg)  # Gamow energy - exponential term b/E^1/2
    # (4.21) effective mean energy
    E0=1.22*pow( amu*T6*T6*Z1*Z1*Z2*Z2 ,0.3333)
    #  dimensionless tau:
    # Imax= exp(-tau)  .....  max value of the integrand
    # reactions with smallest CoulBar = highest Imax will be most rapid
    tau=42.46* pow( Z1*Z1*Z2*Z2*amu/T6, 0.33333)   # (4.23)
    Imax=exp(-1.0*tau)
    # gamow peak can be approximated by gaussian: sigma = delta (4.25)
    delta=0.749*pow( Z1*Z1*Z2*Z2*amu*pow(T6,5.0),0.33333/2.)
    # delta * Imax ~ approx value of the integral
    #
    #  consider gaussian shape of gamow; <sigma v> with tau from (4.23)
    # gives the rate when S(E0) is given keVb:  rate per particle pair
    rate=7.20e-19 /amu/Z1/Z2*tau*tau *exp(-1.0*tau)*Skevb
    #
    #  reaction rate can have a correction F(tau) Rolfs (4.31)
    #     it is like 3% for p+p or less
    print(" kT={:5.3g} keV, E0={:6.3g} keV  delta/2={:6.3g} keV  Imax={:7.3g}   rate={:.3g} cm3/s".format(	k*T6*1e+6 ,E0, delta/2., Imax,  rate )   );
    # E0 is efffective mean energy for thermonucl reactions
    return E0


if __name__ == "__main__":
    print( 'Coulomb Potential Z1Z2/r at 1.2 fm:',CoulombPotential(1,  2, 1.2e-13)  )
    ND=NuclearDistance(1,1, 2,1)
    print( 'Nuclear Distance p+d {:.3g}cm ={:.3g}fm'.format( ND,ND/1e-13)  )

    print( 'p+d Coulomb Barrier            {:.5g} keV'.format( CoulombBarrier(1,1, 2,1 ) ) )
    print( 'p+d Sommerfield @66keV<<500keV {:.3g}'.format(  Sommerfield(1,1,  2,1,  66  ) ) )

    print("    examples Rolfs, eq (4.21E0) and (4.23Imax) and eq (4.26DImax) ad (4.27 rate)")

    GamowEnergy( 1,1,  1,1,   15. ,  550 ) 
    GamowEnergy( 1,1,  14,7,  15.,  0 )  
    GamowEnergy( 4,2,  12,6,  15.,  0 )  
    GamowEnergy( 16,8, 16,8,  15,   0 )  

    #print()
    print(' pd  dd dt  dhe3  he3he3  pb11')
    GamowEnergy( 1,1,  2,1,   765. ,   2.5e-4 )  # S(10keV)
    GamowEnergy( 2,1,  2,1,   765. ,   58 )      # S
    GamowEnergy( 2,1,  3,1,   765. ,   14000 )   # S=14000   
    GamowEnergy( 2,1,  3,2,   8000. ,  10000 ) 
    GamowEnergy( 3,2,  3,2,   310. ,  550 ) 
    GamowEnergy( 1,1,  11,5,  6600. ,  550 ) 

    
    CoulombBarrier(2,1, 3,1 )
    CoulombBarrier(2,1, 3,2 )
