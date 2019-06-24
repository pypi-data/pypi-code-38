"""*******************************************************
Brutus: a python's implementation of Noam Ganot's code for shock cooling modeling.

This is a copy of Noam's sn_cooling_sw
******************************************************"""
#print(__doc__)

import numpy as np
import math
import pdb
from . import constant
from . import energy_conversions
from . import calc_black_body_flux_filters
from . import get_filter
from . import lum_dist
from astropy import constants as const
import multiprocessing as mp

__all__=['sn_cooling_sw']
kB_cgs = const.k_B.cgs.value

def sn_cooling_sw(Time=None,Type=None,Vs=None,E51=None,Rs=None,Mejs=None,f_rho=None,kappa=None,Tcorr=None,redshift=None,Ebv=None,Dist_Mpc=None,Rv=None,FiltSys=None,Model=None,Filter_vector=None,output_flux=None,dic_transmissions=None,verbose=False):
    """Description:Calculate the shock cooling light curve (following the shock breakout) of a supernova, based on the Sapir & Waxman (2017) model (ApJ 838:130)
    	Input  :-Vector of times [days] in which to calculate the shock cooling luminosity in the obeserver frame. Default is logspace(log10(1./24),log10(10),30).';
    	        - Type - {'rsg','bsg','wr'}. Default is 'rsg'.
    	        - Vs -   The shock velocity paramaeter in units of cm/s. Default is 10^8.5 cm/s (see eq. 2,3).
    	        - E51  - Energy in units of 10^51 erg. Default is 1. If empty will use Vs field, otherwise will override the Vs field. Default is empty.
    	        - Rs   - Progenitor radius in units of the solar radii. Default is 500.
    	        - Mejs  - Ejecta mass in solar masses. Default is 10. Ms in Noam's code
    	        - f_rho- f_{\rho} parameter. If empty use 1 for 'rsg', 0.05 for 'bsg', and 0.1 for 'wr'.
    	        - kappa- Opacity. Default is 0.34 cm^2 gr^-1.
    	        - Tcorr- Temperature correction factor. Default is 1.1 for RSG and 1.0 for BSG.
    	        - redshift'- SN redshift. Default is 0.023061. If Dist_Mpc is not empty, will be caluclated from it.
    	        - Dist_Mpc - SN distance [Mpc]. If empty will use the redshift field, otherwise will override the redshift field. Default is empty.
    	        - Ebv  - Extinction E(B-V). Default is 0.
    	        - Rv   - Selective extinction (R_V). Default is 3.08.Default is 'LIM'. If FiltFam is a struct in the format returned by
    	        get_filter.m, the input filter is used instead of
    	        calling get_filter.m
    	        - FiltName'- Filter name (see get_filter.m for options). Default is 'JPL'.
    	        - FiltSys - Filter system {'AB','Vega'}. Default is 'AB'.
    	        - NOT IMPLEMENTED Wave    - Wavelength [A] of AB monochromatic magnitude to calculate. If provided the returned magnitude will
    	        corresponds to this wavelength (instead of the filter family and name). Default is empty.
    	        - Model'- Determine weither to use SK17 extension to the original RW11 model by supressing the bolometric
    	        luminocity or not. Extending the model beyond the small delta approximation introduces dependencies on the progenitor's structure. Default is 'RW'.
    	        Use 'SW' to extend.
        Output :-[L,Tc,R,t_d,Mag,t_min,t_max,t_opac,t_tr,t_delta]
                - Intrinsic luminosity [erg/s] as a function of time.
                - Intrinsic color temperature [K] as a function of time.
                - photospheric effective radius [cm] as a function of time (using T_col and not T_ph).
                - t_d [days] in the rest frame.
                - Observed apparnt Magnitude as a function of time. Corrected for redshift.
                - t_min [days]  - the earliest time the model is valid given in rest frame.
                - t_max [days]  - the latest time the dynamical model is valid given in rest frame.
                - t_opac [days] - the time T_ph = 0.7eV and the constant opacity approximation breaks. The time is given in rest frame.
                - t_tr [days]   - the transperancy time which is the timescale for the luminosity suppression.
                - t_delta [days]- the time where the small delta approximation breaks (delta ~ 0.1) and the emmision becomes dependent in the envelope density profile. The time is given in rest frame.
    	Tested by Noam Ganot.
    	    By : Maayane T. Soumagnac Feb 2019
    	   URL :
    	Example:
    	Reliable:
    	"""

    SolR=constant.SunR
    #print(SolR)
    #pdb.set_trace()
    SolM=constant.SunM
    SigmaB = constant.sigma

    if Time is None:
        Time=np.logspace(math.log10(1. / 24),math.log10(10),30)
    if Type is None:
        Type='rsg'
    if Vs is None:
        Vs=10**8.5#
    if Mejs is None:
        Mejs=10#
    if Rs is None:
        Rs=500#
    if f_rho is None:
        f_rho=1
    if kappa is None:
        kappa=0.34
    if redshift is None:
        redshift= 0.023061
    if Ebv is None:
        Ebv=0
    if Rv is None:
        Rv=3.08
    if FiltSys is None:
        FiltSys='AB'
    if Model is None:
        Model='Original'

    #TO DO if Dist is None:
    if Dist_Mpc is None:
        Dist=lum_dist.redshift2distance(redshift)
    else:
        Dist=Dist_Mpc*1e6#pc
        redshift=lum_dist.distance2redshift(Dist,'ld')
        #pdb.set_trace()

    #convert input time to restframe time (comprendre)
    #print('redshift is',redshift)
    td=Time/(1+redshift)
    #print('Time is',Time)
    #print('td is',td)
    #print('redshift is',redshift)
    #pdb.set_trace()
    if Type.lower()=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        A=0.94
        a=1.67
        alpha=0.8
        eps1=0.027
        eps2=0.086
        L_RW_prefactor=2.0
        Tph_RW_prefactor = 1.61
        Menv = f_rho ** 2 / (1 + f_rho ** 2) * Mejs

    elif Type.lower()=='bsg': #Hydrogen radiative enveloppe n=3
        beta = 0.186
        A = 0.79
        a = 4.57
        alpha = 0.73
        eps1 = 0.016
        eps2 = 0.175
        L_RW_prefactor=2.1
        Tph_RW_prefactor = 1.69
        Menv = f_rho*Mejs/(0.08+f_rho)
    else:
        print('unknown type of progenitor')
        pdb.set_trace()

    if E51 is None:
        v_sstar=Vs
    else:
        v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))

    Tph_RW=Tph_RW_prefactor*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV

    if Tcorr is None:
        Tcorr=1.1
    Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T') # Temp in Kelvins as a function of time

    L_RW=L_RW_prefactor*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s

    #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
    t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

    if Model.lower() == 'sw':#equation 19 of SW
        #print('model is sw')
        #pdb.set_trace()
        LtoL_RW=A*np.exp(-(a*td/t_tr)**alpha)
        L=L_RW*LtoL_RW
    else:
        L=L_RW #radius as a function of time

    #Model Validity Limits SW eq 5
    tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days

    #print('Rs*SolR/1e13',Rs*SolR/1e13)# ok
    #print('v_sstar/10**8.5',v_sstar/10**8.5)#presque ok
    #print('max',max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)))#ok
    #print('(Rs*SolR/1e13)**0.4',(Rs*SolR/1.e13)**0.4)
    #print('(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7',(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)#ok
    #pdb.set_trace()

    tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

    #opacity condition #SW equation 24
    topac=((0.7*(kappa/0.34)**0.25/(Tph_RW_prefactor*(Rs*SolR/1e13)**0.25))*(f_rho*Mejs*kappa/0.34/(v_sstar/10**8.5)**2)**eps1)**(1/(2*eps1-0.5))
#7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
    tmax=t_tr/a

    pc=3.08567758e18

    R=np.sqrt(L/(4*math.pi*SigmaB*Tc**4)) #radius as a function of time, of BB with temperature Tc
    #print('Dist is',Dist)
    #pdb.set_trace()
    #redshifted_Tc=Tc/(1+redshift)
    if Filter_vector is not None:
        [P, wav] = get_filter.make_filter_object(Filter_vector,dic_transmissions=dic_transmissions)
        fluxes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxes_verif=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        magnitudes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxfile_block = 0
        Spec_factor = (L / (
        SigmaB * Tc ** 4 * 4 * math.pi * (pc * Dist['distance_pc']) ** 2))  # /(4*math.pi*(Dist['distance_pc']*pc)**2)

        if verbose==True:
            print('Tc is',Tc)
            print('SigmaB*Tc**4 is',SigmaB*Tc**4)
            print('L is',L)
            print('Spec_factor is',Spec_factor)
        print(Filter_vector)
        #pdb.set_trace()
        for i,j in enumerate(Time):
            fluxes[i,:]=(1+redshift)**4*Spec_factor[i]*calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i]/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_dic=dic_transmissions,verbose=verbose)[:,3]

            #print('fluxes[i,:]',fluxes[i,:])
            #pdb.set_trace()
            # ALMOST THE SAME AS (R/D)**2*B_lambda
            #fluxes[i, :]=calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), Filter_vector=Filter_vector, P_vector=None, Radius=R[i]
            #                                                                      , distance_pc=Dist['distance_pc'],
            #                         output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
            #                         z=redshift, output_file=None)[:,3]

            #pdb.set_trace()
            #magnitudes[i,:]=calc_black_body_mag_filters.calc_black_body_mag_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), 'AB', Filter_vector=Filter_vector, P_vector=None, Radius=R[i],
            #                            distance_pc=Dist['distance_pc'], output_plot=False, output_txt=False, show_plots=False, z=redshift, Ebv=Ebv,
            #                            mabs=False)[:,4]
            #print(Filter_vector)
            list_filters=[Filter_vector[s][1] for s in range(len(Filter_vector))]
            #print([Filter_vector[s][1] for s in range(len(Filter_vector))])
            #print(fluxes[i,:])
            #print(Time[i]*np.ones(np.shape(Filter_vector)[0]))
            #pdb.set_trace()
            if output_flux is not None:
                if isinstance(fluxfile_block, np.ndarray) is True:
                    fluxfile_block=np.vstack((fluxfile_block,np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)))
                else:
                    fluxfile_block=np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)
        if output_flux is not None:
            np.savetxt(output_flux,fluxfile_block,fmt='%.18e,%.18e,%s',header='jd,flux,filter',delimiter=',',comments='')

        return L,Tc,R,td,magnitudes,tmin,tmax,topac,t_tr,tdelta,fluxes,Tph_RW,L_RW,Spec_factor
    else:
        return L,Tc, R, td, tmin, tmax, topac, t_tr, tdelta,Tph_RW,L_RW


    '''
    if Type=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        if E51 is None:
            v_sstar=Vs
        else:
            v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))
        eps1=0.027
        eps2=0.086
        Tph_RW=1.61*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV
        if Tcorr is None:
            Tcorr=1.1
        Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T')
        L_RW=2.0*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s
        #Menv: the mass of the enveloppe
        Menv=f_rho**2/(1+f_rho**2)*Mejs
        #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
        t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

        A=0.94
        a=1.67
        alpha=0.8

        if Model is 'SW':#equation 19 of SW
            LtoL_RW=a*np.exp(-(a*td/t_tr)**alpha)
            L=L_RW*LtoL_RW
        else:
            L=L_RW

        #Model Validity Limits SW eq 5
        tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days
        tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

        #opacity condition #SW equation 24
        topac=7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
        tmax=t_tr/a


    elif Type is 'bsg': #Hydrogen radiative enveloppe n=3


        beta = 0.186
        if E51 is None:
            v_sstar = Vs
        else:
            v_sstar = 1.05 * f_rho ** (-beta) * math.sqrt(E51 * 1e51 / (Mejs * SolM))
        eps1 = 0.016
        eps2 = 0.175
        Tph_RW = 1.69 * ((v_sstar / 10 ** 8.5) ** 2 * np.power(td, 2) / (f_rho * Mejs * kappa / 0.34)) ** eps1 * (
                                                                                                                 Rs * SolR / 1e13) ** 0.25 / (
                                                                                                                                             kappa / 0.34) ** 0.25 * np.power(
            td, -0.5)  # eV
        if Tcorr is None:
            Tcorr = 1.
        Tc = energy_conversions.convert_energy(Tph_RW * Tcorr, 'ev', 'T')
        L_RW = 2.1 * 1e42 * ((v_sstar / 10 ** 8.5) * np.power(td, 2) / (f_rho * Mejs * kappa / 0.34)) ** -eps2 * (
        (v_sstar / 10 ** 8.5) ** 2 * (Rs * SolR / 1e13) / (kappa / 0.34))  # erg/s

        # Menv: the mass of the enveloppe
        Menv = f_rho*Mejs/(0.08+f_rho)

        # t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
        t_tr = 19.5 * math.sqrt((kappa / 0.34) * Menv / (v_sstar / 10 ** 8.5))  # days

        A = 0.79
        a = 4.57
        alpha = 0.73

        if Model is 'SW':  # equation 19 of SW
            LtoL_RW = a * np.exp(-(a * td / t_tr) ** alpha)
            L = L_RW * LtoL_RW
        else:
            L = L_RW

        # Model Validity Limits SW eq 5
        tmin = 0.2 * (Rs * SolR / 1e13) / (v_sstar / 10 ** 8.5) * max(0.5, (Rs * SolR / 1e13) ** 0.4 / (
        (f_rho * kappa / 0.34 * Mejs) ** 0.2 * (v_sstar / 10 ** 8.5) ** 0.7))  # days
        tdelta = 3 * f_rho ** -0.1 * math.sqrt((kappa / 0.34) * Mejs) / (v_sstar / 10 ** 8.5)  # days

        # opacity condition #SW equation 24
        topac = 7.4 * ((Rs * SolR / 1e13) / (kappa / 0.34)) ** 0.55  # days
        tmax = t_tr / a
    else:
       print('unknown type of progenitor')
       pdb.set_trace()

'''


def sn_cooling_sw_w_Pyphot(Time=None,Type=None,Vs=None,E51=None,Rs=None,Mejs=None,f_rho=None,kappa=None,Tcorr=None,redshift=None,Ebv=None,Dist_Mpc=None,Rv=None,FiltSys=None,Model=None,Filter_vector=None,output_flux=None,filters_directory=None,verbose=False):
    """Description:Calculate the shock cooling light curve (following the shock breakout) of a supernova, based on the Sapir & Waxman (2017) model (ApJ 838:130)
    	Input  :-Vector of times [days] in which to calculate the shock cooling luminosity in the obeserver frame. Default is logspace(log10(1./24),log10(10),30).';
    	        - Type - {'rsg','bsg','wr'}. Default is 'rsg'.
    	        - Vs -   The shock velocity paramaeter in units of cm/s. Default is 10^8.5 cm/s (see eq. 2,3).
    	        - E51  - Energy in units of 10^51 erg. Default is 1. If empty will use Vs field, otherwise will override the Vs field. Default is empty.
    	        - Rs   - Progenitor radius in units of the solar radii. Default is 500.
    	        - Mejs  - Ejecta mass in solar masses. Default is 10. Ms in Noam's code
    	        - f_rho- f_{\rho} parameter. If empty use 1 for 'rsg', 0.05 for 'bsg', and 0.1 for 'wr'.
    	        - kappa- Opacity. Default is 0.34 cm^2 gr^-1.
    	        - Tcorr- Temperature correction factor. Default is 1.1 for RSG and 1.0 for BSG.
    	        - redshift'- SN redshift. Default is 0.023061. If Dist_Mpc is not empty, will be caluclated from it.
    	        - Dist_Mpc - SN distance [Mpc]. If empty will use the redshift field, otherwise will override the redshift field. Default is empty.
    	        - Ebv  - Extinction E(B-V). Default is 0.
    	        - Rv   - Selective extinction (R_V). Default is 3.08.Default is 'LIM'. If FiltFam is a struct in the format returned by
    	        get_filter.m, the input filter is used instead of
    	        calling get_filter.m
    	        - FiltName'- Filter name (see get_filter.m for options). Default is 'JPL'.
    	        - FiltSys - Filter system {'AB','Vega'}. Default is 'AB'.
    	        - NOT IMPLEMENTED Wave    - Wavelength [A] of AB monochromatic magnitude to calculate. If provided the returned magnitude will
    	        corresponds to this wavelength (instead of the filter family and name). Default is empty.
    	        - Model'- Determine weither to use SK17 extension to the original RW11 model by supressing the bolometric
    	        luminocity or not. Extending the model beyond the small delta approximation introduces dependencies on the progenitor's structure. Default is 'RW'.
    	        Use 'SW' to extend.
        Output :-[L,Tc,R,t_d,Mag,t_min,t_max,t_opac,t_tr,t_delta]
                - Intrinsic luminosity [erg/s] as a function of time.
                - Intrinsic color temperature [K] as a function of time.
                - photospheric effective radius [cm] as a function of time (using T_col and not T_ph).
                - t_d [days] in the rest frame.
                - Observed apparnt Magnitude as a function of time. Corrected for redshift.
                - t_min [days]  - the earliest time the model is valid given in rest frame.
                - t_max [days]  - the latest time the dynamical model is valid given in rest frame.
                - t_opac [days] - the time T_ph = 0.7eV and the constant opacity approximation breaks. The time is given in rest frame.
                - t_tr [days]   - the transperancy time which is the timescale for the luminosity suppression.
                - t_delta [days]- the time where the small delta approximation breaks (delta ~ 0.1) and the emmision becomes dependent in the envelope density profile. The time is given in rest frame.
    	Tested by Noam Ganot.
    	    By : Maayane T. Soumagnac Feb 2019
    	   URL :
    	Example:
    	Reliable:
    	"""

    SolR=constant.SunR
    #print(SolR)
    #pdb.set_trace()
    SolM=constant.SunM
    SigmaB = constant.sigma

    if Time is None:
        Time=np.logspace(math.log10(1. / 24),math.log10(10),30)
    if Type is None:
        Type='rsg'
    if Vs is None:
        Vs=10**8.5#
    if Mejs is None:
        Mejs=10#
    if Rs is None:
        Rs=500#
    if f_rho is None:
        f_rho=1
    if kappa is None:
        kappa=0.34
    if redshift is None:
        redshift= 0.023061
    if Ebv is None:
        Ebv=0
    if Rv is None:
        Rv=3.08
    if FiltSys is None:
        FiltSys='AB'
    if Model is None:
        Model='Original'

    #TO DO if Dist is None:
    if Dist_Mpc is None:
        Dist=lum_dist.redshift2distance(redshift)
    else:
        Dist=Dist_Mpc*1e6#pc
        redshift=lum_dist.distance2redshift(Dist,'ld')
        #pdb.set_trace()

    #convert input time to restframe time (comprendre)
    #print('redshift is',redshift)
    td=Time/(1+redshift)
    #print('Time is',Time)
    #print('td is',td)
    #print('redshift is',redshift)
    #pdb.set_trace()
    if Type.lower()=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        A=0.94
        a=1.67
        alpha=0.8
        eps1=0.027
        eps2=0.086
        L_RW_prefactor=2.0
        Tph_RW_prefactor = 1.61
        Menv = f_rho ** 2 / (1 + f_rho ** 2) * Mejs

    elif Type.lower()=='bsg': #Hydrogen radiative enveloppe n=3
        beta = 0.186
        A = 0.79
        a = 4.57
        alpha = 0.73
        eps1 = 0.016
        eps2 = 0.175
        L_RW_prefactor=2.1
        Tph_RW_prefactor = 1.69
        Menv = f_rho*Mejs/(0.08+f_rho)
    else:
        print('unknown type of progenitor')
        pdb.set_trace()

    if E51 is None:
        v_sstar=Vs
    else:
        v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))

    Tph_RW=Tph_RW_prefactor*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV

    if Tcorr is None:
        Tcorr=1.1
    Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T') # Temp in Kelvins as a function of time

    L_RW=L_RW_prefactor*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s

    #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
    t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

    if Model.lower() == 'sw':#equation 19 of SW
        #print('model is sw')
        #pdb.set_trace()
        LtoL_RW=A*np.exp(-(a*td/t_tr)**alpha)
        L=L_RW*LtoL_RW
    else:
        L=L_RW #radius as a function of time

    #Model Validity Limits SW eq 5
    tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days

    #print('Rs*SolR/1e13',Rs*SolR/1e13)# ok
    #print('v_sstar/10**8.5',v_sstar/10**8.5)#presque ok
    #print('max',max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)))#ok
    #print('(Rs*SolR/1e13)**0.4',(Rs*SolR/1.e13)**0.4)
    #print('(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7',(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)#ok
    #pdb.set_trace()

    tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

    #opacity condition #SW equation 24
    topac = ((0.7 * (kappa / 0.34) ** 0.25 / (Tph_RW_prefactor * (Rs * SolR / 1e13) ** 0.25)) * (
    f_rho * Mejs * kappa / 0.34 / (v_sstar / 10 ** 8.5) ** 2) ** eps1) ** (1 / (2 * eps1 - 0.5))

    #topac=7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
    tmax=t_tr/a

    pc=3.08567758e18

    R=np.sqrt(L/(4*math.pi*SigmaB*Tc**4)) #radius as a function of time, of BB with temperature Tc
    #print('Dist is',Dist)
    #pdb.set_trace()
    #redshifted_Tc=Tc/(1+redshift)
    if Filter_vector is not None:
        [P, wav] = get_filter.make_filter_object_w_Pyphot(Filter_vector,filters_directory=filters_directory)
        fluxes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxes_verif=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        magnitudes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxfile_block = 0
        Spec_factor = (L / (
        SigmaB * Tc ** 4 * 4 * math.pi * (pc * Dist['distance_pc']) ** 2))  # /(4*math.pi*(Dist['distance_pc']*pc)**2)

        if verbose==True:
            print('Tc is',Tc)
            print('SigmaB*Tc**4 is',SigmaB*Tc**4)
            print('L is',L)
            print('Spec_factor is',Spec_factor)

        for i,j in enumerate(Time):
            print('redshifted temp',Tc[i]/(1+redshift))
            pdb.set_trace()
            fluxes[i,:]=(1+redshift)**4*Spec_factor[i]*calc_black_body_flux_filters.calc_black_body_flux_filters_w_Pyphot(Tc[i]/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_directory=filters_directory)[:,3]

            #print('fluxes[i,:]',fluxes[i,:])
            #pdb.set_trace()
            # ALMOST THE SAME AS (R/D)**2*B_lambda
            #fluxes[i, :]=calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), Filter_vector=Filter_vector, P_vector=None, Radius=R[i]
            #                                                                      , distance_pc=Dist['distance_pc'],
            #                         output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
            #                         z=redshift, output_file=None)[:,3]

            #pdb.set_trace()
            #magnitudes[i,:]=calc_black_body_mag_filters.calc_black_body_mag_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), 'AB', Filter_vector=Filter_vector, P_vector=None, Radius=R[i],
            #                            distance_pc=Dist['distance_pc'], output_plot=False, output_txt=False, show_plots=False, z=redshift, Ebv=Ebv,
            #                            mabs=False)[:,4]
            #print(Filter_vector)
            list_filters=[Filter_vector[s][1] for s in range(len(Filter_vector))]
            #print([Filter_vector[s][1] for s in range(len(Filter_vector))])
            #print(fluxes[i,:])
            #print(Time[i]*np.ones(np.shape(Filter_vector)[0]))
            #pdb.set_trace()
            if output_flux is not None:
                if isinstance(fluxfile_block, np.ndarray) is True:
                    fluxfile_block=np.vstack((fluxfile_block,np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)))
                else:
                    fluxfile_block=np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)
        if output_flux is not None:
            np.savetxt(output_flux,fluxfile_block,fmt='%.18e,%.18e,%s',header='jd,flux,filter',delimiter=',',comments='')

        return L,Tc,R,td,magnitudes,tmin,tmax,topac,t_tr,tdelta,fluxes,Tph_RW,L_RW,Spec_factor
    else:
        return L,Tc, R, td, tmin, tmax, topac, t_tr, tdelta,Tph_RW,L_RW


    '''
    if Type=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        if E51 is None:
            v_sstar=Vs
        else:
            v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))
        eps1=0.027
        eps2=0.086
        Tph_RW=1.61*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV
        if Tcorr is None:
            Tcorr=1.1
        Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T')
        L_RW=2.0*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s
        #Menv: the mass of the enveloppe
        Menv=f_rho**2/(1+f_rho**2)*Mejs
        #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
        t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

        A=0.94
        a=1.67
        alpha=0.8

        if Model is 'SW':#equation 19 of SW
            LtoL_RW=a*np.exp(-(a*td/t_tr)**alpha)
            L=L_RW*LtoL_RW
        else:
            L=L_RW

        #Model Validity Limits SW eq 5
        tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days
        tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

        #opacity condition #SW equation 24
        topac=7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
        tmax=t_tr/a


    elif Type is 'bsg': #Hydrogen radiative enveloppe n=3


        beta = 0.186
        if E51 is None:
            v_sstar = Vs
        else:
            v_sstar = 1.05 * f_rho ** (-beta) * math.sqrt(E51 * 1e51 / (Mejs * SolM))
        eps1 = 0.016
        eps2 = 0.175
        Tph_RW = 1.69 * ((v_sstar / 10 ** 8.5) ** 2 * np.power(td, 2) / (f_rho * Mejs * kappa / 0.34)) ** eps1 * (
                                                                                                                 Rs * SolR / 1e13) ** 0.25 / (
                                                                                                                                             kappa / 0.34) ** 0.25 * np.power(
            td, -0.5)  # eV
        if Tcorr is None:
            Tcorr = 1.
        Tc = energy_conversions.convert_energy(Tph_RW * Tcorr, 'ev', 'T')
        L_RW = 2.1 * 1e42 * ((v_sstar / 10 ** 8.5) * np.power(td, 2) / (f_rho * Mejs * kappa / 0.34)) ** -eps2 * (
        (v_sstar / 10 ** 8.5) ** 2 * (Rs * SolR / 1e13) / (kappa / 0.34))  # erg/s

        # Menv: the mass of the enveloppe
        Menv = f_rho*Mejs/(0.08+f_rho)

        # t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
        t_tr = 19.5 * math.sqrt((kappa / 0.34) * Menv / (v_sstar / 10 ** 8.5))  # days

        A = 0.79
        a = 4.57
        alpha = 0.73

        if Model is 'SW':  # equation 19 of SW
            LtoL_RW = a * np.exp(-(a * td / t_tr) ** alpha)
            L = L_RW * LtoL_RW
        else:
            L = L_RW

        # Model Validity Limits SW eq 5
        tmin = 0.2 * (Rs * SolR / 1e13) / (v_sstar / 10 ** 8.5) * max(0.5, (Rs * SolR / 1e13) ** 0.4 / (
        (f_rho * kappa / 0.34 * Mejs) ** 0.2 * (v_sstar / 10 ** 8.5) ** 0.7))  # days
        tdelta = 3 * f_rho ** -0.1 * math.sqrt((kappa / 0.34) * Mejs) / (v_sstar / 10 ** 8.5)  # days

        # opacity condition #SW equation 24
        topac = 7.4 * ((Rs * SolR / 1e13) / (kappa / 0.34)) ** 0.55  # days
        tmax = t_tr / a
    else:
       print('unknown type of progenitor')
       pdb.set_trace()

'''

def fluxes_para(x,y,redshift,Filter_vector,Ebv,dic_transmissions=None,verbose=False):
    return (1+redshift)**4*x*calc_black_body_flux_filters.calc_black_body_flux_filters(y/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_dic=dic_transmissions,verbose=verbose)[:,3]

def fluxes_para_w_Pyphot(x,y,redshift,Filter_vector,Ebv,filters_directory,verbose=False):
    return (1+redshift)**4*x*calc_black_body_flux_filters.calc_black_body_flux_filters_w_Pyphot(y/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_directory=filters_directory)[:,3]

def sn_cooling_sw_parallel(Time=None,Type=None,Vs=None,E51=None,Rs=None,Mejs=None,f_rho=None,kappa=None,Tcorr=None,redshift=None,Ebv=None,Dist_Mpc=None,Rv=None,FiltSys=None,Model=None,
                           Filter_vector=None,output_flux=None,dic_transmissions=None,filters_directory=None,verbose=False,async=True,processes=None):
    """Description:Calculate the shock cooling light curve (following the shock breakout) of a supernova, based on the Sapir & Waxman (2017) model (ApJ 838:130)
    	Input  :-Vector of times [days] in which to calculate the shock cooling luminosity in the obeserver frame. Default is logspace(log10(1./24),log10(10),30).';
    	        - Type - {'rsg','bsg','wr'}. Default is 'rsg'.
    	        - Vs -   The shock velocity paramaeter in units of cm/s. Default is 10^8.5 cm/s (see eq. 2,3).
    	        - E51  - Energy in units of 10^51 erg. Default is 1. If empty will use Vs field, otherwise will override the Vs field. Default is empty.
    	        - Rs   - Progenitor radius in units of the solar radii. Default is 500.
    	        - Mejs  - Ejecta mass in solar masses. Default is 10. Ms in Noam's code
    	        - f_rho- f_{\rho} parameter. If empty use 1 for 'rsg', 0.05 for 'bsg', and 0.1 for 'wr'.
    	        - kappa- Opacity. Default is 0.34 cm^2 gr^-1.
    	        - Tcorr- Temperature correction factor. Default is 1.1 for RSG and 1.0 for BSG.
    	        - redshift'- SN redshift. Default is 0.023061. If Dist_Mpc is not empty, will be caluclated from it.
    	        - Dist_Mpc - SN distance [Mpc]. If empty will use the redshift field, otherwise will override the redshift field. Default is empty.
    	        - Ebv  - Extinction E(B-V). Default is 0.
    	        - Rv   - Selective extinction (R_V). Default is 3.08.Default is 'LIM'. If FiltFam is a struct in the format returned by
    	        get_filter.m, the input filter is used instead of
    	        calling get_filter.m
    	        - FiltName'- Filter name (see get_filter.m for options). Default is 'JPL'.
    	        - FiltSys - Filter system {'AB','Vega'}. Default is 'AB'.
    	        - NOT IMPLEMENTED Wave    - Wavelength [A] of AB monochromatic magnitude to calculate. If provided the returned magnitude will
    	        corresponds to this wavelength (instead of the filter family and name). Default is empty.
    	        - Model'- Determine weither to use SK17 extension to the original RW11 model by supressing the bolometric
    	        luminocity or not. Extending the model beyond the small delta approximation introduces dependencies on the progenitor's structure. Default is 'RW'.
    	        Use 'SW' to extend.
        Output :-[L,Tc,R,t_d,Mag,t_min,t_max,t_opac,t_tr,t_delta]
                - Intrinsic luminosity [erg/s] as a function of time.
                - Intrinsic color temperature [K] as a function of time.
                - photospheric effective radius [cm] as a function of time (using T_col and not T_ph).
                - t_d [days] in the rest frame.
                - Observed apparnt Magnitude as a function of time. Corrected for redshift.
                - t_min [days]  - the earliest time the model is valid given in rest frame.
                - t_max [days]  - the latest time the dynamical model is valid given in rest frame.
                - t_opac [days] - the time T_ph = 0.7eV and the constant opacity approximation breaks. The time is given in rest frame.
                - t_tr [days]   - the transperancy time which is the timescale for the luminosity suppression.
                - t_delta [days]- the time where the small delta approximation breaks (delta ~ 0.1) and the emmision becomes dependent in the envelope density profile. The time is given in rest frame.
    	Tested by Noam Ganot.
    	    By : Maayane T. Soumagnac Feb 2019
    	   URL :
    	Example:
    	Reliable:
    	"""

    SolR=constant.SunR
    #print(SolR)
    #pdb.set_trace()
    SolM=constant.SunM
    SigmaB = constant.sigma

    if Time is None:
        Time=np.logspace(math.log10(1. / 24),math.log10(10),30)
    if Type is None:
        Type='rsg'
    if Vs is None:
        Vs=10**8.5#
    if Mejs is None:
        Mejs=10#
    if Rs is None:
        Rs=500#
    if f_rho is None:
        f_rho=1
    if kappa is None:
        kappa=0.34
    if redshift is None:
        redshift= 0.023061
    if Ebv is None:
        Ebv=0
    if Rv is None:
        Rv=3.08
    if FiltSys is None:
        FiltSys='AB'
    if Model is None:
        Model='Original'

    #TO DO if Dist is None:
    if Dist_Mpc is None:
        Dist=lum_dist.redshift2distance(redshift)
    else:
        Dist=Dist_Mpc*1e6#pc
        redshift=lum_dist.distance2redshift(Dist,'ld')
        #pdb.set_trace()

    #convert input time to restframe time (comprendre)
    #print('redshift is',redshift)
    td=Time/(1+redshift)
    #print('Time is',Time)
    #print('td is',td)
    #print('redshift is',redshift)
    #pdb.set_trace()
    if Type.lower()=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        A=0.94
        a=1.67
        alpha=0.8
        eps1=0.027
        eps2=0.086
        L_RW_prefactor=2.0
        Tph_RW_prefactor = 1.61
        Menv = f_rho ** 2 / (1 + f_rho ** 2) * Mejs

    elif Type.lower()=='bsg': #Hydrogen radiative enveloppe n=3
        beta = 0.186
        A = 0.79
        a = 4.57
        alpha = 0.73
        eps1 = 0.016
        eps2 = 0.175
        L_RW_prefactor=2.1
        Tph_RW_prefactor = 1.69
        Menv = f_rho*Mejs/(0.08+f_rho)
    else:
        print('unknown type of progenitor')
        pdb.set_trace()

    if E51 is None:
        v_sstar=Vs
    else:
        v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))

    Tph_RW=Tph_RW_prefactor*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV

    if Tcorr is None:
        Tcorr=1.1
    Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T') # Temp in Kelvins as a function of time

    L_RW=L_RW_prefactor*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s

    #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
    t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

    if Model.lower() == 'sw':#equation 19 of SW
        #print('model is sw')
        #pdb.set_trace()
        LtoL_RW=A*np.exp(-(a*td/t_tr)**alpha)
        L=L_RW*LtoL_RW
    else:
        L=L_RW #radius as a function of time

    #Model Validity Limits SW eq 5
    tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days

    #print('Rs*SolR/1e13',Rs*SolR/1e13)# ok
    #print('v_sstar/10**8.5',v_sstar/10**8.5)#presque ok
    #print('max',max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)))#ok
    #print('(Rs*SolR/1e13)**0.4',(Rs*SolR/1.e13)**0.4)
    #print('(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7',(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)#ok
    #pdb.set_trace()

    tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

    #opacity condition #SW equation 24
    topac = ((0.7 * (kappa / 0.34) ** 0.25 / (Tph_RW_prefactor * (Rs * SolR / 1e13) ** 0.25)) * (
    f_rho * Mejs * kappa / 0.34 / (v_sstar / 10 ** 8.5) ** 2) ** eps1) ** (1 / (2 * eps1 - 0.5))

    #topac=7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
    tmax=t_tr/a

    pc=3.08567758e18

    R=np.sqrt(L/(4*math.pi*SigmaB*Tc**4)) #radius as a function of time, of BB with temperature Tc
    #print('Dist is',Dist)
    #pdb.set_trace()
    #redshifted_Tc=Tc/(1+redshift)
    if Filter_vector is not None:
        [P, wav] = get_filter.make_filter_object(Filter_vector,dic_transmissions=dic_transmissions,filters_directory=filters_directory)
        fluxes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxes_verif=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        magnitudes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxfile_block = 0
        Spec_factor = (L / (
        SigmaB * Tc ** 4 * 4 * math.pi * (pc * Dist['distance_pc']) ** 2))  # /(4*math.pi*(Dist['distance_pc']*pc)**2)

        if verbose==True:
            print('Tc is',Tc)
            print('SigmaB*Tc**4 is',SigmaB*Tc**4)
            print('L is',L)
            print('Spec_factor is',Spec_factor)
        if processes is None:
            pool = mp.Pool(processes=8)
        else:
            print('I am using {0} cores in parallel, IMALEH!'.format(processes))
            pool = mp.Pool(processes=processes)
        if async ==True:
            resultx = [[Time[i],pool.apply_async(fluxes_para, args=(Spec_factor[i],Tc[i],redshift,Filter_vector,Ebv,dic_transmissions))] for i in range(np.shape(Time)[0])]
            #print(resultx)
            output = [np.array([p[0],p[1].get()[0]]) for p in resultx]
            results_unsorted = np.array(output)
            results= results_unsorted[np.argsort(results_unsorted,axis=0)[:,0]]
            pool.close()
        else:
            resultx =[np.array([Time[i],pool.apply(fluxes_para, args=(Spec_factor[i],Tc[i],redshift,Filter_vector,Ebv,dic_transmissions))[0]]) for i in range(np.shape(Time)[0])]
            results=np.array(resultx)

        '''
        for i,j in enumerate(Time):
            fluxes[i,:]=(1+redshift)**4*Spec_factor[i]*calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i]/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_directory=filters_directory)[:,3]

            #print('fluxes[i,:]',fluxes[i,:])
            #pdb.set_trace()
            # ALMOST THE SAME AS (R/D)**2*B_lambda
            #fluxes[i, :]=calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), Filter_vector=Filter_vector, P_vector=None, Radius=R[i]
            #                                                                      , distance_pc=Dist['distance_pc'],
            #                         output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
            #                         z=redshift, output_file=None)[:,3]

            #pdb.set_trace()
            #magnitudes[i,:]=calc_black_body_mag_filters.calc_black_body_mag_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), 'AB', Filter_vector=Filter_vector, P_vector=None, Radius=R[i],
            #                            distance_pc=Dist['distance_pc'], output_plot=False, output_txt=False, show_plots=False, z=redshift, Ebv=Ebv,
            #                            mabs=False)[:,4]
            #print(Filter_vector)
            list_filters=[Filter_vector[s][1] for s in range(len(Filter_vector))]
            #print([Filter_vector[s][1] for s in range(len(Filter_vector))])
            #print(fluxes[i,:])
            #print(Time[i]*np.ones(np.shape(Filter_vector)[0]))
            #pdb.set_trace()
            if isinstance(fluxfile_block, np.ndarray) is True:
                fluxfile_block=np.vstack((fluxfile_block,np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)))
            else:
                fluxfile_block=np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)
        if output_flux is not None:
            np.savetxt(output_flux,fluxfile_block,fmt='%.18e,%.18e,%s',header='jd,flux,filter',delimiter=',',comments='')
        '''
        return L,Tc,R,td,magnitudes,tmin,tmax,topac,t_tr,tdelta,results,Tph_RW,L_RW,Spec_factor
    else:
        return L,Tc, R, td, tmin, tmax, topac, t_tr, tdelta,Tph_RW,L_RW

def sn_cooling_sw_parallel_w_Pyphot(Time=None,Type=None,Vs=None,E51=None,Rs=None,Mejs=None,f_rho=None,kappa=None,Tcorr=None,redshift=None,Ebv=None,Dist_Mpc=None,Rv=None,FiltSys=None,Model=None,
                           Filter_vector=None,output_flux=None,filters_directory=None,verbose=False,async=True,processes=None):
    """Description:Calculate the shock cooling light curve (following the shock breakout) of a supernova, based on the Sapir & Waxman (2017) model (ApJ 838:130)
    	Input  :-Vector of times [days] in which to calculate the shock cooling luminosity in the obeserver frame. Default is logspace(log10(1./24),log10(10),30).';
    	        - Type - {'rsg','bsg','wr'}. Default is 'rsg'.
    	        - Vs -   The shock velocity paramaeter in units of cm/s. Default is 10^8.5 cm/s (see eq. 2,3).
    	        - E51  - Energy in units of 10^51 erg. Default is 1. If empty will use Vs field, otherwise will override the Vs field. Default is empty.
    	        - Rs   - Progenitor radius in units of the solar radii. Default is 500.
    	        - Mejs  - Ejecta mass in solar masses. Default is 10. Ms in Noam's code
    	        - f_rho- f_{\rho} parameter. If empty use 1 for 'rsg', 0.05 for 'bsg', and 0.1 for 'wr'.
    	        - kappa- Opacity. Default is 0.34 cm^2 gr^-1.
    	        - Tcorr- Temperature correction factor. Default is 1.1 for RSG and 1.0 for BSG.
    	        - redshift'- SN redshift. Default is 0.023061. If Dist_Mpc is not empty, will be caluclated from it.
    	        - Dist_Mpc - SN distance [Mpc]. If empty will use the redshift field, otherwise will override the redshift field. Default is empty.
    	        - Ebv  - Extinction E(B-V). Default is 0.
    	        - Rv   - Selective extinction (R_V). Default is 3.08.Default is 'LIM'. If FiltFam is a struct in the format returned by
    	        get_filter.m, the input filter is used instead of
    	        calling get_filter.m
    	        - FiltName'- Filter name (see get_filter.m for options). Default is 'JPL'.
    	        - FiltSys - Filter system {'AB','Vega'}. Default is 'AB'.
    	        - NOT IMPLEMENTED Wave    - Wavelength [A] of AB monochromatic magnitude to calculate. If provided the returned magnitude will
    	        corresponds to this wavelength (instead of the filter family and name). Default is empty.
    	        - Model'- Determine weither to use SK17 extension to the original RW11 model by supressing the bolometric
    	        luminocity or not. Extending the model beyond the small delta approximation introduces dependencies on the progenitor's structure. Default is 'RW'.
    	        Use 'SW' to extend.
        Output :-[L,Tc,R,t_d,Mag,t_min,t_max,t_opac,t_tr,t_delta]
                - Intrinsic luminosity [erg/s] as a function of time.
                - Intrinsic color temperature [K] as a function of time.
                - photospheric effective radius [cm] as a function of time (using T_col and not T_ph).
                - t_d [days] in the rest frame.
                - Observed apparnt Magnitude as a function of time. Corrected for redshift.
                - t_min [days]  - the earliest time the model is valid given in rest frame.
                - t_max [days]  - the latest time the dynamical model is valid given in rest frame.
                - t_opac [days] - the time T_ph = 0.7eV and the constant opacity approximation breaks. The time is given in rest frame.
                - t_tr [days]   - the transperancy time which is the timescale for the luminosity suppression.
                - t_delta [days]- the time where the small delta approximation breaks (delta ~ 0.1) and the emmision becomes dependent in the envelope density profile. The time is given in rest frame.
    	Tested by Noam Ganot.
    	    By : Maayane T. Soumagnac Feb 2019
    	   URL :
    	Example:
    	Reliable:
    	"""
    print('Filter_vector', Filter_vector)
    SolR=constant.SunR
    #print(SolR)
    #pdb.set_trace()
    SolM=constant.SunM
    SigmaB = constant.sigma

    if Time is None:
        Time=np.logspace(math.log10(1. / 24),math.log10(10),30)
    if Type is None:
        Type='rsg'
    if Vs is None:
        Vs=10**8.5#
    if Mejs is None:
        Mejs=10#
    if Rs is None:
        Rs=500#
    if f_rho is None:
        f_rho=1
    if kappa is None:
        kappa=0.34
    if redshift is None:
        redshift= 0.023061
    if Ebv is None:
        Ebv=0
    if Rv is None:
        Rv=3.08
    if FiltSys is None:
        FiltSys='AB'
    if Model is None:
        Model='Original'

    #TO DO if Dist is None:
    if Dist_Mpc is None:
        Dist=lum_dist.redshift2distance(redshift)
    else:
        Dist=Dist_Mpc*1e6#pc
        redshift=lum_dist.distance2redshift(Dist,'ld')
        #pdb.set_trace()

    #convert input time to restframe time (comprendre)
    #print('redshift is',redshift)
    td=Time/(1+redshift)
    #print('Time is',Time)
    #print('td is',td)
    #print('redshift is',redshift)
    #pdb.set_trace()
    if Type.lower()=='rsg': #Hydrodrogen convective enveloppe, n=3/2, equation 3 in SW
        beta=0.191
        A=0.94
        a=1.67
        alpha=0.8
        eps1=0.027
        eps2=0.086
        L_RW_prefactor=2.0
        Tph_RW_prefactor = 1.61
        Menv = f_rho ** 2 / (1 + f_rho ** 2) * Mejs

    elif Type.lower()=='bsg': #Hydrogen radiative enveloppe n=3
        beta = 0.186
        A = 0.79
        a = 4.57
        alpha = 0.73
        eps1 = 0.016
        eps2 = 0.175
        L_RW_prefactor=2.1
        Tph_RW_prefactor = 1.69
        Menv = f_rho*Mejs/(0.08+f_rho)
    else:
        print('unknown type of progenitor')
        pdb.set_trace()

    if E51 is None:
        v_sstar=Vs
    else:
        v_sstar=1.05*f_rho**(-beta)*math.sqrt(E51*1e51/(Mejs*SolM))

    Tph_RW=Tph_RW_prefactor*((v_sstar/10**8.5)**2*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**eps1*(Rs*SolR/1e13)**0.25/(kappa/0.34)**0.25*np.power(td,-0.5) #eV

    if Tcorr is None:
        Tcorr=1.1
    Tc=energy_conversions.convert_energy(Tph_RW*Tcorr,'ev','T') # Temp in Kelvins as a function of time

    L_RW=L_RW_prefactor*1e42*((v_sstar/10**8.5)*np.power(td,2)/(f_rho*Mejs*kappa/0.34))**-eps2*((v_sstar/10**8.5)**2*(Rs*SolR/1e13)/(kappa/0.34))#erg/s

    #t_tr: the time at which the enveloppe is expected to become transparent (e.q. 13-14 de SW)
    t_tr=19.5*math.sqrt((kappa/0.34)*Menv/(v_sstar/10**8.5))#days

    if Model.lower() == 'sw':#equation 19 of SW
        #print('model is sw')
        #pdb.set_trace()
        LtoL_RW=A*np.exp(-(a*td/t_tr)**alpha)
        L=L_RW*LtoL_RW
    else:
        L=L_RW #radius as a function of time

    #Model Validity Limits SW eq 5
    tmin=0.2*(Rs*SolR/1e13)/(v_sstar/10**8.5)*max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7))#days

    #print('Rs*SolR/1e13',Rs*SolR/1e13)# ok
    #print('v_sstar/10**8.5',v_sstar/10**8.5)#presque ok
    #print('max',max(0.5,(Rs*SolR/1e13)**0.4/((f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)))#ok
    #print('(Rs*SolR/1e13)**0.4',(Rs*SolR/1.e13)**0.4)
    #print('(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7',(f_rho*kappa/0.34*Mejs)**0.2*(v_sstar/10**8.5)**0.7)#ok
    #pdb.set_trace()

    tdelta=3*f_rho**-0.1*math.sqrt((kappa/0.34)*Mejs)/(v_sstar/10**8.5)#days

    #opacity condition #SW equation 24
    topac = (
                (0.7 * (kappa / 0.34) ** 0.25 / (Tph_RW_prefactor * (Rs * SolR / 1e13) ** 0.25)) *
                (f_rho * Mejs * kappa / 0.34 / (v_sstar / 10 ** 8.5) ** 2) ** eps1
            ) ** (1 / (2 * eps1 - 0.5))

    #topac=7.4*((Rs*SolR/1e13)/(kappa/0.34))**0.55#days
    tmax=t_tr/a

    pc=3.08567758e18

    R=np.sqrt(L/(4*math.pi*SigmaB*Tc**4)) #radius as a function of time, of BB with temperature Tc
    #print('Dist is',Dist)
    #pdb.set_trace()
    #redshifted_Tc=Tc/(1+redshift)
    if Filter_vector is not None:
        [P, wav] = get_filter.make_filter_object_w_Pyphot(Filter_vector,filters_directory=filters_directory)
        fluxes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxes_verif=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        magnitudes=np.zeros((np.shape(Time)[0],np.shape(Filter_vector)[0]))
        fluxfile_block = 0
        Spec_factor = (L / (
        SigmaB * Tc ** 4 * 4 * math.pi * (pc * Dist['distance_pc']) ** 2))  # /(4*math.pi*(Dist['distance_pc']*pc)**2)

        if verbose==True:
            print('Tc is',Tc)
            print('SigmaB*Tc**4 is',SigmaB*Tc**4)
            print('L is',L)
            print('Spec_factor is',Spec_factor)
        if processes is None:
            pool = mp.Pool(processes=8)
        else:
            print('I am using {0} cores in parallel, IMALEH!'.format(processes))
            pool = mp.Pool(processes=processes)
        if async ==True:
            resultx = [[Time[i],pool.apply_async(fluxes_para_w_Pyphot, args=(Spec_factor[i],Tc[i],redshift,Filter_vector,Ebv,filters_directory))] for i in range(np.shape(Time)[0])]
            #print(resultx)
            output = [np.array([p[0],p[1].get()[0]]) for p in resultx]
            results_unsorted = np.array(output)
            results= results_unsorted[np.argsort(results_unsorted,axis=0)[:,0]]
            pool.close()
        else:
            resultx =[np.array([Time[i],pool.apply(fluxes_para_w_Pyphot, args=(Spec_factor[i],Tc[i],redshift,Filter_vector,Ebv,filters_directory))[0]]) for i in range(np.shape(Time)[0])]
            results=np.array(resultx)

        '''
        for i,j in enumerate(Time):
            fluxes[i,:]=(1+redshift)**4*Spec_factor[i]*calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i]/(1+redshift), np.arange(1e-7, 3e-6, 1e-9)*(1+redshift), Filter_vector=Filter_vector, P_vector=None, Radius=None
                                                                                  , distance_pc=None,
                                     output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
                                     z=0, output_file=None,filters_directory=filters_directory)[:,3]

            #print('fluxes[i,:]',fluxes[i,:])
            #pdb.set_trace()
            # ALMOST THE SAME AS (R/D)**2*B_lambda
            #fluxes[i, :]=calc_black_body_flux_filters.calc_black_body_flux_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), Filter_vector=Filter_vector, P_vector=None, Radius=R[i]
            #                                                                      , distance_pc=Dist['distance_pc'],
            #                         output_txt=False, output_plot=False, lib=None, show_plots=False, Ebv=Ebv, R_ext=None,
            #                         z=redshift, output_file=None)[:,3]

            #pdb.set_trace()
            #magnitudes[i,:]=calc_black_body_mag_filters.calc_black_body_mag_filters(Tc[i], np.arange(1e-7, 3e-6, 1e-9), 'AB', Filter_vector=Filter_vector, P_vector=None, Radius=R[i],
            #                            distance_pc=Dist['distance_pc'], output_plot=False, output_txt=False, show_plots=False, z=redshift, Ebv=Ebv,
            #                            mabs=False)[:,4]
            #print(Filter_vector)
            list_filters=[Filter_vector[s][1] for s in range(len(Filter_vector))]
            #print([Filter_vector[s][1] for s in range(len(Filter_vector))])
            #print(fluxes[i,:])
            #print(Time[i]*np.ones(np.shape(Filter_vector)[0]))
            #pdb.set_trace()
            if isinstance(fluxfile_block, np.ndarray) is True:
                fluxfile_block=np.vstack((fluxfile_block,np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)))
            else:
                fluxfile_block=np.array(list(zip(np.ndarray.astype(Time[i]*np.ones(np.shape(Filter_vector)[0]),float),np.ndarray.astype(fluxes[i,:],float),list_filters)),dtype=object)
        if output_flux is not None:
            np.savetxt(output_flux,fluxfile_block,fmt='%.18e,%.18e,%s',header='jd,flux,filter',delimiter=',',comments='')
        '''
        return L,Tc,R,td,magnitudes,tmin,tmax,topac,t_tr,tdelta,results,Tph_RW,L_RW,Spec_factor
    else:
        return L,Tc, R, td, tmin, tmax, topac, t_tr, tdelta,Tph_RW,L_RW

