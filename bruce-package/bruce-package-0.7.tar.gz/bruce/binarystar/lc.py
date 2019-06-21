# Standard imports
import numba, numba.cuda, numpy as np , math 
from numba import prange 

# bruce imports
from .kepler import getTrueAnomaly, get_z, getProjectedPosition
from .eker_spots import eker_spots
from .doppler import Fdoppler
from .ellipsoidal import Fellipsoidal 
from .quadratic import Flux_drop_analytical_quadratic 
from .qpower2 import Flux_drop_analytical_power_2
from .uniform import Flux_drop_uniform 
from time import time as _time

#@numba.njit
def _lc(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, k ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        loglike_switch ):

    # Unpack and convert (assume incl in radians)
    w = math.atan2(fs, fc)
    e = fs**2 + fc**2 

    nspots = spots.shape[0]//4 

    loglike=0.
    for i in range(time.shape[0]):
        # Calculate the true anomaly 
        nu = getTrueAnomaly(time[i], e, w, period,  t_zero, incl, E_tol, radius_1 ) 

        # Calculate the projected seperation 
        z = get_z(nu, e, incl, w, radius_1)  

        # Initialse the flux
        # The model we will use is:
        #   F_tot = continuum + F_ecl + F_ellipsoidal + F_spots + F_transit 
        #   F_ellipsoidal -> ellipsoidal effect contralled by the mass ratio, q and the gravity limb-darkening coefficient
        #   F_spots       -> flux drop from spots controlled by the eker model
        #   F_transit     -> flux from the desired transit model (using 1 as the continuum)

        continuum = 1.0 # continuum at 1.0 (normalised)
        F_spots = 0.    # spot flux 
        F_doppler = 0.  # Doppler beaming
        F_ellipsoidal = 0.  # Ellipsoidal variation
        F_transit =  0.0    # transit flux drop

        # First, let's check for spots 
        if (nspots > 0):
            spot_phase = omega_1*2*math.pi*(time[i] - t_zero)/period
            for j in range(nspots) : F_spots += eker_spots(spots[j*4 + 0], spots[j*4 +1], incl, spots[j*4 +2], spots[j*4 +3], 0.5,0.3, spot_phase);


        # Next, we need to check for doppler beaming
        # Check for doppler beaming 
        if (alpha_doppler > 0) and (K1 > 0) : F_doppler = Fdoppler(nu, alpha_doppler, K1 )


        # Check for eelipsoidal variation and apply it if needed
        if (q>0.):
            alpha = math.acos(math.sin(w + nu)*math.sin(incl))
            F_ellipsoidal = Fellipsoidal(alpha, q, radius_1, incl, 0.5, gdc_1)

        # Check distance between them to see if its transiting
        if (z < (1.0+ k)):
            # So it's eclipsing, lets find out if its a primary or secondary
            f = getProjectedPosition(nu, w, incl);

            if (f > 0):
                # First, get the flux drop
                if (ld_law_1==0) : F_transit = Flux_drop_uniform( z, k, 1.) # uniform limb-darkening 
                if (ld_law_1==1) : F_transit = Flux_drop_analytical_quadratic( z,  k,  ldc_1_1,  ldc_1_2,  1e-8)
                if (ld_law_1==2) : F_transit = Flux_drop_analytical_power_2(z, k, ldc_1_1, ldc_1_2, 1E-8) 
                if (ld_law_1==-1) : F_transit = -1.

                # Now account for SBR (third light)
                #F_transit = F_transit/(1. + k*k*SBR) + (1.-1.0/(1 + k*k*SBR))

            elif (SBR>0.) :
                    if (ld_law_1!=-1) : F_transit =  Flux_drop_uniform(z, k, SBR) # Secondary eclipse
                    else : F_transit = -1.

        # Now put the model together
        model = continuum + F_spots + F_doppler + F_ellipsoidal + F_transit 

        # That's all from the star, so let's account for third light 
        if (light_3 > 0.0) : model = model/(1. + light_3) + (1.-1.0/(1. + light_3)) # third light


        if loglike_switch : 
            model = zp - 2.5*math.log10(model)
            wt = 1.0 / (LC_ERR[i]**2 + J**2)
            loglike += -0.5*((LC[i] - model)**2*wt - math.log(wt))
        else : LC[i] = model 

    return loglike 



#@numba.njit(parallel=True)
def _lc_prange(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, k ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        loglike_switch ):

    # Unpack and convert (assume incl in radians)
    w = math.atan2(fs, fc)
    e = fs**2 + fc**2 

    nspots = spots.shape[0]//4 

    loglike=0.
    for i in prange(time.shape[0]):
        # Calculate the true anomaly 
        nu = getTrueAnomaly(time[i], e, w, period,  t_zero, incl, E_tol ) 

        # Calculate the projected seperation 
        z = get_z(nu, e, incl, w, radius_1)  

        # Initialse the flux
        # The model we will use is:
        #   F_tot = continuum + F_ecl + F_ellipsoidal + F_spots + F_transit 
        #   F_ellipsoidal -> ellipsoidal effect contralled by the mass ratio, q and the gravity limb-darkening coefficient
        #   F_spots       -> flux drop from spots controlled by the eker model
        #   F_transit     -> flux from the desired transit model (using 1 as the continuum)

        continuum = 1.0 # continuum at 1.0 (normalised)
        F_spots = 0.    # spot flux 
        F_doppler = 0.  # Doppler beaming
        F_ellipsoidal = 0.  # Ellipsoidal variation
        F_transit =  0.0    # transit flux drop

        # First, let's check for spots 
        if (nspots > 0):
            spot_phase = omega_1*2*math.pi*(time[i] - t_zero)/period
            for j in range(nspots) : F_spots += eker_spots(spots[j*4 + 0], spots[j*4 +1], incl, spots[j*4 +2], spots[j*4 +3], 0.5,0.3, spot_phase);


        # Next, we need to check for doppler beaming
        # Check for doppler beaming 
        if (alpha_doppler > 0) and (K1 > 0) : F_doppler = Fdoppler(nu, alpha_doppler, K1 )


        # Check for eelipsoidal variation and apply it if needed
        if (q>0.):
            alpha = math.acos(math.sin(w + nu)*math.sin(incl))
            F_ellipsoidal = Fellipsoidal(alpha, q, radius_1, incl, 0.5, gdc_1)

        # Check distance between them to see if its transiting
        if (z < (1.0+ k)):
            # So it's eclipsing, lets find out if its a primary or secondary
            f = getProjectedPosition(nu, w, incl);

            if (f > 0):
                # First, get the flux drop
                if (ld_law_1==0) : F_transit = Flux_drop_uniform( z, k, 1.) # uniform limb-darkening 
                if (ld_law_1==1) : F_transit = Flux_drop_analytical_quadratic( z,  k,  ldc_1_1,  ldc_1_2,  1e-8)
                if (ld_law_1==2) : F_transit = Flux_drop_analytical_power_2(z, k, ldc_1_1, ldc_1_2, 1E-8) 

                # Now account for SBR (third light)
                #F_transit = F_transit/(1. + k*k*SBR) + (1.-1.0/(1 + k*k*SBR))

            elif (SBR>0.) :  F_transit =  Flux_drop_uniform(z, k, SBR) # Secondary eclipse
        
        # Now put the model together
        model = continuum + F_spots + F_doppler + F_ellipsoidal + F_transit 

        # That's all from the star, so let's account for third light 
        if (light_3 > 0.0) : model = model/(1. + light_3) + (1.-1.0/(1. + light_3)) # third light


        if loglike_switch : 
            model = zp - 2.5*math.log10(model)
            wt = 1.0 / (LC_ERR[i]**2 + J**2)
            loglike += -0.5*((LC[i] - model)**2*wt - math.log(wt))
        else : LC[i] = model 

    return loglike 



@numba.cuda.jit
def kernel_lc(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, k ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        loglike ):

    # Unpack and convert (assume incl in radians)
    w = math.atan2(fs, fc)
    e = fs**2 + fc**2 

    i = numba.cuda.grid(1)


    nspots = spots.shape[0]//4 

    # Calculate the true anomaly 
    nu = getTrueAnomaly(time[i], e, w, period,  t_zero, incl, E_tol ) 

    # Calculate the projected seperation 
    z = get_z(nu, e, incl, w, radius_1)  

    # Initialse the flux
    # The model we will use is:
    #   F_tot = continuum + F_ecl + F_ellipsoidal + F_spots + F_transit 
    #   F_ellipsoidal -> ellipsoidal effect contralled by the mass ratio, q and the gravity limb-darkening coefficient
    #   F_spots       -> flux drop from spots controlled by the eker model
    #   F_transit     -> flux from the desired transit model (using 1 as the continuum)

    continuum = 1.0 # continuum at 1.0 (normalised)
    F_spots = 0.    # spot flux 
    F_doppler = 0.  # Doppler beaming
    F_ellipsoidal = 0.  # Ellipsoidal variation
    F_transit =  0.0    # transit flux drop

    # First, let's check for spots 
    if (nspots > 0):
        spot_phase = omega_1*2*math.pi*(time[i] - t_zero)/period
        for j in range(nspots) : F_spots += eker_spots(spots[j*4 + 0], spots[j*4 +1], incl, spots[j*4 +2], spots[j*4 +3], 0.5,0.3, spot_phase);


    # Next, we need to check for doppler beaming
    # Check for doppler beaming 
    if (alpha_doppler > 0) and (K1 > 0) : F_doppler = Fdoppler(nu, alpha_doppler, K1 )


    # Check for eelipsoidal variation and apply it if needed
    if (q>0.):
        alpha = math.acos(math.sin(w + nu)*math.sin(incl))
        F_ellipsoidal = Fellipsoidal(alpha, q, radius_1, incl, 0.5, gdc_1)

    # Check distance between them to see if its transiting
    if (z < (1.0+ k)):
        # So it's eclipsing, lets find out if its a primary or secondary
        f = getProjectedPosition(nu, w, incl);

        if (f > 0):
            # First, get the flux drop
            if (ld_law_1==0) : F_transit = Flux_drop_uniform( z, k, 1.) # uniform limb-darkening 
            if (ld_law_1==1) : F_transit = Flux_drop_analytical_quadratic( z,  k,  ldc_1_1,  ldc_1_2,  1e-8)
            if (ld_law_1==2) : F_transit = Flux_drop_analytical_power_2(z, k, ldc_1_1, ldc_1_2, 1E-8) 

            # Now account for SBR (third light)
            #F_transit = F_transit/(1. + k*k*SBR) + (1.-1.0/(1 + k*k*SBR))

        elif (SBR>0.) :  F_transit =  Flux_drop_uniform(z, k, SBR) # Secondary eclipse
    
    # Now put the model together
    model = continuum + F_spots + F_doppler + F_ellipsoidal + F_transit 

    # That's all from the star, so let's account for third light 
    if (light_3 > 0.0) : model = model/(1. + light_3) + (1.-1.0/(1. + light_3)) # third light

    model = zp - 2.5*math.log10(model)

    wt = 1.0 / (LC_ERR[i]**2 + J**2)
    loglike[i] = -0.5*((LC[i] - model)**2*wt - math.log(wt))

@numba.cuda.reduce
def sum_reduce(a, b):
    return a + b

def lc(time, LC=np.zeros(1), LC_ERR=np.zeros(1), J=0., zp=0.,
    t_zero=0., period=1.,
    radius_1=0.2, k=0.2 ,
    fs=0., fc=0., 
    q=0., albedo=0.,
    alpha_doppler=0., K1=0.,
    spots = np.zeros(1), omega_1=1., 
    incl = 90.,
    ld_law_1=1, ldc_1_1=0.5, ldc_1_2=0.2, gdc_1=0.4,
    SBR=0., light_3=0.,
    E_tol=1e-5, parallel=False,
    gpu=0, loglike=np.zeros(1), blocks = 10, threads_per_block = 512):

    incl = np.pi * incl/180.


        
    if not gpu:
        # First, let's see if we need loglike or not!
        if LC_ERR[0]==0 : loglike_switch = 0
        else            : loglike_switch = 1

        # Now, let's initiase the arrays, if needed
        if not loglike_switch : LC = np.empty_like(time) 

        # Now make the call
        if parallel:
            loglike = _lc_prange(time, LC, LC_ERR, J, zp,
                t_zero, period,
                radius_1, k ,
                fs, fc, 
                q, albedo,
                alpha_doppler, K1,
                spots, omega_1, 
                incl,
                ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
                SBR, light_3,
                E_tol,
                loglike_switch )
        else:
            loglike = _lc(time, LC, LC_ERR, J, zp,
                t_zero, period,
                radius_1, k ,
                fs, fc, 
                q, albedo,
                alpha_doppler, K1,
                spots, omega_1, 
                incl,
                ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
                SBR, light_3,
                E_tol,
                loglike_switch )
                

        if loglike_switch : return loglike 
        else              : return LC 

    if gpu:
        # Loglike ony supported 
        # assumeing loglike is array

        ## Call the kernel to populate loglike
        #start = _time() 
        kernel_lc[blocks, threads_per_block](time, LC, LC_ERR, J, zp,
            t_zero, period,
            radius_1, k ,
            fs, fc, 
            q, albedo,
            alpha_doppler, K1,
            spots, omega_1, 
            incl,
            ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
            SBR, light_3,
            E_tol,
            loglike )
        #end = _time() 
        #print('Kernel : {:}'.format(end-start))
        #start = _time() 

        # let's synchronise to ensure it's finished
        #numba.cuda.synchronize() 
        #end = _time() 
        #print('sync : {:}'.format(end-start))

        #start = _time() 
        # Now reduce the loglike array
        #lll =  sum_reduce(loglike)
        #end = _time() 
        #print('reduce : {:}'.format(end-start))
        return sum_reduce(loglike)

'''
TEST 3


import numpy as np 
import matplotlib.pyplot as plt  
from bruce import lc 

t = np.linspace(-0.2, 0.8, 100) 
f = lc(t) 
m = -2.5*np.log10(f) 
me = np.random.uniform(0.5e-3,1.5e-3,t.shape[0])
m = np.random.normal(m, me)  

zps = np.linspace(-1,1,1000)

for i in zps : plt.scatter(i, lc(t,m , me, zp=i))
plt.show()
'''


'''
# TEST 2 
import numpy as np 
import matplotlib.pyplot as plt  

t = np.linspace(-0.2, 0.8, 1e6) 
f = lc(t) 
m = -2.5*np.log10(f) 
me = np.random.uniform(0.5e-3,1.5e-3,t.shape[0])
m = np.random.normal(m, me) 

CPU_loglike = lc(t, m, me) 
print('CPU log : ', CPU_loglike)


d_t = numba.cuda.to_device(t)
d_m = numba.cuda.to_device(m)
d_me = numba.cuda.to_device(me) 
d_spots = numba.cuda.to_device(np.array([]))
d_loglike = numba.cuda.to_device(np.empty_like(t)) 

threads_per_block = 256 
blocks = int(np.ceil(t.shape[0]/threads_per_block))


GPU_loglike = lc(d_t, d_m, d_me, gpu=1, loglike=d_loglike, blocks = blocks, threads_per_block = threads_per_block)
print('GPU log : ', GPU_loglike)



plt.scatter(t, m, c='k', s=10)
plt.gca().invert_yaxis() 
plt.show() 
'''
'''

# TEST 1
import numpy as np 
import matplotlib.pyplot as plt 

time = np.linspace(-0.2, 0.8, 1000) 
LC = np.empty_like(time) 
LC_ERR = np.empty_like(time) 
J = 0.1 
zp = 0. 

t_zero = 0. 
period = 1. 
radius_1 = k = 0.2 
fs=fc = 0. 
q = 0.
albedo = 0. 

alpha_doppler = 0.
K1 = 150 

spots = np.array([0.2, 0.2, 0.2, 0.9,4.2, 0.2, 0.2, 0.9]) 
omega_1 = 1.0 

incl = math.pi/2 

ld_law_1 = 1 
ldc_1_1 = 0.5 
ldc_1_2 = 0.2 
gdc_1 = 0.4

SBR = 0.
light_3 = 0. 

E_tol = 1e-5 
logswitch =0

a = _lc(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, k ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        logswitch )


lC = -2.5*np.log10(LC)
LC_ERR = np.random.uniform(0.5e-3, 1.5e-3, time.shape[0])
LC = np.random.normal(LC, LC_ERR)


a = _lc(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, k ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        1 )


plt.scatter(time, LC, c='k', s=10)
plt.title('Loglike : {:}'.format(   a  ))


plt.figure() 

k = np.linspace(0.05,0.4, 100) 
for i in k : plt.scatter(i, _lc(time, LC, LC_ERR, J, zp,
        t_zero, period,
        radius_1, i ,
        fs, fc, 
        q, albedo,
        alpha_doppler, K1,
        spots, omega_1, 
        incl,
        ld_law_1, ldc_1_1, ldc_1_2, gdc_1,
        SBR, light_3,
        E_tol,
        1 ))
plt.show() 
'''