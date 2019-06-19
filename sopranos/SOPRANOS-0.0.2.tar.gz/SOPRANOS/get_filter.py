#! //anaconda/bin/python

import pdb
import numpy as np
import pyphot
from scipy.integrate import trapz
# It would make sens to reorganize this as a class Filter, with attributes: family_name, name,
# and methods effective wavelength, tranmission curve, filter half width, see for example Eran's get_filter

def filter_effective_wavelength(filter_family,filtername):
    """Description: inspired by Eran's finction of the same name. Given a filter name, finds the effective wavelength in microns
    Input  :-Filter family among:
                Johnson, sdss, poss
            -Filter name among:
                Johnson: 'U','B','V','R','I','J','H','K' or in minuscules
                sdss: 'u','g','r','i','z'
                poss: 'O','E'
    Output  :-effective wavelength in microns (kind of a hybrid between wavelength-weighted average and frequency-weighted average. See reference)
    Reference: Fukugita et al. 1996, Table 2a.
    Tested : ?
    By : Maayane T. Soumagnac Nov 2016
    URL :
    Example:
    Reliable:  """
    if filter_family.lower()=='sdss':
        if filtername.lower()=='u':
            W=0.3557
        elif filtername.lower()=='g':
            W=0.4825
        elif filtername.lower()=='r':
            W=0.6261
        elif filtername.lower()=='i':
            W=0.7672
        elif filtername.lower()=='z':
            W=0.9097
        else: print('unknown SDSS filter name')
    elif filter_family.lower()=='johnson':
        if filtername.lower()=='u':
            W=0.367#?
        elif filtername.lower()=='b':
            W=0.436#?
        elif filtername.lower()=='v':
            W=0.545
        elif filtername.lower()=='r':
            W=0.638
        elif filtername.lower()=='i':
            W=0.797
        elif filtername.lower()=='j':
            W=1.220
        elif filtername.lower()=='h':
            W=1.630
        elif filtername.lower()=='k':
            W=2.190
        else: print('unknown Johnson filter name')
    elif filter_family.lower()=='poss':
        if filtername.lower()=='o':
            W=0.420
        elif filtername.lower()=='e':
            W=0.640
    else:
        print('unknown family filter name. You can choose among [sdss, johnson, poss] and it is case insensitive')
        pdb.set_trace()
    return W

def make_filter_object_w_Pyphot(Filter_vector, filters_directory, central=True, verbose=False):
    """Description: from a filter vector where each element is a couple [filter family,filter name], create a filter object P as in pyphoy
        Input  :- a filter vector: can be given in two shapes:

        OPTION 1:
        Filter_vector = np.empty([2, 2], dtype=object)
        Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
        Filter_vector[1]=[str('ptf_p48'),str('r_p48')]

        OPTION 2:
        Filter_vector_2=[['swift','UVW1'],['ztf_p48','p48_r']]

                - central. If true, gives pyphot .cl wavelength, which corresponds to Eran's AstFilter.get('family','band').eff_wl
                            else, gives phyphot .eff wavelength, which I am not sure what it is..
        Output :- a dictionnary P where
            P['filter_object'] is a list  with all the filters,
            P['filtername'] is a numpy array with all the filters names
            P['filter_family'] is a numpy array with all the families
        with the corresponding data
        Tested : ?
             By : Maayane T. Soumagnac Nov 2016
            URL :
        Example:Filter_vector = np.empty([2, 2], dtype=object)
                Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
                Filter_vector[1]=[str('ptf_p48'),str('r')]
                [P, wav]=make_filter_object(Filter_vector)
        Reliable:  """
    wavelength_filter_effective = dict()  # np.empty(np.shape(Filter_vector)[0])
    wavelength_filter_central = dict()
    wavelength_filter_pivot = dict()
    P_vector = dict()
    #print('Filter_vector is', Filter_vector)
    #print(isinstance(Filter_vector, (list,)))
    # pdb.set_trace()
    if isinstance(Filter_vector, (list,)):
        Filter_vectorx = np.empty([len(Filter_vector), 2], dtype=object)
        for i, j in enumerate(Filter_vector):
            Filter_vectorx[i, 0] = Filter_vector[i][0]
            Filter_vectorx[i, 1] = Filter_vector[i][1]
        P_vector['filter_family'] = Filter_vectorx[:, 0]
        P_vector['filter_name'] = Filter_vectorx[:, 1]
        P_vector['filter_object'] = []

    else:
        Filter_vectorx = Filter_vector
        P_vector['filter_family'] = Filter_vector[:, 0]
        P_vector['filter_name'] = Filter_vector[:, 1]
        P_vector['filter_object'] = []
    # print("P_vector['filter_object'] is",P_vector['filter_object'])
    # pdb.set_trace()
    for i, j in enumerate(Filter_vectorx):
        #print('j is', j)
        if j[0].lower() == 'ptf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                # if verbose == True:
                print('You gave the G filter of the PTF_P48 family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/PTF_G.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_G', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_p48':
                # if verbose==True:
                print('You gave the R filter of the PTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/P48_R_T.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_R', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'ztf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                if verbose == True:
                    print('You gave the G filter of the ztf_P48 family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/ZTF_g_fromgithub_AA.txt', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_G', dtype='photon',
                                  unit='Angstrom')
                # print('P is',P)
                # pdb.set_trace()
            elif j[1].lower() == 'r_p48':
                if verbose == True:
                    print('You gave the R filter of the ZTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/ZTF_r_fromgithub_AA.txt', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_R', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_p48':
                if verbose == True:
                    print('You gave the I filter of the ZTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/ZTF_i_fromgithub_AA_reorder.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_I', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'swift':
            if j[1].lower() == 'uvw1':
                if verbose == True:
                    print('You gave the uvw1 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/Swift_UVW1.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW1', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvw2':
                if verbose == True:
                    print('You gave the uvw2 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_UVW2.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW2', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvm2':
                if verbose == True:
                    print('You gave the uvm2 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_UVM2.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVM2', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_swift':
                if verbose == True:
                    print('You gave the u filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_u.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_u', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_swift':
                if verbose == True:
                    print('You gave the v filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_V.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_V', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_swift':
                if verbose == True:
                    print('You gave the b filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_B.rtf', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_B', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'galex':
            if j[1].lower() == 'galex_nuv':
                if verbose == True:
                    print('You gave the nuv filter of the galex family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/GALEX_NUV.dat', delimiter=None)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='galex_nuv', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'sdss':
            if verbose == True:
                print('You gave the sdss family')
            # print(j[1].lower())
            if j[1].lower() == 'r_sdss':
                if verbose == True:
                    print('You gave the r filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_r.txt', delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='r_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'g_sdss':
                if verbose == True:
                    print('You gave the g filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_g.txt', delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='g_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_sdss':
                if verbose == True:
                    print('You gave the i filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_i.txt', delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='i_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_sdss':
                if verbose == True:
                    print('You gave the u filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_u.txt', delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='u_sdss', dtype='photon',
                                  unit='Angstrom')

            elif j[1].lower() == 'z_sdss':
                if verbose == True:
                    print('You gave the z filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/SDSS_z.txt', delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='z_sdss', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == '2mass':
            if verbose == True:
                print('You gave the 2MASS family')
                print(j[1].lower())
            if j[1].lower() == 'j_2mass':
                if verbose == True:
                    print('You gave the J filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/2MASS_J.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='2MASS_J', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'h_2mass':
                if verbose == True:
                    print('You gave the h filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/2MASS_H.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='h_2mass', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'k_2mass':
                if verbose == True:
                    print('You gave the k filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/2MASS_K.txt',
                    delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='k_2mass', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'cousin':
            if verbose == True:
                print('You gave the cousin family')
                # print(j[1].lower())
            if j[1].lower() == 'i_cousin':
                if verbose == True:
                    print('You gave the i filter of the cousin family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/cousin_i.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='i_counsin', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_cousin':
                if verbose == True:
                    print('You gave the r filter of the cousin family')
                Transmission = np.genfromtxt(filters_directory + '/cousin_r.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='r_cousin', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'johnson':
            if verbose == True:
                print('You gave the johnson family')
                print(j[1].lower())
            if j[1].lower() == 'u_johnson':
                if verbose == True:
                    print('You gave the u filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/johnson_u.txt',
                                             delimiter=',')
                # print('the shape of transission is',Transmission)
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='u_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_johnson':
                if verbose == True:
                    print('You gave the b filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/johnson_b.txt',
                                             delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='b_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_johnson':
                if verbose == True:
                    print('You gave the v filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/johnson_v.txt',
                    delimiter=',')
                P = pyphot.Filter(Transmission[:, 0], Transmission[:, 1], name='v_johnson', dtype='photon',
                                  unit='Angstrom')
        else:
            print('I HAVE NOT RECOGNIZE THE FILTER')
            lib = pyphot.get_library()
            f = lib.find(j[0].lower())  # filter family
            if verbose == True:
                for name in f:
                    lib[name].info(show_zeropoints=True)
            P = lib[j[1]]  # filter name
            # min_w=np.min(Transmission[:,0])
            # max_w=np.max(Transmission[:,0])
            # print(P_vector)
            # print('Filter_vector is',Filter_vector)
            # print('P is',P)
            # print("P_vector['filter_object'] is",P_vector['filter_object'])
            # if isinstance(P_vector['filter_object'],(list,)) is False:
            #   P_vector['filter_object']=[P_vector['filter_object']].append(P)
            # print("P_vector['filter_object'] is", P_vector['filter_object'])
            # print("P_vector['filter_name'] is", P_vector['filter_name'])
        if isinstance(P_vector['filter_object'], (list,)) is True:
            #print('oui, liste de longueur', len(P_vector['filter_object']))
            if len(P_vector['filter_object']) > 0:
                ##print('oui')
                # print('I am trying to append {0} to {1}'.format(P,P_vector['filter_object']))
                P_vector['filter_object'] = P_vector['filter_object'] + [P]
                P_vector['filter_name'] = P_vector['filter_name'] + [j[1].lower()]
                P_vector['filter_family'] = P_vector['filter_family'] + [j[0].lower()]
                # print('ca a marche?',P_vector['filter_object'])
            else:
                # print('faison une liste')
                P_vector['filter_object'] = [P]
                # print(P_vector['filter_object'])
                P_vector['filter_name'] = [j[1].lower()]
                P_vector['filter_family'] = [j[0].lower()]
                # pdb.set_trace()

                # print("P_vector['filter_object'] is",P_vector['filter_object'])
                # print("P_vector['filter_name'] is",P_vector['filter_name'])
                # print('i is',i)
        wavelength_filter_effective[P_vector['filter_name'][i]] = P.leff.item()
        wavelength_filter_central[P_vector['filter_name'][i]] = P.cl.item()
        # wavelength_filter_min[P_vector['filter_name'][i]]=np.min(Transmission[:,0])
        # wavelength_filter_max[P_vector['filter_name'][i]] = np.max(Transmission[:, 0])

        # if isinstance(Filter_vector, (list,)):
        # P_vector['filter_object']=P_vector['filter_object'][0]

        # print(P_vector)
        # print(P)
        # P_vector['filter_object'].append(P)
        # wavelength_filter_effective[P_vector['filter_name'][i]]=P.leff.item()
        # wavelength_filter_central[P_vector['filter_name'][i]]=P.cl.item()
        # if isinstance(Filter_vector, (list,)):
        #    P_vector['filter_object']=P_vector['filter_object'][0]

    # print('Filter_vector was', Filter_vector)
    # print(' and P_vector is', P_vector)
    # pdb.set_trace()

    if central == True:
        return P_vector, wavelength_filter_central  # same as Eran eff_wl
    else:
        return P_vector, wavelength_filter_effective

class filterObj_w_Pyphot(object):#create a filterObj similar to Eran's definition
    def __init__(self, filtername, instrumentname, path_to_filters):
        self.family = instrumentname
        self.band = filtername
        self.path_to_filters = path_to_filters
        if self.family=='ztf_p48':
            if self.band.lower() == 'g_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/ZTF_g_fromgithub_AA.txt', delimiter=None)
                self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_G', dtype='photon',
                                       unit='Angstrom')
            elif self.band.lower() == 'r_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/ZTF_r_fromgithub_AA.txt', delimiter=None)
                self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_R', dtype='photon',
                                       unit='Angstrom')
        elif self.family=='ptf_p48':
            if self.band.lower() == 'g_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/PTF_G.rtf', delimiter=',')
                self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_G', dtype='photon',
                                       unit='Angstrom')
            elif self.band.lower() == 'r_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/P48_R_T.rtf', delimiter=',')
                self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_R', dtype='photon',
                                       unit='Angstrom')
        elif self.band.lower() == 'uvw1':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVW1.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW1', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'uvw2':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVW2.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW2', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'uvm2':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVM2.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW2', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_u.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_u', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'v_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_V.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_v', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'b_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_B.rtf', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='Swift_B', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'galex_nuv':
            self.T = np.genfromtxt(
                path_to_filters + '/GALEX_NUV.dat', delimiter=None)
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='galex_nuv', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'r_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_r.txt', delimiter=',')
            #print('np.shape(self.T) is',np.shape(self.T))

            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='r_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'g_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_g.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='g_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'i_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_i.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='i_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_u.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='u_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'z_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_z.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='z_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'j_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_J.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='j_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'h_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_H.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='h_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'k_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_K.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='k_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'i_cousin':
            self.T = np.genfromtxt(
                path_to_filters + '/cousin_i.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='i_cousin', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'r_cousin':
            self.T = np.genfromtxt(
                path_to_filters + '/cousin_r.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='r_cousin', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_u.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='u_johnson', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'b_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_b.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='b_johnson', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'v_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_v.txt', delimiter=',')
            self.P = pyphot.Filter(self.T[:, 0], self.T[:, 1], name='v_johnson', dtype='photon',
                                   unit='Angstrom')

        else:
            print('I HAVE NOT RECOGNIZE THE FILTER')
            lib = pyphot.get_library()
            f = lib.find(self.band.lower())  # filter family
            for name in f:
                lib[name].info(show_zeropoints=True)
            P = lib[self.band.lower()]  # filter name

    def min_wl(self):
        min_wl = np.min(self.T[:, 0])
        return min_wl

    def max_wl(self):
        max_wl = np.max(self.T[:, 0])
        return max_wl

    def eff_wl(self):
        return self.P.leff.item()

    def cl_wl(self):
        return self.P.cl.item()

def make_filter_object_no_dic(Filter_vector, filters_directory, central=True, verbose=False):
    """Description: from a filter vector where each element is a couple [filter family,filter name], create a filter object P as in pyphoy
        Input  :- a filter vector: can be given in two shapes:

        OPTION 1:
        Filter_vector = np.empty([2, 2], dtype=object)
        Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
        Filter_vector[1]=[str('ptf_p48'),str('r_p48')]

        OPTION 2:
        Filter_vector_2=[['swift','UVW1'],['ztf_p48','p48_r']]

                - central. If true, gives pyphot .cl wavelength, which corresponds to Eran's AstFilter.get('family','band').eff_wl
                            else, gives phyphot .eff wavelength, which I am not sure what it is..
        Output :- a dictionnary P where
            P['filter_object'] is a list  with all the filters,
            P['filtername'] is a numpy array with all the filters names
            P['filter_family'] is a numpy array with all the families
        with the corresponding data
        Tested : ?
             By : Maayane T. Soumagnac Nov 2016
            URL :
        Example:Filter_vector = np.empty([2, 2], dtype=object)
                Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
                Filter_vector[1]=[str('ptf_p48'),str('r')]
                [P, wav]=make_filter_object(Filter_vector)
        Reliable:  """
    wavelength_filter_effective = dict()  # np.empty(np.shape(Filter_vector)[0])
    wavelength_filter_central = dict()
    wavelength_filter_pivot = dict()
    P_vector = dict()
    #print('Filter_vector is', Filter_vector)
    #print(isinstance(Filter_vector, (list,)))
    # pdb.set_trace()
    if isinstance(Filter_vector, (list,)):
        Filter_vectorx = np.empty([len(Filter_vector), 2], dtype=object)
        for i, j in enumerate(Filter_vector):
            Filter_vectorx[i, 0] = Filter_vector[i][0]
            Filter_vectorx[i, 1] = Filter_vector[i][1]
        P_vector['filter_family'] = Filter_vectorx[:, 0]
        P_vector['filter_name'] = Filter_vectorx[:, 1]
        P_vector['filter_object'] = []

    else:
        Filter_vectorx = Filter_vector
        P_vector['filter_family'] = Filter_vector[:, 0]
        P_vector['filter_name'] = Filter_vector[:, 1]
        P_vector['filter_object'] = []
    # print("P_vector['filter_object'] is",P_vector['filter_object'])
    # pdb.set_trace()
    for i, j in enumerate(Filter_vectorx):
        #print('j is', j)
        if j[0].lower() == 'ptf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                # if verbose == True:
                print('You gave the G filter of the PTF_P48 family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/PTF_G.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_G', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_p48':
                # if verbose==True:
                print('You gave the R filter of the PTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/P48_R_T.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_R', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'ztf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                if verbose == True:
                    print('You gave the G filter of the ztf_P48 family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/ZTF_g_fromgithub_AA.txt', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_G', dtype='photon',
                                  unit='Angstrom')
                # print('P is',P)
                # pdb.set_trace()
            elif j[1].lower() == 'r_p48':
                if verbose == True:
                    print('You gave the R filter of the ZTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/ZTF_r_fromgithub_AA.txt', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_R', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_p48':
                if verbose == True:
                    print('You gave the I filter of the ZTF_P48 family')
                Transmission = np.genfromtxt(filters_directory + '/ZTF_i_fromgithub_AA_reorder.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_I', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'swift':
            if j[1].lower() == 'uvw1':
                if verbose == True:
                    print('You gave the uvw1 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/Swift_UVW1.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW1', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvw2':
                if verbose == True:
                    print('You gave the uvw2 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_UVW2.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW2', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvm2':
                if verbose == True:
                    print('You gave the uvm2 filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_UVM2.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVM2', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_swift':
                if verbose == True:
                    print('You gave the u filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_u.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_u', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_swift':
                if verbose == True:
                    print('You gave the v filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_V.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_V', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_swift':
                if verbose == True:
                    print('You gave the b filter of the swift family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/Swift_B.rtf', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_B', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'galex':
            if j[1].lower() == 'galex_nuv':
                if verbose == True:
                    print('You gave the nuv filter of the galex family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/GALEX_NUV.dat', delimiter=None)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='galex_nuv', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'sdss':
            if verbose == True:
                print('You gave the sdss family')
            # print(j[1].lower())
            if j[1].lower() == 'r_sdss':
                if verbose == True:
                    print('You gave the r filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_r.txt', delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='r_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'g_sdss':
                if verbose == True:
                    print('You gave the g filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_g.txt', delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='g_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_sdss':
                if verbose == True:
                    print('You gave the i filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_i.txt', delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='i_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_sdss':
                if verbose == True:
                    print('You gave the u filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/SDSS_u.txt', delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='u_sdss', dtype='photon',
                                  unit='Angstrom')

            elif j[1].lower() == 'z_sdss':
                if verbose == True:
                    print('You gave the z filter of the sdss family')
                # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/SDSS_z.txt', delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='z_sdss', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == '2mass':
            if verbose == True:
                print('You gave the 2MASS family')
                print(j[1].lower())
            if j[1].lower() == 'j_2mass':
                if verbose == True:
                    print('You gave the J filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/2MASS_J.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='2MASS_J', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'h_2mass':
                if verbose == True:
                    print('You gave the h filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/2MASS_H.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='h_2mass', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'k_2mass':
                if verbose == True:
                    print('You gave the k filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/2MASS_K.txt',
                    delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='k_2mass', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'cousin':
            if verbose == True:
                print('You gave the cousin family')
                # print(j[1].lower())
            if j[1].lower() == 'i_cousin':
                if verbose == True:
                    print('You gave the i filter of the cousin family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/cousin_i.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='i_counsin', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_cousin':
                if verbose == True:
                    print('You gave the r filter of the cousin family')
                Transmission = np.genfromtxt(filters_directory + '/cousin_r.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='r_cousin', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'johnson':
            if verbose == True:
                print('You gave the johnson family')
                print(j[1].lower())
            if j[1].lower() == 'u_johnson':
                if verbose == True:
                    print('You gave the u filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/johnson_u.txt',
                                             delimiter=',')
                # print('the shape of transission is',Transmission)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='u_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_johnson':
                if verbose == True:
                    print('You gave the b filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(filters_directory + '/johnson_b.txt',
                                             delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='b_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_johnson':
                if verbose == True:
                    print('You gave the v filter of the johnson family')
                    # pdb.set_trace()
                Transmission = np.genfromtxt(
                    filters_directory + '/johnson_v.txt',
                    delimiter=',')
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='v_johnson', dtype='photon',
                                  unit='Angstrom')
        else:
            print('I HAVE NOT RECOGNIZE THE FILTER')
            pdb.set_trace()
            #lib = pyphot.get_library()
            #f = lib.find(j[0].lower())  # filter family
            #if verbose == True:
            #    for name in f:
            #        lib[name].info(show_zeropoints=True)
            #P = lib[j[1]]  # filter name
            # min_w=np.min(Transmission[:,0])
            # max_w=np.max(Transmission[:,0])
            # print(P_vector)
            # print('Filter_vector is',Filter_vector)
            # print('P is',P)
            # print("P_vector['filter_object'] is",P_vector['filter_object'])
            # if isinstance(P_vector['filter_object'],(list,)) is False:
            #   P_vector['filter_object']=[P_vector['filter_object']].append(P)
            # print("P_vector['filter_object'] is", P_vector['filter_object'])
            # print("P_vector['filter_name'] is", P_vector['filter_name'])
        if isinstance(P_vector['filter_object'], (list,)) is True:
            #print('oui, liste de longueur', len(P_vector['filter_object']))
            if len(P_vector['filter_object']) > 0:
                ##print('oui')
                # print('I am trying to append {0} to {1}'.format(P,P_vector['filter_object']))
                P_vector['filter_object'] = P_vector['filter_object'] + [P]
                P_vector['filter_name'] = P_vector['filter_name'] + [j[1].lower()]
                P_vector['filter_family'] = P_vector['filter_family'] + [j[0].lower()]
                # print('ca a marche?',P_vector['filter_object'])
            else:
                # print('faison une liste')
                P_vector['filter_object'] = [P]
                # print(P_vector['filter_object'])
                P_vector['filter_name'] = [j[1].lower()]
                P_vector['filter_family'] = [j[0].lower()]
                # pdb.set_trace()

                # print("P_vector['filter_object'] is",P_vector['filter_object'])
                # print("P_vector['filter_name'] is",P_vector['filter_name'])
                # print('i is',i)
        #wavelength_filter_effective[P_vector['filter_name'][i]] = P.leff.item()
        wavelength_filter_central[P_vector['filter_name'][i]] = P.cl()
        # wavelength_filter_min[P_vector['filter_name'][i]]=np.min(Transmission[:,0])
        # wavelength_filter_max[P_vector['filter_name'][i]] = np.max(Transmission[:, 0])

        # if isinstance(Filter_vector, (list,)):
        # P_vector['filter_object']=P_vector['filter_object'][0]

        # print(P_vector)
        # print(P)
        # P_vector['filter_object'].append(P)
        # wavelength_filter_effective[P_vector['filter_name'][i]]=P.leff.item()
        # wavelength_filter_central[P_vector['filter_name'][i]]=P.cl.item()
        # if isinstance(Filter_vector, (list,)):
        #    P_vector['filter_object']=P_vector['filter_object'][0]

    # print('Filter_vector was', Filter_vector)
    # print(' and P_vector is', P_vector)
    # pdb.set_trace()

    if central == True:
        return P_vector, wavelength_filter_central  # same as Eran eff_wl
    else:
        return P_vector, wavelength_filter_effective

def dic_transmissions(filters_directory):
    #print('I am loading the dic')
    #pdb.set_trace()
    dic_transmissions={}
    dic_transmissions['ptf_g_p48']=np.genfromtxt(filters_directory + '/PTF_G.rtf', delimiter=None)
    dic_transmissions['ptf_r_p48']=np.genfromtxt(filters_directory + '/P48_R_T.rtf', delimiter=None)
    dic_transmissions['ztf_g_p48']=np.genfromtxt(filters_directory + '/ZTF_g_fromgithub_AA.txt', delimiter=None)
    dic_transmissions['ztf_r_p48']=np.genfromtxt(filters_directory + '/ZTF_r_fromgithub_AA.txt', delimiter=None)
    dic_transmissions['ztf_i_p48']=np.genfromtxt(filters_directory + '/ZTF_i_fromgithub_AA_reorder.txt',
                                             delimiter=None)
    dic_transmissions['uvw1_swift']=np.genfromtxt(filters_directory + '/Swift_UVW1.rtf', delimiter=None)
    dic_transmissions['uvw2_swift']=np.genfromtxt(
                    filters_directory + '/Swift_UVW2.rtf', delimiter=None)
    dic_transmissions['uvm2_swift'] =np.genfromtxt(
        filters_directory + '/Swift_UVM2.rtf', delimiter=None)
    dic_transmissions['u_swift']=np.genfromtxt(
        filters_directory + '/Swift_u.rtf', delimiter=None)
    dic_transmissions['v_swift'] =np.genfromtxt(
        filters_directory + '/Swift_V.rtf', delimiter=None)
    dic_transmissions['b_swift'] =np.genfromtxt(
        filters_directory + '/Swift_B.rtf', delimiter=None)
    dic_transmissions['nuv_galex']=np.genfromtxt(
                    filters_directory + '/GALEX_NUV.dat', delimiter=None)
    dic_transmissions['r_sdss']=np.genfromtxt(
        filters_directory + '/SDSS_r.txt', delimiter=',')
    dic_transmissions['z_sdss']=np.genfromtxt(filters_directory + '/SDSS_z.txt', delimiter=',')
    dic_transmissions['i_sdss'] = np.genfromtxt(
        filters_directory + '/SDSS_i.txt', delimiter=',')
    dic_transmissions['g_sdss'] = np.genfromtxt(
        filters_directory + '/SDSS_g.txt', delimiter=',')
    dic_transmissions['u_sdss'] = np.genfromtxt(
        filters_directory + '/SDSS_u.txt', delimiter=',')

    dic_transmissions['j_2mass'] =np.genfromtxt(filters_directory + '/2MASS_J.txt',
                  delimiter=',')
    dic_transmissions['h_2mass']=np.genfromtxt(filters_directory + '/2MASS_H.txt',
                  delimiter=',')
    dic_transmissions['k_2mass']=np.genfromtxt(
        filters_directory + '/2MASS_K.txt',
        delimiter=',')
    dic_transmissions['i_cousin']=np.genfromtxt(filters_directory + '/cousin_i.txt',
                  delimiter=',')
    dic_transmissions['r_cousin'] =np.genfromtxt(filters_directory + '/cousin_r.txt',
                  delimiter=',')
    dic_transmissions['u_johnson']=np.genfromtxt(filters_directory + '/johnson_u.txt',
                  delimiter=',')
    dic_transmissions['b_johnson']=np.genfromtxt(filters_directory + '/johnson_b.txt',
                  delimiter=',')
    dic_transmissions['v_johnson'] =np.genfromtxt(
        filters_directory + '/johnson_v.txt',
        delimiter=',')
    return dic_transmissions

def make_filter_object(Filter_vector, dic_transmissions=None, central=True, verbose=False,filters_directory=None):
    """Description: from a filter vector where each element is a couple [filter family,filter name], create a filter object P as in pyphoy
        Input  :- a filter vector: can be given in two shapes:

        OPTION 1:
        Filter_vector = np.empty([2, 2], dtype=object)
        Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
        Filter_vector[1]=[str('ptf_p48'),str('r_p48')]

        OPTION 2:
        Filter_vector_2=[['swift','UVW1'],['ztf_p48','p48_r']]
                - dic tranmission: a dictionnary where all the transmission curves have been loaded as nparrays
                - central. If true, gives pyphot .cl wavelength, which corresponds to Eran's AstFilter.get('family','band').eff_wl
                            else, gives phyphot .eff wavelength, which I am not sure what it is..
        Output :- a dictionnary P where
            P['filter_object'] is a list  with all the filters,
            P['filtername'] is a numpy array with all the filters names
            P['filter_family'] is a numpy array with all the families
        with the corresponding data
        Tested : ?
             By : Maayane T. Soumagnac Nov 2016
            URL :
        Example:Filter_vector = np.empty([2, 2], dtype=object)
                Filter_vector[0] = [str('GALEX'), str('GALEX_NUV')]
                Filter_vector[1]=[str('ptf_p48'),str('r')]
                [P, wav]=make_filter_object(Filter_vector)
        Reliable:  """
    wavelength_filter_effective = dict()  # np.empty(np.shape(Filter_vector)[0])
    wavelength_filter_central = dict()
    wavelength_filter_pivot = dict()
    P_vector = dict()
    #print('Filter_vector is', Filter_vector)
    #print(isinstance(Filter_vector, (list,)))
    # pdb.set_trace()
    if isinstance(Filter_vector, (list,)):
        Filter_vectorx = np.empty([len(Filter_vector), 2], dtype=object)
        for i, j in enumerate(Filter_vector):
            Filter_vectorx[i, 0] = Filter_vector[i][0]
            Filter_vectorx[i, 1] = Filter_vector[i][1]
        P_vector['filter_family'] = Filter_vectorx[:, 0]
        P_vector['filter_name'] = Filter_vectorx[:, 1]
        P_vector['filter_object'] = []

    else:
        Filter_vectorx = Filter_vector
        P_vector['filter_family'] = Filter_vector[:, 0]
        P_vector['filter_name'] = Filter_vector[:, 1]
        P_vector['filter_object'] = []
    # print("P_vector['filter_object'] is",P_vector['filter_object'])
    # pdb.set_trace()
    if dic_transmissions is None:
        if filters_directory is None:
            print('ERROR you need to give either a dic_transmissions or a filters_directory variable')
            pdb.set_trace()
        else:
            dic_transmissions=dic_transmissions(filters_directory)
    for i, j in enumerate(Filter_vectorx):
        #print('j is', j)
        if j[0].lower() == 'ptf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                # if verbose == True:
                print('You gave the G filter of the PTF_P48 family')
                # pdb.set_trace()
                Transmission = dic_transmissions['ptf_g_p48']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_G', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_p48':
                # if verbose==True:
                print('You gave the R filter of the PTF_P48 family')
                Transmission = dic_transmissions['ptf_r_p48']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='PTF_P48_R', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'ztf_p48':
            # print(j[1])
            if j[1].lower() == 'g_p48':
                if verbose == True:
                    print('You gave the G filter of the ztf_P48 family')
                # pdb.set_trace()
                Transmission = dic_transmissions['ztf_g_p48']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_G', dtype='photon',
                                  unit='Angstrom')
                # print('P is',P)
                # pdb.set_trace()
            elif j[1].lower() == 'r_p48':
                if verbose == True:
                    print('You gave the R filter of the ZTF_P48 family')
                Transmission = dic_transmissions['ztf_r_p48']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_R', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_p48':
                if verbose == True:
                    print('You gave the I filter of the ZTF_P48 family')
                Transmission = dic_transmissions['ztf_i_p48']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='ZTF_P48_I', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'swift':
            if j[1].lower() == 'uvw1':
                if verbose == True:
                    print('You gave the uvw1 filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['uvw1_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW1', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvw2':
                if verbose == True:
                    print('You gave the uvw2 filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['uvw2_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVW2', dtype='photon',
                                  unit='Angstrom')
                # elif j[0].lower() == 'swift':
            elif j[1].lower() == 'uvm2':
                if verbose == True:
                    print('You gave the uvm2 filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['uvm2_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_UVM2', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_swift':
                if verbose == True:
                    print('You gave the u filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['u_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_u', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_swift':
                if verbose == True:
                    print('You gave the v filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['v_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_V', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_swift':
                if verbose == True:
                    print('You gave the b filter of the swift family')
                # pdb.set_trace()
                Transmission = dic_transmissions['b_swift']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='Swift_B', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'galex':
            if j[1].lower() == 'galex_nuv':
                if verbose == True:
                    print('You gave the nuv filter of the galex family')
                # pdb.set_trace()
                Transmission = dic_transmissions['nuv_galex']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='galex_nuv', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'sdss':
            if verbose == True:
                print('You gave the sdss family')
            # print(j[1].lower())
            if j[1].lower() == 'r_sdss':
                if verbose == True:
                    print('You gave the r filter of the sdss family')
                # pdb.set_trace()
                Transmission = dic_transmissions['r_sdss']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='r_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'g_sdss':
                if verbose == True:
                    print('You gave the g filter of the sdss family')
                # pdb.set_trace()
                Transmission = dic_transmissions['g_sdss']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='g_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'i_sdss':
                if verbose == True:
                    print('You gave the i filter of the sdss family')
                # pdb.set_trace()
                Transmission = dic_transmissions['i_sdss']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='i_sdss', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'u_sdss':
                if verbose == True:
                    print('You gave the u filter of the sdss family')
                # pdb.set_trace()
                Transmission = dic_transmissions['u_sdss']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='u_sdss', dtype='photon',
                                  unit='Angstrom')

            elif j[1].lower() == 'z_sdss':
                if verbose == True:
                    print('You gave the z filter of the sdss family')
                # pdb.set_trace()
                Transmission = dic_transmissions['z_sdss']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='z_sdss', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == '2mass':
            if verbose == True:
                print('You gave the 2MASS family')
                print(j[1].lower())
            if j[1].lower() == 'j_2mass':
                if verbose == True:
                    print('You gave the J filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['j_2mass']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='2MASS_J', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'h_2mass':
                if verbose == True:
                    print('You gave the h filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['h_2mass']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='h_2mass', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'k_2mass':
                if verbose == True:
                    print('You gave the k filter of the 2MASS family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['k_2mass']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='k_2mass', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'cousin':
            if verbose == True:
                print('You gave the cousin family')
                # print(j[1].lower())
            if j[1].lower() == 'i_cousin':
                if verbose == True:
                    print('You gave the i filter of the cousin family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['i_cousin']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='i_counsin', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'r_cousin':
                if verbose == True:
                    print('You gave the r filter of the cousin family')
                Transmission = dic_transmissions['r_cousin']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='r_cousin', dtype='photon',
                                  unit='Angstrom')
        elif j[0].lower() == 'johnson':
            if verbose == True:
                print('You gave the johnson family')
                print(j[1].lower())
            if j[1].lower() == 'u_johnson':
                if verbose == True:
                    print('You gave the u filter of the johnson family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['u_johnson']
                # print('the shape of transission is',Transmission)
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='u_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'b_johnson':
                if verbose == True:
                    print('You gave the b filter of the johnson family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['b_johnson']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='b_johnson', dtype='photon',
                                  unit='Angstrom')
            elif j[1].lower() == 'v_johnson':
                if verbose == True:
                    print('You gave the v filter of the johnson family')
                    # pdb.set_trace()
                Transmission = dic_transmissions['v_johnson']
                P = Filter(Transmission[:, 0], Transmission[:, 1], name='v_johnson', dtype='photon',
                                  unit='Angstrom')
        else:
            print('I HAVE NOT RECOGNIZE THE FILTER')
            pdb.set_trace()
            #lib = pyphot.get_library()
            #f = lib.find(j[0].lower())  # filter family
            #if verbose == True:
            #    for name in f:
            #        lib[name].info(show_zeropoints=True)
            #P = lib[j[1]]  # filter name
            # min_w=np.min(Transmission[:,0])
            # max_w=np.max(Transmission[:,0])
            # print(P_vector)
            # print('Filter_vector is',Filter_vector)
            # print('P is',P)
            # print("P_vector['filter_object'] is",P_vector['filter_object'])
            # if isinstance(P_vector['filter_object'],(list,)) is False:
            #   P_vector['filter_object']=[P_vector['filter_object']].append(P)
            # print("P_vector['filter_object'] is", P_vector['filter_object'])
            # print("P_vector['filter_name'] is", P_vector['filter_name'])
        if isinstance(P_vector['filter_object'], (list,)) is True:
            #print('oui, liste de longueur', len(P_vector['filter_object']))
            if len(P_vector['filter_object']) > 0:
                ##print('oui')
                # print('I am trying to append {0} to {1}'.format(P,P_vector['filter_object']))
                P_vector['filter_object'] = P_vector['filter_object'] + [P]
                P_vector['filter_name'] = P_vector['filter_name'] + [j[1].lower()]
                P_vector['filter_family'] = P_vector['filter_family'] + [j[0].lower()]
                # print('ca a marche?',P_vector['filter_object'])
            else:
                # print('faison une liste')
                P_vector['filter_object'] = [P]
                # print(P_vector['filter_object'])
                P_vector['filter_name'] = [j[1].lower()]
                P_vector['filter_family'] = [j[0].lower()]
                # pdb.set_trace()

                # print("P_vector['filter_object'] is",P_vector['filter_object'])
                # print("P_vector['filter_name'] is",P_vector['filter_name'])
                # print('i is',i)
        #wavelength_filter_effective[P_vector['filter_name'][i]] = P.leff.item()
        wavelength_filter_central[P_vector['filter_name'][i]] = P.cl()
        # wavelength_filter_min[P_vector['filter_name'][i]]=np.min(Transmission[:,0])
        # wavelength_filter_max[P_vector['filter_name'][i]] = np.max(Transmission[:, 0])

        # if isinstance(Filter_vector, (list,)):
        # P_vector['filter_object']=P_vector['filter_object'][0]

        # print(P_vector)
        # print(P)
        # P_vector['filter_object'].append(P)
        # wavelength_filter_effective[P_vector['filter_name'][i]]=P.leff.item()
        # wavelength_filter_central[P_vector['filter_name'][i]]=P.cl.item()
        # if isinstance(Filter_vector, (list,)):
        #    P_vector['filter_object']=P_vector['filter_object'][0]

    # print('Filter_vector was', Filter_vector)
    # print(' and P_vector is', P_vector)
    # pdb.set_trace()

    if central == True:
        return P_vector, wavelength_filter_central  # same as Eran eff_wl
    else:
        return P_vector, wavelength_filter_effective

class filterObj(object):#create a filterObj similar to Eran's definition
    def __init__(self, filtername, instrumentname, path_to_filters):
        self.family = instrumentname
        self.band = filtername
        self.path_to_filters = path_to_filters
        if self.family=='ztf_p48':
            if self.band.lower() == 'g_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/ZTF_g_fromgithub_AA.txt', delimiter=None)
                self.P = Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_G', dtype='photon',
                                       unit='Angstrom')
            elif self.band.lower() == 'r_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/ZTF_r_fromgithub_AA.txt', delimiter=None)
                self.P = Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_R', dtype='photon',
                                       unit='Angstrom')
        elif self.family=='ptf_p48':
            if self.band.lower() == 'g_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/PTF_G.rtf', delimiter=',')
                self.P = Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_G', dtype='photon',
                                       unit='Angstrom')
            elif self.band.lower() == 'r_p48':
                self.T = np.genfromtxt(
                    path_to_filters + '/P48_R_T.rtf', delimiter=',')
                self.P = Filter(self.T[:, 0], self.T[:, 1], name='PTF_P48_R', dtype='photon',
                                       unit='Angstrom')
        elif self.band.lower() == 'uvw1':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVW1.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW1', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'uvw2':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVW2.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW2', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'uvm2':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_UVM2.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_UVW2', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_u.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_u', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'v_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_V.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_v', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'b_swift':
            self.T = np.genfromtxt(
                path_to_filters + '/Swift_B.rtf', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='Swift_B', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'galex_nuv':
            self.T = np.genfromtxt(
                path_to_filters + '/GALEX_NUV.dat', delimiter=None)
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='galex_nuv', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'r_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_r.txt', delimiter=',')
            #print('np.shape(self.T) is',np.shape(self.T))

            self.P = Filter(self.T[:, 0], self.T[:, 1], name='r_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'g_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_g.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='g_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'i_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_i.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='i_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_u.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='u_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'z_sdss':
            self.T = np.genfromtxt(
                path_to_filters + '/SDSS_z.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='z_sdss', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'j_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_J.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='j_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'h_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_H.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='h_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'k_2mass':
            self.T = np.genfromtxt(
                path_to_filters + '/2MASS_K.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='k_2mass', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'i_cousin':
            self.T = np.genfromtxt(
                path_to_filters + '/cousin_i.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='i_cousin', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'r_cousin':
            self.T = np.genfromtxt(
                path_to_filters + '/cousin_r.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='r_cousin', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'u_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_u.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='u_johnson', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'b_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_b.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='b_johnson', dtype='photon',
                                   unit='Angstrom')
        elif self.band.lower() == 'v_johnson':
            self.T = np.genfromtxt(
                path_to_filters + '/johnson_v.txt', delimiter=',')
            self.P = Filter(self.T[:, 0], self.T[:, 1], name='v_johnson', dtype='photon',
                                   unit='Angstrom')

        else:
            print('I HAVE NOT RECOGNIZE THE FILTER')
            pdb.set_trace()

    def min_wl(self):
        min_wl = np.min(self.T[:, 0])
        return min_wl

    def max_wl(self):
        max_wl = np.max(self.T[:, 0])
        return max_wl

    #def eff_wl(self):
    #    return self.P.leff.item()

    def cl_wl(self):
        return self.P.cl

class Filter:
    def __init__(self, wavelength, transmit, name='', dtype="photon",unit='Angstrom'):
        """a class inspired by the pyphot class"""
        self.name       = name
        self.set_dtype(dtype)
        self._wavelength = wavelength
        #self.set_wavelength_unit(unit)
        self.transmit   = np.clip(transmit, 0., np.nanmax(transmit))
        self.norm       = trapz(self.transmit, self._wavelength)#int(T dlambda)
        self._lT        = trapz(self._wavelength * self.transmit, self._wavelength)#int(lambda*T dlambda)
        self._lpivot    = self.calculate_lpivot()
        self._cl        = self._lT / self.norm
        self.unit=unit
    #def set_wavelength_unit(self, unit):
    #    """ Set the wavelength units """
    #    '''
    #    try:   # get units from the inputs
    #        self.wavelength_unit = str(self._wavelength.units)
    #    except AttributeError:'''
    #    self.wavelength_unit = unit
    def set_dtype(self, dtype):
        """ Set the detector type (photon or energy)"""
        _d = dtype.lower()
        if "phot" in _d:
            self.dtype = "photon"
        elif "ener" in _d:
            self.dtype = "energy"
        else:
            raise ValueError('Unknown detector type {0}'.format(dtype))
    def calculate_lpivot(self):
        if 'photon' in self.dtype:
            lpivot2 = self._lT / trapz(self.transmit / self._wavelength, self._wavelength)
        else:
            lpivot2 = self.norm / trapz(self.transmit / self._wavelength ** 2, self._wavelength)
        return np.sqrt(lpivot2)
    def cl(self):
        return self._cl
    def info(self, show_zeropoints=True):
        """ display information about the current filter"""
        """
            print('''Filter object information:
    name:                 {s.name:s}
    detector type:        {s.dtype:s}
    central wavelength:   {s._cl:f}
    pivot wavelength:     {s._lpivot:f}
    effective wavelength: {s.leff:f}
    photon wavelength:    {s.lphot:f}
    minimum wavelength:   {s.lmin:f}
    maximum wavelength:   {s.lmax:f}
    norm:                 {s.norm:f}
    effective width:      {s.width:f}
    fullwidth half-max:   {s.fwhm:f}
    definition contains {s.transmit.size:d} points'''.format(s=self).replace('None', 'unknown'))"""
        print("""Zeropoints
          AB: {0} magAB,
              {1} erg/s/cm^2/AA
        """.format(self.AB_zero_mag(),self.AB_zero_flux()))
    def get_flux(self, slamb, sflux, axis=-1,verbose=True):
        """getFlux
        Integrate the flux within the filter and return the integrated energy
        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain
        sflux: ndarray(dtype=float, ndim=1)
            associated flux
        Returns
        -------
        flux: float
            Energy of the spectrum within the filter
        """
        if verbose==True:
            print('in Filter.get_flus, WARNING: T and the flux wavelengths should be given in AA')
        _slamb=slamb
        # clean data for inf values by interpolation
        if True in np.isinf(sflux):
            indinf = np.where(np.isinf(sflux))
            indfin = np.where(np.isfinite(sflux))
            sflux[indinf] = np.interp(_slamb[indinf], _slamb[indfin], sflux[indfin])

        # reinterpolate transmission onto the same wavelength def as the data
        ifT = np.interp(_slamb, self._wavelength, self.transmit, left=0., right=0.)
        # if the filter is null on that wavelength range flux is then 0
        # ind = ifT > 0.
        nonzero = np.where(ifT > 0)[0]
        if nonzero.size <= 0:
            return 0.
        nonzero_start = max(0, min(nonzero) - 5)
        nonzero_end = min(len(ifT), max(nonzero) + 5)
        ind = np.zeros(len(ifT), dtype=bool)
        ind[nonzero_start:nonzero_end] = True
        if True in ind:
            try:
                _sflux = sflux[:, ind]
            except:
                _sflux = sflux[ind]
            # limit integrals to where necessary
            # ind = ifT > 0.
            if 'photon' in self.dtype:
                a = np.trapz(_slamb[ind] * ifT[ind] * _sflux, _slamb[ind], axis=axis)
                b = np.trapz(_slamb[ind] * ifT[ind], _slamb[ind])
            elif 'energy' in self.dtype:
                a = np.trapz(ifT[ind] * _sflux, _slamb[ind], axis=axis)
                b = np.trapz(ifT[ind], _slamb[ind])
            if (np.isinf(a).any() | np.isinf(b).any()):
                print(self.name, "Warn for inf value")
            return a / b
        else:
            return 0.
    def AB_zero_mag(self):
        """ AB magnitude zero point
        ABmag = -2.5 * log10(f_nu) - 48.60
              = -2.5 * log10(f_lamb) - 2.5 * log10(lpivot ** 2 / c) - 48.60
              = -2.5 * log10(f_lamb) - zpts
        """
        #C1 = unit[self.wavelength_unit].to('AA').magnitude ** 2 / unit['c'].to('AA/s').magnitude
        c1 = self._lpivot ** 2 /(2.99792458e18)
        m = 2.5 * np.log10(c1) + 48.6
        return m
    def AB_zero_flux(self):
        """ AB flux zero point in erg/s/cm2/AA """
        return 10 ** (-0.4 * self.AB_zero_mag())
    def get_mag(self, slamb, sflux):
        print('in Filter.get_mag, WARNING: T and the flux wavelengths should be given in AA')
        return -2.5 * np.log10(self.get_flux(slamb, sflux) / self.AB_zero_flux())




    