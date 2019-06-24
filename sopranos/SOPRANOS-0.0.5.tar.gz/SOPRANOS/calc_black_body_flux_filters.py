#! //anaconda/bin/python

"""*******************************************************
This code calcultes the magnitude of a black_body in a given filter, given its temperature T, Radius and distance
******************************************************"""
__author__ = 'maayanesoumagnac'

#print(__doc__)

import numpy as np
from . import get_filter
import pdb
from . import black_body_flux_density
from . import distances_conversions
import pylab
import pyphot
import os
import logging
import shutil


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calc_black_body_flux_filters_w_Pyphot(Temp,wavelengths,filters_directory=None,Filter_vector=None,P_vector=None,Radius=None,distance_pc=None,output_txt=True,output_plot=True,lib=None,show_plots=False,Ebv=None,R_ext=None,z=0,output_file=None,fast=False):
    """This code calcultes the synthetic flux \bar{f}(P) of a black_body in a given filter P (filter family and filter name), given its temperature T, Radius and distance.
    Input  :- Temperature [K]
            - wavelengths [m]
            - Filter vector: N-long array of of arrays [[filter family, filtername],[filter family, filtername],[filter family, filtername],...etc]
            the family and names are the ones provided by the pyphot library #FIX THERE IS A PROBBLEM IF FILTER VECTOR IS ONLY 1D
            - alternatively, you can give a N-long array [[filter family, filtername,P1],[filter family, filtername,P2],..,[filter family, filtername.PN]], where P are pyphot.Filter objects. This can help to speed up the code, e.g. if it's used in a mcmc
            - Radius in cm default is None
            - distance: distance of the blackbody in pc, default is 10 pc
            - output_txt: if True (default), create an output file with txt files. In codes using this function
            many tims (e.g. fit_black_body_fluxfiters.py), you may want to set it to false.
            - output_plot: if True (default), create an output file with txt files. In codes using this function
            in loops (e.g. fit_black_body_fluxfiters.py), you may want to set it to false.
            - lib: library of filters in the same format as the pyphot library. If None, uses lib = pyphot.get_library().
            in codes using this function in loops (e.g. fit_black_body_fluxfiters.py), you may want to set lib = pyphot.get_library() outside of the loop.
            - CAREFULL! Ebv and z are exinctions and redshift to be APPLIED (not corrected) to a theoretical black boday before synthetic photometry is ran on it.
            i.e. the theoretical bb is extincted and redshifted by E abd z
    Output  :- N*4 array where each line is: [filter family, filtername,effective wavelength of P,\bar{f}(P)], f is in [erg/sec/cm^2/\AA ]
    Plots and output files: -plot of lambda_mean(P), \bar{f}(P)
	Tested : ?
	    By : Maayane T. Soumagnac Nov 2016
	   URL :
	Example: sun_flux=calc_black_body_flux_filters.calc_black_body_flux_filters(T,wavelengths,Filter_vector,distance=4.8481e-6,Radius=1.)
	Link to other functions: it is the same to do calc_anyspectrum_flux_filters(black_body_flux_density) and calc_black_body_flux_filters
	Reliable:
	Reference: my notes in observationnal astronomy, pargraph on synthetic photometry,
	            //anaconda/lib/python2.7/site-packages/pyphot/phot.py Filter class
	 TO DO: give an option for the speed: decrease the length of TempVec, give the spec units as options"""
    #print('I am running calc_blacl_body_flux_filter'
    if Filter_vector is None and P_vector is None:
        print('ERROR: you need to define either Filter_vector or P_vector')
        pdb.set_trace()
    if output_txt==True:
        if os.path.exists('./outputs_from_calc_black_body_flux_filters_function'):
            logger.info('output_path/txt_files did exist, I am removing it and creating a new one')
            shutil.rmtree('./outputs_from_calc_black_body_flux_filters_function')
        else:
            logger.info('the output file file did not exist yet. I am creating it now')
        os.makedirs('./outputs_from_calc_black_body_flux_filters_function')
    #wavelengths = wavelengths*(z + 1)
    #print('wavelengths are',wavelengths)
    if Radius is not None:
        #print('Radius is not none'
        #print('Raius is {0}'.format(Radius)
        #pdb.set_trace()
        Radius=distances_conversions.cm_to_solar_radius(Radius)
    #if Ebv is None:
    #    black_body_spectrum=black_body_flux_density.black_body_flux_density(Temp,wavelengths,'P',distance_pc=distance_pc,Radius=Radius)[2]/(z+1)#,Ebv=Ebv)[2]# in erg/sec/cm^2/Ang
    #print(' black_body_spectrum is {0}'.format(black_body_spectrum)
    #else:
    #    black_body_spectrum =black_body_flux_density.black_body_flux_density(Temp, wavelengths, 'P', distance_pc=distance_pc, Radius=Radius,Ebv=Ebv)[2]/(z+1)  # in erg/sec/cm^2/Ang
    black_body_spectrum = \
    black_body_flux_density.black_body_flux_density(Temp, wavelengths, 'P', distance_pc=distance_pc, Radius=Radius,
                                                    Ebv=Ebv,R_ext=R_ext,redshift=z)[2]   # in erg/sec/cm^2/Ang
    wavelengths_AA=black_body_spectrum[:,0]*1e10

    if lib is None:
        lib = pyphot.get_library()
        #print("Library contains: ", len(lib), " filters")
    else:
        #print('the library was defined outside'
        lib=lib

    wavelengths_AA = wavelengths_AA.astype(float)


    if Filter_vector is not None:
        #print('filters_directory:',filters_directory)
        #print('Filter_vector is',Filter_vector)
        [P, wav]=get_filter.make_filter_object_w_Pyphot(Filter_vector,filters_directory=filters_directory)
        #print('P is',P)
        #pdb.set_trace()
        output_array = np.empty([np.shape(Filter_vector)[0], 4], dtype=object)
        string = np.empty(np.shape(Filter_vector)[0], dtype=object)
        for i,j in enumerate(Filter_vector):
            '''
            #print j
            if j[0].lower()=='ptf_p48':
               if j[1].lower()=='r':
                   print('You gave the R filter of the PTF_P48 family')
                   Transmission=np.genfromtxt('/Users/maayanesoumagnac/Maayane_Astro_python_library/data/filters/P48_R_T.rtf',delimiter=None)
                   P=pyphot.Filter(Transmission[:,0], Transmission[:,1], name='PTF_P48_R', dtype='photon', unit='Angstrom')
            elif j[0].lower() == 'galex':
                if j[1].lower() == 'galex_nuv':
                    print('You gave the nuv filter of the galex family')
                    Transmission = np.genfromtxt(
                        '/Users/maayanesoumagnac/Maayane_Astro_python_library/data/filters//GALEX_NUV.dat',
                        delimiter=None)
                    P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='GALEX_NUV', dtype='photon',
                                      unit='Angstrom')

            else:
                f = lib.find(j[0].lower())#filter family
                P = lib[j[1]]#filter name

            # this calculates \bar{f}(P) through through filter P. wavelength must be given in the same units as wavelength units defined in filters
#            print('wavelengths in AA are',wavelengths_AA

#            print('the bb spectrum is', black_body_spectrum[:, 1]
            #pdb.set_trace()
            '''
            fluxes = P['filter_object'][i].get_flux(black_body_spectrum[:, 0]*1e10, black_body_spectrum[:, 1])
            if fast !=True:
                output_array[i,0]=np.array(Filter_vector)[i,0]
                output_array[i,1]=np.array(Filter_vector)[i,1]
                output_array[i,2] = P['filter_object'][i].cl.item()#le eff_wl de Eran (auquel je veux pouvoir comparer) est le cl de pyphot
                output_array[i,3]=fluxes
                string[i] = output_array[i, 1] + '\n' + r'$(\lambda_c=$' + str(round(output_array[i, 2], 3)) + '$)$'
            else:
                print('Fast is true')
                output_array[i, 3] = fluxes

            #if output_txt == True:

    else:
        #print('P vector is',P_vector)
        output_array = np.empty([np.shape(P_vector)[0], 4], dtype=object)
        string = np.empty(np.shape(P_vector)[0], dtype=object)
        for i, fil in enumerate(P_vector):
            fluxes = P_vector[i,2].get_flux(black_body_spectrum[:, 0]*1e10, black_body_spectrum[:, 1])
            #print('fluxes are',fluxes)
            #print fluxes
            output_array[i, 0] = P_vector[i, 0]
            output_array[i, 1] = P_vector[i, 1]
            output_array[i, 2] = P_vector[i, 2].cl.item()# le eff_wl de Eran (auquel je veux pouvoir comparer) est le cl de pyphot
            #output_array[i, 2] = P_vector[i, 2].leff.item()
            #pdb.set_trace()
            output_array[i, 3] = fluxes
            string[i] = output_array[i, 1] + '\n' + r'$(\lambda_c=$' + str(round(output_array[i, 2], 3)) + '$)$'
            #if output_txt == True:
            #    np.savetxt('./outputs_from_calc_black_body_flux_filters_function/output_array.txt', output_array,
            #               header=r'Filter family, Filter name, effective wavelength $(\AA)$, flux $\bar{f}(P)$ $[erg/sec/cm^2/\AA ]$',
            #               fmt="%s")
    if output_txt==True:
        print('I am saving')
        np.savetxt('./outputs_from_calc_black_body_flux_filters_function/output_array.txt', output_array,header=r'Filter family, Filter name, effective wavelength $(\AA)$, flux $\bar{f}(P)$ $[erg/sec/cm^2/\AA ]$',fmt="%s")
    if output_plot==True:
        print('I am plotting')
        pylab.figure()
        pylab.plot(output_array[:,2], output_array[:,3], 'ro', label='synthetic flux through input filters')
        pylab.plot(black_body_spectrum[:,0]*1e10,black_body_spectrum[:,1],'b-', label='theoretical black body with input T ans R')
        #if Ebv != None:
        #    pylab.plot(output_array[:, 2], output_array[:,4], 'mo', label='without extinction')
            #pylab.plot(1 / wavelengths_allen, AlA_Alen, 'b', label='Allen')
        pylab.xlabel(r'Central wavelength of filters ($\AA$)')
        pylab.ylabel(r'flux $\bar{f}(P)$, $[erg/sec/cm^2/\AA ]$')
        pylab.title('result of calc_blac_body_flux_filters.py')
        labels = string[:]
        pylab.xticks(output_array[:,2],labels)#,rotation='vertical')
        pylab.legend(loc=4)
        if output_file is not None:
            pylab.savefig(output_file+'/spectrum_plot_from_calc_black_body_flux_filters.pdf', facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format='pdf', transparent=False, bbox_inches=None,
                  pad_inches=0.1)
    if show_plots==True:
        pylab.show()
    #print('output array is',output_array)
    return output_array #N*4 array where each line is: [filter family, filtername,effective wavelength of P,\bar{f}(P)], f is in [erg/sec/cm^2/\AA ]

def calc_black_body_flux_filters(Temp,wavelengths,filters_dic=None,Filter_vector=None,P_vector=None,Radius=None,distance_pc=None,output_txt=True,output_plot=True,lib=None,show_plots=False,Ebv=None,R_ext=None,z=0,output_file=None,fast=False,verbose=False):
    """This code calcultes the synthetic flux \bar{f}(P) of a black_body in a given filter P (filter family and filter name), given its temperature T, Radius and distance.
    Input  :- Temperature [K]
            - wavelengths [m]
            - Filter vector: N-long array of of arrays [[filter family, filtername],[filter family, filtername],[filter family, filtername],...etc]
            the family and names are the ones provided by the pyphot library #FIX THERE IS A PROBBLEM IF FILTER VECTOR IS ONLY 1D
            - alternatively, you can give a N-long array [[filter family, filtername,P1],[filter family, filtername,P2],..,[filter family, filtername.PN]], where P are pyphot.Filter objects. This can help to speed up the code, e.g. if it's used in a mcmc
            - Radius in cm default is None
            - distance: distance of the blackbody in pc, default is 10 pc
            - output_txt: if True (default), create an output file with txt files. In codes using this function
            many tims (e.g. fit_black_body_fluxfiters.py), you may want to set it to false.
            - output_plot: if True (default), create an output file with txt files. In codes using this function
            in loops (e.g. fit_black_body_fluxfiters.py), you may want to set it to false.
            - lib: library of filters in the same format as the pyphot library. If None, uses lib = pyphot.get_library().
            in codes using this function in loops (e.g. fit_black_body_fluxfiters.py), you may want to set lib = pyphot.get_library() outside of the loop.
            - CAREFULL! Ebv and z are exinctions and redshift to be APPLIED (not corrected) to a theoretical black boday before synthetic photometry is ran on it.
            i.e. the theoretical bb is extincted and redshifted by E abd z
    Output  :- N*4 array where each line is: [filter family, filtername,effective wavelength of P,\bar{f}(P)], f is in [erg/sec/cm^2/\AA ]
    Plots and output files: -plot of lambda_mean(P), \bar{f}(P)
	Tested : ?
	    By : Maayane T. Soumagnac Nov 2016
	   URL :
	Example: sun_flux=calc_black_body_flux_filters.calc_black_body_flux_filters(T,wavelengths,Filter_vector,distance=4.8481e-6,Radius=1.)
	Link to other functions: it is the same to do calc_anyspectrum_flux_filters(black_body_flux_density) and calc_black_body_flux_filters
	Reliable:
	Reference: my notes in observationnal astronomy, pargraph on synthetic photometry,
	            //anaconda/lib/python2.7/site-packages/pyphot/phot.py Filter class
	 TO DO: give an option for the speed: decrease the length of TempVec, give the spec units as options"""
    #print('I am running calc_blacl_body_flux_filter'
    if Filter_vector is None and P_vector is None:
        print('ERROR: you need to define either Filter_vector or P_vector')
        pdb.set_trace()
    if output_txt==True:
        if os.path.exists('./outputs_from_calc_black_body_flux_filters_function'):
            logger.info('output_path/txt_files did exist, I am removing it and creating a new one')
            shutil.rmtree('./outputs_from_calc_black_body_flux_filters_function')
        else:
            logger.info('the output file file did not exist yet. I am creating it now')
        os.makedirs('./outputs_from_calc_black_body_flux_filters_function')
    #wavelengths = wavelengths*(z + 1)
    #print('wavelengths are',wavelengths)
    if Radius is not None:
        #print('Radius is not none'
        #print('Raius is {0}'.format(Radius)
        #pdb.set_trace()
        Radius=distances_conversions.cm_to_solar_radius(Radius)
    #if Ebv is None:
    #    black_body_spectrum=black_body_flux_density.black_body_flux_density(Temp,wavelengths,'P',distance_pc=distance_pc,Radius=Radius)[2]/(z+1)#,Ebv=Ebv)[2]# in erg/sec/cm^2/Ang
    #print(' black_body_spectrum is {0}'.format(black_body_spectrum)
    #else:
    #    black_body_spectrum =black_body_flux_density.black_body_flux_density(Temp, wavelengths, 'P', distance_pc=distance_pc, Radius=Radius,Ebv=Ebv)[2]/(z+1)  # in erg/sec/cm^2/Ang
    black_body_spectrum = \
    black_body_flux_density.black_body_flux_density(Temp, wavelengths, 'P', distance_pc=distance_pc, Radius=Radius,
                                                    Ebv=Ebv,R_ext=R_ext,redshift=z)[2]   # in erg/sec/cm^2/Ang

    #print('black_body_spectrum is',black_body_spectrum)
    #pdb.set_trace()

    wavelengths_AA=black_body_spectrum[:,0]*1e10

    '''
    if lib is None:
        lib = pyphot.get_library()
        #print("Library contains: ", len(lib), " filters")
    else:
        #print('the library was defined outside'
        lib=lib
    '''

    wavelengths_AA = wavelengths_AA.astype(float)


    if Filter_vector is not None:
        #print('filters_directory:',filters_directory)
        #print('Filter_vector is',Filter_vector)
        [P, wav]=get_filter.make_filter_object(Filter_vector,dic_transmissions=filters_dic)
        #print('P is',P)
        #pdb.set_trace()
        output_array = np.empty([np.shape(Filter_vector)[0], 4], dtype=object)
        string = np.empty(np.shape(Filter_vector)[0], dtype=object)
        for i,j in enumerate(Filter_vector):
            '''
            #print j
            if j[0].lower()=='ptf_p48':
               if j[1].lower()=='r':
                   print('You gave the R filter of the PTF_P48 family')
                   Transmission=np.genfromtxt('/Users/maayanesoumagnac/Maayane_Astro_python_library/data/filters/P48_R_T.rtf',delimiter=None)
                   P=pyphot.Filter(Transmission[:,0], Transmission[:,1], name='PTF_P48_R', dtype='photon', unit='Angstrom')
            elif j[0].lower() == 'galex':
                if j[1].lower() == 'galex_nuv':
                    print('You gave the nuv filter of the galex family')
                    Transmission = np.genfromtxt(
                        '/Users/maayanesoumagnac/Maayane_Astro_python_library/data/filters//GALEX_NUV.dat',
                        delimiter=None)
                    P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='GALEX_NUV', dtype='photon',
                                      unit='Angstrom')

            else:
                f = lib.find(j[0].lower())#filter family
                P = lib[j[1]]#filter name

            # this calculates \bar{f}(P) through through filter P. wavelength must be given in the same units as wavelength units defined in filters
#            print('wavelengths in AA are',wavelengths_AA

#            print('the bb spectrum is', black_body_spectrum[:, 1]
            #pdb.set_trace()
            '''
            fluxes = P['filter_object'][i].get_flux(black_body_spectrum[:, 0]*1e10, black_body_spectrum[:, 1],verbose=verbose)
            if fast !=True:
                output_array[i,0]=np.array(Filter_vector)[i,0]
                output_array[i,1]=np.array(Filter_vector)[i,1]
                output_array[i,2] = P['filter_object'][i].cl()#le eff_wl de Eran (auquel je veux pouvoir comparer) est le cl de pyphot
                output_array[i,3]=fluxes
                string[i] = output_array[i, 1] + '\n' + r'$(\lambda_c=$' + str(round(output_array[i, 2], 3)) + '$)$'
            else:
                print('Fast is true')
                output_array[i, 3] = fluxes

            #if output_txt == True:

    else:
        #print('P vector is',P_vector)
        output_array = np.empty([np.shape(P_vector)[0], 4], dtype=object)
        string = np.empty(np.shape(P_vector)[0], dtype=object)
        for i, fil in enumerate(P_vector):
            fluxes = P_vector[i,2].get_flux(black_body_spectrum[:, 0]*1e10, black_body_spectrum[:, 1],verbose=verbose)
            #print('fluxes are',fluxes)
            #print fluxes
            output_array[i, 0] = P_vector[i, 0]
            output_array[i, 1] = P_vector[i, 1]
            output_array[i, 2] = P_vector[i, 2].cl.item()# le eff_wl de Eran (auquel je veux pouvoir comparer) est le cl de pyphot
            #output_array[i, 2] = P_vector[i, 2].leff.item()
            #pdb.set_trace()
            output_array[i, 3] = fluxes
            string[i] = output_array[i, 1] + '\n' + r'$(\lambda_c=$' + str(round(output_array[i, 2], 3)) + '$)$'
            #if output_txt == True:
            #    np.savetxt('./outputs_from_calc_black_body_flux_filters_function/output_array.txt', output_array,
            #               header=r'Filter family, Filter name, effective wavelength $(\AA)$, flux $\bar{f}(P)$ $[erg/sec/cm^2/\AA ]$',
            #               fmt="%s")
    if output_txt==True:
        print('I am saving')
        np.savetxt('./outputs_from_calc_black_body_flux_filters_function/output_array.txt', output_array,header=r'Filter family, Filter name, effective wavelength $(\AA)$, flux $\bar{f}(P)$ $[erg/sec/cm^2/\AA ]$',fmt="%s")
    if output_plot==True:
        print('I am plotting')
        pylab.figure()
        pylab.plot(output_array[:,2], output_array[:,3], 'ro', label='synthetic flux through input filters')
        pylab.plot(black_body_spectrum[:,0]*1e10,black_body_spectrum[:,1],'b-', label='theoretical black body with input T ans R')
        #if Ebv != None:
        #    pylab.plot(output_array[:, 2], output_array[:,4], 'mo', label='without extinction')
            #pylab.plot(1 / wavelengths_allen, AlA_Alen, 'b', label='Allen')
        pylab.xlabel(r'Central wavelength of filters ($\AA$)')
        pylab.ylabel(r'flux $\bar{f}(P)$, $[erg/sec/cm^2/\AA ]$')
        pylab.title('result of calc_blac_body_flux_filters.py')
        labels = string[:]
        pylab.xticks(output_array[:,2],labels)#,rotation='vertical')
        pylab.legend(loc=4)
    if output_file is not None:
        pylab.savefig(output_file+'/spectrum_plot_from_calc_black_body_flux_filters.pdf', facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format='pdf', transparent=False, bbox_inches=None,
                  pad_inches=0.1)
    if show_plots==True:
        pylab.show()
    #print('output array is',output_array)
    return output_array #N*4 array where each line is: [filter family, filtername,effective wavelength of P,\bar{f}(P)], f is in [erg/sec/cm^2/\AA ]

