"""*******************************************************
This code converts redshift to distance and the oposite
******************************************************"""

from . import cosmo_pars
import math
import numpy as np
import scipy.integrate as integrate
import pdb
from . import distances_conversions
from . import find

def redshift2distance(redshift,CosmoPar=None):
    """Description: converts redshift to distance, given the cosmological parameters
    Input  :-redshift, or a numpy array of redhsifts
            -Cosmological parameters. Default is
    Output :- a dictionnary with keys:
            - distanc_pc (in parsecs)
            - dm
     Tested : yes, compared to Eran's function with same name
         By : Maayane T. Soumagnac Feb 2019. Inspired by Eran's function of the same name
        URL :
     Example: dist=lum_dist.redshift2distance(8.8)
     Reliable: checked against Eran's function lum_dist """
    c=29979245800   # speed of light [cm/sec]
    Pc = 3.0857e18  #Parsec [cm]
    if CosmoPar is None:
    #    CosmoPar='wmap3'
    #print('CosmoPar is',CosmoPar)

        cosmological_parameters=cosmo_pars.cosmo_pars(Partype='wmap3')[0]


    H0_beforeconv=cosmological_parameters['H0']
    OmegaM   = cosmological_parameters['OmegaM']
    OmegaL   = cosmological_parameters['OmegaL']
    OmegaRad = cosmological_parameters['OmegaRad']
    # convert H0 to cm/sec/sec
    H0 = H0_beforeconv*100000./(Pc*1e6)
    if OmegaM+OmegaL>1:
        Lx = lambda x:math.sin(x)
        K  = 1 - OmegaM - OmegaL
    elif ((OmegaM+OmegaL)<1):
        Lx = lambda x:math.sinh(x)
        K  = 1 - OmegaM - OmegaL
    else:
        Lx = lambda x:x
        K  = 1

    Int = lambda x: ((1 + x) ** 2. * (1 + OmegaM * x) - x * (2 + x) * OmegaL) ** (-1. / 2)
    if isinstance(redshift, np.ndarray):
        N  = len(redshift)
        DL = np.zeros(N)
        for i in range(N):
            ZI = redshift[i]
            DL_Int = integrate.quad(Int, 0, ZI)[0]
            DL[i] = (c * (1 + ZI) / (H0 * math.sqrt(abs(K)))) * Lx(math.sqrt(abs(K)) * DL_Int)
        DL = DL / Pc
        # distance modulus:
        DM = 5. * np.log10(DL / 10)
    else:
        ZI=redshift
        DL_Int = integrate.quad(Int,0,ZI)[0]
        DL = (c*(1+ZI)/(H0*math.sqrt(abs(K))))*Lx(math.sqrt(abs(K))*DL_Int)
        # luminosity distance in Parsecs:
        DL = DL/Pc
        #distance modulus:
        DM = 5.*math.log10(DL/10)
    D=dict()
    D['distance_pc']=DL
    D['dm']=DM
    return D

def distance2redshift(dist,Type=None,CosmoPar=None):
    """Description: Given the distance modulus or distance, calculates the corresponding redshift
    Input  :-Vector of distance modulus or luminosity distance in parsec
            -Type of first input argument:
            'DM'  - distance modulus
            'LD'  - luminosity distance (default).
            -Cosmological parameters. Default is 'wmap3'
    Output :- redshift
     Tested : yes, compared to Eran's function with same name
         By : Maayane T. Soumagnac Feb 2019. Inspired by Eran's function of the same name
        URL :
     Example: z=lum_dist.distance2redshift(40.5,'dm')
     Reliable:  checked against Eran's function inv_lum_dist """

    if CosmoPar is None:
    #    CosmoPar='wmap3'
    #print('CosmoPar is',CosmoPar)
        cosmological_parameters=cosmo_pars.cosmo_pars(Partype='wmap3')[0]
    else:
        cosmological_parameters = cosmo_pars.cosmo_pars(Partype=CosmoPar)[0]
    if Type is None:
        Type='LD'
    else:
        Type=Type
    print(Type.lower())
    if Type.lower() not in ['ld','dm']:
        print("type must be 'LD' (Lumnosity Distance) or 'DM' (Distance Modulus). Unknown type.")
        pdb.set_trace()

    H0_beforeconv=cosmological_parameters['H0']
    OmegaM   = cosmological_parameters['OmegaM']
    OmegaL   = cosmological_parameters['OmegaL']
    OmegaRad = cosmological_parameters['OmegaRad']
    #print('Type.lower() is',Type.lower())
    if Type.lower() == 'dm':
        LumDist=distances_conversions.DM_to_pc(dist)
        #print('LumDist of DM={0} is {1}'.format(dist,LumDist))
    else:
        LumDist=dist

    if isinstance(LumDist, np.ndarray):
        Ndm = len(dist)
        Z = np.zeros(Ndm)
        for Idm in range(Ndm):
            Z[Idm] = find.fun_binsearch( lambda x:redshift2distance(x,CosmoPar=CosmoPar)['distance_pc'], LumDist[Idm], [1e-15,100], 1e-5)
    else:
        Z=find.fun_binsearch( lambda x:redshift2distance(x,CosmoPar=CosmoPar)['distance_pc'], LumDist, [1e-15,100], 1e-5)
    return Z