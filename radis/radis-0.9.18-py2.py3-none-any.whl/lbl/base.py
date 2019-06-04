# -*- coding: utf-8 -*-
"""

Summary
-------

A class to aggregate methods to calculate spectroscopic parameter and
populations (and unload factory.py)

BaseFactory is inherited by BroadenFactory eventually

Routine Listing
---------------


PUBLIC METHODS

- :meth:`~radis.lbl.base.BaseFactory.print_conditions`         >>> get all calculation conditions
- :meth:`~radis.lbl.base.BaseFactory.get_energy_levels`        >>> return energy database
- :meth:`~radis.lbl.base.BaseFactory.get_abundance`            >>> return energy database
- :meth:`~radis.lbl.base.BaseFactory.plot_linestrength_hist`   >>>  plot distribution of linestrengths
- :meth:`~radis.lbl.base.BaseFactory.plot_hist`                >>> same

PRIVATE METHODS - CALCULATE SPECTROSCOPIC PARAMETERS
(everything that doesnt depend on populations / temperatures)
(computation: work & update with 'df0' and called before eq_spectrum()  )

- _add_EvibErot
- _add_EvibErot_CDSD
- _add_EvibErot_RADIS_cls1
- _add_Evib123Erot_RADIS_cls5
- _add_ju
- _add_Eu
- _check_noneq_parameters
- _calc_noneq_parameters
- _calc_weighted_trans_moment
- _calc_einstein_coefficients

PRIVATE METHODS - APPLY ENVIRONMENT PARAMETERS
(all functions that depends upon T or P)
(calculates populations, linestrength & radiance, lineshift)
(computation: work on df1, called by or after eq_spectrum() )

- _calc_lineshift
- _calc_linestrength_eq
- _calc_populations_eq
- _calc_populations_noneq
- _calc_linestrength_noneq
- _calc_emission_integral
- _cutoff_linestrength

Most methods are written in inherited class with the following inheritance scheme:
    
:py:class:`~radis.lbl.loader.DatabankLoader` > :py:class:`~radis.lbl.base.BaseFactory` > 
:py:class:`~radis.lbl.broadening.BroadenFactory` > :py:class:`~radis.lbl.bands.BandFactory` > 
:py:class:`~radis.lbl.factory.SpectrumFactory` > :py:class:`~radis.lbl.parallel.ParallelFactory`



----------


"""


from __future__ import print_function, absolute_import, division, unicode_literals
import radis
from radis.db.molparam import MolParams
from radis.lbl.loader import DatabankLoader, KNOWN_LVLFORMAT, df_metadata
from radis.lbl.labels import (vib_lvl_name_hitran_class1,
                             vib_lvl_name_hitran_class5)
from radis.phys.constants import c_CGS, h_CGS
from radis.phys.convert import cm2J, cm2nm, nm2cm
from radis.phys.constants import hc_k
from radis.misc.basics import all_in, transfer_metadata
from radis.misc.debug import printdbg
from radis.misc.log import printwarn
from radis.misc.printer import printg
# TODO: rename in get_molecule_name
from radis.io.hitran import get_molecule, get_molecule_identifier
from radis.spectrum.utils import print_conditions
from radis.phys.air import air2vacuum, vacuum2air
from numpy import exp, pi
import numpy as np
import sys
from time import time
from six import string_types
import matplotlib.pyplot as plt
import pandas as pd
from six.moves import range
from six.moves import zip


class BaseFactory(DatabankLoader):

    # Output units
    units = {
        'absorbance': '-ln(I/I0)',
        'abscoeff': 'cm_1',
        'abscoeff_continuum': 'cm_1',
        # TODO: deal with case where 'cm-1' is given as input for a Spectrum
        # (write a cast_unit of some kind)
        # different in Specair (mw/cm2/sr) because slit
        'radiance': 'mW/cm2/sr/nm',
        # function is not normalized to conserve energy
        'radiance_noslit': 'mW/cm2/sr/nm',       # it's actually a spectral radiance
        'emisscoeff': 'mW/cm3/sr/nm',
        'emisscoeff_continuum': 'mW/cm3/sr/nm',
        'emissivity': 'eps',
        'emissivity_noslit': 'eps',
        'transmittance': 'I/I0',
        'transmittance_noslit': 'I/I0'
    }

    # Calculation Conditions units
    cond_units = {
        'wavenum_min':  'cm-1',
        'wavenum_max':  'cm-1',
        'wavenum_min_calc':     'cm-1',
        'wavenum_max_calc':     'cm-1',
        'wstep':        'cm-1',
        'wavelength_min':  'nm',    # not defined as a variable. All calculations
                                    # are done with cm-1. Just for information
        'wavelength_max':  'nm',
        'Tref':         'K',
        'Tgas':         'K',
        'Tvib':         'K',
        'Trot':         'K',
        'pressure_mbar':    'mbar',
        'path_length':  'cm',
        #        'slit_function_FWHM':   'nm',
        'cutoff':       'cm-1/(#.cm-2)',
        'broadening_max_width': 'cm-1',

        # The later is never stored in Factory, but exported in Spectrum at the end of the calculation
        'calculation_time': 's'
    }

    def __init__(self):

        super(BaseFactory, self).__init__()  # initialize parent class

        # Define variable names
        # ... Note: defaults values are overwritten by SpectrumFactory input
        # ... values here are just to help autocompletion tools
        self.input.Tref = 296

        # all calculations are done in cm-1 in SpectrumFactory
        self.params.waveunit = 'cm-1'
        # dont change this without making sure your line database
        # is correct, and the units conversions (ex: radiance)
        # are changed accordingly
        # Note that radiance are converted from ~ [mW/cm2/sr/cm_1]
        # to ~ [mW/cm/sr/nm]
        assert self.params.waveunit == self.cond_units['wstep']
        
        self._export_continuum = False
        # private key to export abscoeff_continuum in the generated Spectrum.
        # so far continuum is not exported by default because rescale functions
        # are not defined yet. #TODO

    # %% ======================================================================
    # PUBLIC METHODS
    # ------------------------
    # print_conditions         >>> get all calculation conditions
    # get_energy_levels        >>> return energy database
    # get_abundance            >>> return energy database
    # plot_linestrength_hist   >>> get all linestrength distribution
    # plot_hist                >>> same
    #
    # =========================================================================

    def print_conditions(self, preprend=None):
        ''' Prints all physical / computational parameters.
        These are also stored in each result Spectrum

        Parameters
        ----------

        preprend: str
            just to text to display before printing conditions

        '''

        if preprend:
            print(preprend)

        conditions = self.get_conditions()

        return print_conditions(conditions, self.cond_units)

    def get_energy_levels(self, molecule, isotope, state, conditions=None):
        ''' Return energy levels database for given molecule > isotope > state
        (look up Factory.parsum_calc[molecule][iso][state])

        Parameters
        ----------

        molecule: str
            molecule name

        isotope: int
            isotope identifier

        state: str:
            electronic state

        conditions: str, or ``None``
            if not None, add conditions on which energies to retrieve, e.g:

            >>> 'j==0' or 'v1==0'

            Conditions are applied using Dataframe.query() method. In that case,
            ``get_energy_levels()`` returns a copy. Default ``None``

        Returns
        -------

        energies: pandas Dataframe
            a view of the energies stored in the Partition Function calculator
            for isotope iso. If conditions are applied, we get a copy

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory.get_populations`

        '''

        energies = self.get_partition_function_calculator(
            molecule, isotope, state).df

        if conditions is not None:
            energies = energies.query(conditions)

        return energies

    def get_abundance(self, molecule, isotope):
        ''' Returns abundance of molecule > isotope '''

        return self.parsum_calc[molecule][isotope].Ia

    def plot_linestrength_hist(self):
        ''' Plot linestrength distribution (to help determine a cutoff criteria) '''
        return self.plot_hist('df1', 'S')

    def plot_hist(self, dataframe='df0', what='int'):
        ''' Plot distribution (to help determine a cutoff criteria)

        Parameters
        ----------

        dataframe: 'df0', 'df1'
            which dataframe to plot (df0 is the loaded one, df1 the scaled one)

        what: str
            which feature to plot. Default ``'S'`` (scaled linestrength). Could also
            be ``'int'`` (reference linestrength intensity), ``'A'`` (Einstein coefficient)
        '''
        assert dataframe in ['df0', 'df1']
        plt.figure()
        df = getattr(self, dataframe)
        a = np.log10(np.array(df[what]))
        if np.isnan(a).any():
            printwarn('Nan values in log10(lines)')
        plt.hist(np.round(a[~np.isnan(a)]))
        plt.xlabel('log10({0})'.format(what))
        plt.ylabel('Count')

    # %% ======================================================================
    # PRIVATE METHODS - CALCULATE SPECTROSCOPIC PARAMETERS
    # (everything that doesnt depend on populations / temperatures)
    # (computation: work & update with 'df0' and called before eq_spectrum()  )
    # ---------------------------------
    # _add_EvibErot
    # _add_EvibErot_CDSD
    # _add_EvibErot_RADIS_cls1
    # _add_Evib123Erot_RADIS_cls5
    # _add_ju
    # _add_Eu
    # _check_noneq_parameters
    # _calc_noneq_parameters
    # _calc_weighted_trans_moment
    # _calc_einstein_coefficients
    # =========================================================================

    def _add_EvibErot(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in Line dataframe

        Parameters
        ----------

        df: DataFrame
            list of transitions
        
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)

        '''
        if self.verbose:
            print('Fetching Evib & Erot.')
            if self.verbose >= 2: 
                  printg('If using this code several' +
                  ' times you should consider updating the database' +
                  ' directly. See functions in factory.py ')

        from radis.io.hitran import HITRAN_CLASS1, HITRAN_CLASS5

        # Different methods to get Evib and Erot:

        # fetch energies from precomputed CDSD levels: one Evib per (p, c) group
        if self.params.levelsfmt == 'cdsd-pc':     
            return self._add_EvibErot_CDSD_pc(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)

        # fetch energies from precomputed CDSD levels: one Evib per (p, c, N) group
        elif self.params.levelsfmt == 'cdsd-pcN':
            return self._add_EvibErot_CDSD_pcN(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)

        # fetch energies from CDSD levels calculated from Hamiltonian: one Evib per (p, c, J, N) group
        # (that's necessary if Evib are different for all levels, which can be 
        # the case if coupling terms are calculated)
        elif self.params.levelsfmt == 'cdsd-hamil':     # fetch energies from precomputed CDSD levels
            return self._add_EvibErot_CDSD_pcJN(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)

        # calculate directly with Dunham expansions, whose terms are included in
        # the radis.db database
        elif self.params.levelsfmt == 'radis':    
            molecule = self.input.molecule
            if molecule in HITRAN_CLASS1:  # class 1
                return self._add_EvibErot_RADIS_cls1(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)
            elif molecule in HITRAN_CLASS5:
                if __debug__:
                    printdbg(
                        'placeholder: using getEvib123 while getEvib would be enough')
                # TODO: write simplified function: doesnt need to fetch Evib1,2,3 here
                # as only Evib is needed in this case
                if calc_Evib_harmonic_anharmonic:
                    return self._add_Evib123Erot_RADIS_cls5_harmonicanharmonic(df)
                else:
                    return self._add_Evib123Erot_RADIS_cls5(df)
            else:
                raise NotImplementedError(
                    'Molecules not implemented: {0}'.format(molecule.name))  # TODO

        else:
            raise NotImplementedError("Impossible to calculate Evib Erot with given energy "
                                      + "format: {0}".format(self.params.levelsfmt))

    def _add_Evib123Erot(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in dataframe

        Parameters
        ----------

        df: DataFrame

        '''
        if self.verbose:
            print('Fetching Evib & Erot. If using this code several' +
                  ' times you should consider updating the database' +
                  ' directly. See functions in factory.py ')

        from radis.io.hitran import HITRAN_CLASS5

        if self.params.levelsfmt == 'cdsd-pc':     # calculate from precomputed CDSD levels
            return self._add_Evib123Erot_CDSD_pc(df)

        elif self.params.levelsfmt == 'cdsd-pcN':     # calculate from precomputed CDSD levels
            raise NotImplementedError(
                '3 Tvib mode for CDSD in pcN convention')  # TODO

        elif self.params.levelsfmt == 'radis':    # calculate with Dunham expansions
            if self.input.molecule in HITRAN_CLASS5:  # class 1
                if calc_Evib_harmonic_anharmonic:
                    return self._add_Evib123Erot_RADIS_cls5_harmonicanharmonic(df)
                else:
                    return self._add_Evib123Erot_RADIS_cls5(df)
            else:
                raise NotImplementedError(
                    'Molecules other than HITRAN class 5 (CO2) not implemented')  # TODO

        else:
            raise NotImplementedError("Impossible to calculate Evib Erot with given energy "
                                      + "format: {0}".format(self.params.levelsfmt))

    def _add_EvibErot_CDSD_pc(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in Lines database:
        - Evib is fetched from Energy Levels database
        - Erot is calculated with Erot = E - Evib 

        Note: p, c, j, n is a partition and we just a groupby(these) so all
        poluy, wangu etc. are the same

        Parameters
        ----------

        df: DataFrame
            list of transitions

        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)

        '''

        # Check inputs
        if calc_Evib_harmonic_anharmonic:
            raise NotImplementedError

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too
        assert molecule == 'CO2'

        # Check energy levels are here
        for iso in self._get_isotope_list(molecule):
            if not iso in self.parsum_calc['CO2']:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')
        if self.verbose>=2:
            t0 = time()
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))

        def get_Evib_CDSD_pc_1iso(df, iso):
            ''' Calculate Evib for a given isotope (energies are specific
            to a given isotope) '''

#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            # list of energy levels for given isotope
            energies = self.get_energy_levels(molecule, iso, state)

            # only keep vibrational energies
            # see text for how we define vibrational energy
            index = ['p', 'c']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)

            # Calculate vibrational / rotational levels for all transitions
            def fillEvibu(r):
                '''
                Note: we just did a groupby('polyu', 'wangu') so all
                r.poluy, r.wangu etc. are the same in a group r

                Implementation
                ------
                r.polyu.iloc[0],r.wangu.iloc[0],r.ranku.iloc[0]  : [0] because they're
                            all the same
                r.ju.iloc[0]  not necessary (same Tvib) but explicitely mentionning it
                         yields a x20 on performances (60s -> 3s)
                '''
                r['Evibu'] = energies.at[(
                    r.polyu.iloc[0], r.wangu.iloc[0]), 'Evib']
                return r

            def fillEvibl(r):
                # Not: p, c, j, n is a partition and we just did a groupby(these)
                # so all r.poluy, r.wangu etc. are the same
                r['Evibl'] = energies.at[(
                    r.polyl.iloc[0], r.wangl.iloc[0]), 'Evib']
                return r

    #        df['Evibu'] = df.groupby(by=['polyu','wangu','ranku']).apply(fillEvibu)
    #        df['Evibl'] = df.groupby('polyl','wangl','rankl').apply(Evibl, axis=1)
    #        %timeit: 43.4s per loop

            # total:  ~ 15s on 460k lines   (probably faster since neq==0.9.20)
#            try:
            # ~ 6.6 s (probably faster since neq==0.9.20 (radis<1.0)
            df = df.groupby(by=['polyu', 'wangu']).apply(fillEvibu)
            # ~ 6.6 s (probably faster since neq==0.9.20 (radis<1.0)
            df = df.groupby(by=['polyl', 'wangl']).apply(fillEvibl)
#            except KeyError:
#                import traceback
#                traceback.print_exc()
#                raise KeyError("{0} -> An error (see above) occured that usually ".format(sys.exc_info()[1]) +
#                               "happens when the energy level is not referenced in the database. " +
#                               "Check your partition function calculator, and energies " +
#                               "for isotope {0} (Factory.parsum_calc['CO2'][{0}]['X'].df)".format(iso))

            # Another version that failed because twice slower than apply() in that case
            # ~ keep it for information
    #        Evibdict = energies.set_index(['p','c','N'])['Evib']
    #        Evibdict = Evibdict.drop_duplicates()
    #        try:
    #            dgb = df.groupby(by=['polyu', 'wangu', 'ranku'])
    #            for (poly, wang, rank), idx in dgb.indices.items(): # ~ 3600 items for 460k lines -> total 15s
    #                Evib = Evibdict[(poly, wang, rank)]             # ~ 7.15 µs
    #                df.loc[idx, 'Evibu'] = Evib                     # ~ 4.38ms
    #
    #            dgb = df.groupby(by=['polyl', 'wangl', 'rankl'])
    #            for (poly, wang, rank), idx in dgb.indices.items(): # ~ 3600 items for 460k lines -> total 15s
    #                Evib = Evibdict[(poly, wang, rank)]             # ~ 7.15 µs
    #                df.loc[idx, 'Evibl'] = Evib                     # ~ 4.38ms

            return df.loc[idx, ['Evibl', 'Evibu']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: add_Evib_CDSD_pc_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936

        df['Evibl'] = np.nan
        df['Evibu'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evibl', 'Evibu']] = get_Evib_CDSD_pc_1iso(df.loc[idx], iso)
            
            if radis.DEBUG_MODE:
                assert (df.loc[idx, 'iso'] == iso).all()

        # Get rotational energy: better recalculate than look up the database
        # (much faster!: perf ~25s -> 765µs)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))
        
        assert np.isnan(df.Evibu).sum() == 0
        assert np.isnan(df.Evibl).sum() == 0

        return # None: Dataframe updated

    def _add_EvibErot_CDSD_pcN(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in Lines database:
        - Evib is fetched from Energy Levels database
        - Erot is calculated with Erot = E - Evib 

        Note: p, c, j, n is a partition and we just a groupby(these) so all
        poluy, wangu etc. are the same

        Parameters
        ----------

        df: DataFrame
            list of transitions
        
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)


        '''
        if __debug__:
            printdbg(
                'called _add_EvibErot_CDSD(calc_Evib_harmonic_anharmonic={0})'.format(calc_Evib_harmonic_anharmonic))

        if calc_Evib_harmonic_anharmonic:
            raise NotImplementedError

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too
        assert molecule == 'CO2'

        if self.verbose>=2:
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Check energy levels are here
        for iso in self._get_isotope_list():
            if not iso in self.parsum_calc['CO2']:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib_CDSD_pcN_1iso(df, iso):
            ''' Calculate Evib for a given isotope (energies are specific
            to a given isotope) '''

#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            # list of energy levels for given isotope
            energies = self.get_energy_levels(molecule, iso, state)

            # only keep vibrational energies
            # see text for how we define vibrational energy
            index = ['p', 'c', 'N']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)
            Evib_dict = dict(list(zip(energies.index, energies.Evib)))

            # Add lower state energy
            df_pcN = df.set_index(['polyl', 'wangl', 'rankl'])
#            for i in df.index:
#                df.loc[i, 'Evibl'] = energies.at[i, 'Evib']
            # the map below is crazy fast compared to above loop
            df['Evibl'] = df_pcN.index.map(Evib_dict.get).values
            # Add upper state energy
            df_pcN = df.set_index(['polyu', 'wangu', 'ranku'])
#            for i in df.index:
#                df.loc[i, 'Evibu'] = energies.at[i, 'Evib']
            # the map below is crazy fast compared to above loop
            df['Evibu'] = df_pcN.index.map(Evib_dict.get).values 

            return df.loc[idx, ['Evibl', 'Evibu']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib_CDSD_pcN_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936

        df['Evibl'] = np.nan
        df['Evibu'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evibl', 'Evibu']] = get_Evib_CDSD_pcN_1iso(df.loc[idx], iso)
            
            if radis.DEBUG_MODE:
                assert (df.loc[idx, 'iso'] == iso).all()

        # Get rotational energy: better recalculate than look up the database
        # (much faster!: perf ~25s -> 765µs)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        assert np.isnan(df.Evibu).sum() == 0
        assert np.isnan(df.Evibl).sum() == 0
        
        return # None: Dataframe updated

    def _add_EvibErot_CDSD_pcJN(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in Lines database:
        - Evib is fetched from Energy Levels database
        - Erot is calculated with Erot = E - Evib 

        Parameters
        ----------

        df: DataFrame
            list of transitions
        
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)


        '''
        if __debug__:
            printdbg(
                'called _add_EvibErot_CDSD_pcJN(calc_Evib_harmonic_anharmonic={0})'.format(calc_Evib_harmonic_anharmonic))

        if calc_Evib_harmonic_anharmonic:
            raise NotImplementedError

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too
        assert molecule == 'CO2'

        if self.verbose>=2:
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Check energy levels are here
        for iso in self._get_isotope_list(molecule):
            if not iso in self.parsum_calc['CO2']:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib_CDSD_pcJN_1iso(df, iso):
            ''' Calculate Evib for a given isotope (energies are specific
            to a given isotope) 
            
            Notes
            -----
            
            for devs:
                
            Unlike get_EvibErot_CDSD_pcN_1iso and get_EvibErot_CDSD_pc_1iso,
            no need to use groupby() here, as (per construction) there is only
            one level for a combination of p, c, J, N
            
            '''
            
#             # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            # list of energy levels for given isotope
            energies = self.get_energy_levels(molecule, iso, state)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            index = ['p', 'c', 'j', 'N']
#            energies.set_index(index, inplace=True) # cant get it work for some reason
            # ... (it seems groupby().apply() is building some cache variables and 
            # ... I cant reset the index of energies properly)
            energies = energies.set_index(index, inplace=False)
            Evib_dict = dict(list(zip(energies.index, energies.Evib)))
            
            # Add lower state energy
            df_pcJN = df.set_index(['polyl', 'wangl', 'jl', 'rankl'])
#            for i in df.index:
#                df.loc[i, 'Evibl'] = energies.at[i, 'Evib']
            # the map below is crazy fast compared to above loop
            df.loc[:, 'Evibl'] = df_pcJN.index.map(Evib_dict.get).values
            # Add upper state energy
            df_pcJN = df.set_index(['polyu', 'wangu', 'ju', 'ranku'])
#            for i in df.index:
#                df.loc[i, 'Evibu'] = energies.at[i, 'Evib']
            # the map below is crazy fast compared to above loop
            df.loc[:, 'Evibu'] = df_pcJN.index.map(Evib_dict.get).values

            return df.loc[:, ['Evibl', 'Evibu']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib_CDSD_pcJN_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936
            
        # slower than the following:
        df['Evibl'] = np.nan
        df['Evibu'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evibl', 'Evibu']] = get_Evib_CDSD_pcJN_1iso(df.loc[idx], iso)

            if radis.DEBUG_MODE:
                assert (df.loc[idx, 'iso'] == iso).all()

        # Get rotational energy: better recalculate than look up the database
        # (much faster!: perf ~25s -> 765µs)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        assert np.isnan(df.Evibu).sum() == 0
        assert np.isnan(df.Evibl).sum() == 0
        
        return  # None: Dataframe updated

    def _add_Evib123Erot_CDSD_pc(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Lookup Evib1, Evib2, Evib3 & Erot for all lines in dataframe

        Note: p, c, j, n is a partition and we just a groupby(these) so all
        poluy, wangu etc. are the same

        Parameters
        ----------

        df: DataFrame
            list of transitions
            
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)

        '''
        if __debug__:
            printdbg(
                'called _add_Evib123Erot_CDSD_pc(calc_Evib_harmonic_anharmonic={0})'.format(calc_Evib_harmonic_anharmonic))

        if calc_Evib_harmonic_anharmonic:
            raise NotImplementedError

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too
        assert molecule == 'CO2'

        if self.verbose>=2:
            printg('Fetching vib123 / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Get Energy database
        if self.parsum_calc == {}:
            raise AttributeError('No Partition function calculator defined in this database'
                                 + '. You need energies to calculate a non-equilibrium spectrum!'
                                 + ' Fill the levels parameter in your database definition, '
                                 + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                 + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib123_CDSD_pc_1iso(df, iso):
            ''' Calculate Evib for a given isotope (energies are specific
            to a given isotope) '''
            # TODO: implement with map() instead (much faster!! see get_Evib_CDSD_* )
            
#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            energies = self.get_energy_levels(molecule, iso, state)
            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)

            # only keep vibrational energies
            # see text for how we define vibrational energy
            index = ['p', 'c']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)

            # Calculate vibrational / rotational levels for all transitions
            def fillEvib123u(r):
                '''
                Note: p, c, j, n is a partition and we just did a groupby(these)
                # so all r.poluy, r.wangu etc. are the same

                Implementation
                ------
                r.polyu.iloc[0],r.wangu.iloc[0],r.ranku.iloc[0]  : [0] because they're
                            all the same
                r.ju.iloc[0]  not necessary (same Tvib) but explicitely mentionning it
                         yields a x20 on performances (60s -> 3s)
                (probably faster since neq==0.9.20) (radis<1.0)
                '''
                r['Evib1u'] = energies.at[(
                    r.polyu.iloc[0], r.wangu.iloc[0]), 'Evib1']
                r['Evib2u'] = energies.at[(
                    r.polyu.iloc[0], r.wangu.iloc[0]), 'Evib2']
                r['Evib3u'] = energies.at[(
                    r.polyu.iloc[0], r.wangu.iloc[0]), 'Evib3']
                return r

            def fillEvib123l(r):
                # Not: p, c, j, n is a partition and we just did a groupby(these)
                # so all r.poluy, r.wangu etc. are the same
                r['Evib1l'] = energies.at[(
                    r.polyl.iloc[0], r.wangl.iloc[0]), 'Evib1']
                r['Evib2l'] = energies.at[(
                    r.polyl.iloc[0], r.wangl.iloc[0]), 'Evib2']
                r['Evib3l'] = energies.at[(
                    r.polyl.iloc[0], r.wangl.iloc[0]), 'Evib3']
                return r

    #        df['Evibu'] = df.groupby(by=['polyu','wangu','ranku']).apply(fillEvibu)
    #        df['Evibl'] = df.groupby('polyl','wangl','rankl').apply(Evibl, axis=1)
    #        %timeit: 43.4s per loop

#            try:  # total:  ~ 15s on 460k lines
            # ~ 6.6 s   (probably faster since neq==0.9.20) (radis<1.0)
            df = df.groupby(by=['polyu', 'wangu']).apply(fillEvib123u)
            # ~ 6.6 s   (probably faster since neq==0.9.20) (radis<1.0)
            df = df.groupby(by=['polyl', 'wangl']).apply(fillEvib123l)
#            except KeyError:
#                printr("{0} -> An error (see above) occured that usually ".format(sys.exc_info()[1]) +
#                       "happens when the energy level is not referenced in the database. " +
#                       "Check your partition function calculator, and energies " +
#                       "for isotope {0} (Factory.parsum_calc['CO2'][{0}]['X'].df)".format(iso))
#                raise
            
            return df.loc[:, ['Evib1l', 'Evib2l', 'Evib3l', 'Evib1u', 'Evib2u', 'Evib3u']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib123_CDSD_pc_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936
        # Slower than the version below:
        df['Evib1l'] = np.nan
        df['Evib2l'] = np.nan
        df['Evib3l'] = np.nan
        df['Evib1u'] = np.nan
        df['Evib2u'] = np.nan
        df['Evib3u'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evib1l', 'Evib2l', 'Evib3l', 'Evib1u', 'Evib2u', 
                       'Evib3u']] = get_Evib123_CDSD_pc_1iso(df.loc[idx], iso)

        # Add total vibrational energy too (doesnt cost much, and can plot populations in spectrum)
        df['Evibu'] = df.Evib1u + df.Evib2u + df.Evib3u
        df['Evibl'] = df.Evib1l + df.Evib2l + df.Evib3l

        # Get rotational energy: better recalculate than look up the database
        # (much faster! perf:  ~25s -> 765µs)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        assert np.isnan(df.Evib1u).sum() == 0
        assert np.isnan(df.Evib2u).sum() == 0
        assert np.isnan(df.Evib3u).sum() == 0
        assert np.isnan(df.Evib1l).sum() == 0
        assert np.isnan(df.Evib2l).sum() == 0
        assert np.isnan(df.Evib3l).sum() == 0
        
        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        return  # None: Dataframe updated

    def _add_EvibErot_RADIS_cls1(self, df, calc_Evib_harmonic_anharmonic=False):
        ''' Calculate Evib & Erot in dataframe for HITRAN class 1 (diatomic) molecules

        Parameters
        ----------

        df: DataFrame
            list of transitions
            
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)


        '''
        if __debug__:
            printdbg(
                'called _add_EvibErot_RADIS_cls1(calc_Evib_harmonic_anharmonic={0})'.format(calc_Evib_harmonic_anharmonic))

        if calc_Evib_harmonic_anharmonic:
            raise NotImplementedError

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too

        if self.verbose>=2:
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Check energy levels are here
        for iso in self._get_isotope_list():
            if not iso in self.parsum_calc[molecule]:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib_RADIS_cls1_1iso(df, iso):
            ''' Calculate Evib & Erot for a given isotope (energies are specific
            to a given isotope) '''
            # TODO: implement with map() instead (much faster!! see get_Evib_CDSD_* )

#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            energies = self.get_energy_levels(molecule, iso, state)
        # TODO: for multi-molecule mode: add loops on molecules and states too

            # only keep vibrational energies
            index = ['viblvl']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)

            # Calculate vibrational / rotational levels for all transitions
            def fillEvibu(r):
                '''
                Note: v, j, is a partition and we just did a groupby(these)
                # so all r.vu are the same

                Implementation
                ------
                r.polyu.iloc[0],r.wangu.iloc[0],r.ranku.iloc[0]  : [0] because they're
                            all the same
                r.ju.iloc[0]  not necessary (same Tvib) but explicitely mentionning it
                         yields a x20 on performances (60s -> 3s)
                (probably faster since neq==0.9.20) (radis<1.0)
                '''
                viblvl = vib_lvl_name_hitran_class1(r.vu.iloc[0])
                r['Evibu'] = energies.at[viblvl, 'Evib']

                return r

            def fillEvibl(r):
                # Not: p, c, j, n is a partition and we just did a groupby(these)
                # so all r.vl, etc. are the same
                viblvl = vib_lvl_name_hitran_class1(r.vl.iloc[0])
                r['Evibl'] = energies.at[viblvl, 'Evib']

                return r

#            try:
            df = df.groupby(by=['vu']).apply(fillEvibu)
            df = df.groupby(by=['vl']).apply(fillEvibl)
#            except KeyError:
#                printr("{0} -> An error (see below) occured that usually ".format(sys.exc_info()[1]) +
#                       "happens when the energy level is not referenced in the database. " +
#                       "Check your partition function calculator, and energies " +
#                       "for isotope {0} (Factory.parsum_calc[{0}][{1}][{2}].df)".format(
#                    molecule, iso, state))
#                raise

            # Another version that failed because twice slower than apply() in that case
            # ~ keep it for information
    #        try:
    #            dgb = df.groupby(by=['vu'])
    #            for vu, dg in dgb: #indices.items():
    #                idx = dgb.indices[vu]
    #                j0 = dg['ju'].iloc[0]     # they all have the same Evib anyway
    #                Evib = energies.at[(vu, j0),'Evib']
    #                df.loc[idx, 'Evibu'] = Evib
    #
    #            dgb = df.groupby(by=['vl'])
    #            for vl, dg in dgb: #indices.items():
    #                idx = dgb.indices[vl]
    #                j0 = dg['jl'].iloc[0]     # they all have the same Evib anyway
    #                Evib = energies.at[(vl, j0),'Evib']
    #                df.loc[idx, 'Evibl'] = Evib

            return df.loc[:, ['Evibl', 'Evibu']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib_RADIS_cls1_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936

        # Slower than the version below:
        df['Evibl'] = np.nan
        df['Evibu'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evibl', 'Evibu']] = get_Evib_RADIS_cls1_1iso(df.loc[idx], iso)

        # Get rotational energy: better recalculate than look up the database (much faster!)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        assert np.isnan(df.Evibu).sum() == 0
        assert np.isnan(df.Evibl).sum() == 0
        
        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        return  # None: Dataframe updated

    def _add_Evib123Erot_RADIS_cls5(self, df):
        ''' Calculate Evib & Erot in dataframe for HITRAN class 5 (linear triatomic
        with Fermi degeneracy... = CO2! ) molecules

        Parameters
        ----------

        df: DataFrame
            list of transitions
        
        Other Parameters
        ----------------
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)


        '''
        if __debug__:
            printdbg(
                'called _add_Evib123Erot_RADIS_cls5()')

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too

        if self.verbose>=2:
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Check energy levels are here
        for iso in self._get_isotope_list(molecule):
            if not iso in self.parsum_calc[molecule]:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib123_RADIS_cls5_1iso(df, iso):
            ''' Calculate Evib & Erot for a given isotope (energies are specific
            to a given isotope)

            Notes
            -----

            We comb the Line Database with groups of same vibrational level,
            and fetch the corresponding vibrational energy from the Energy Level
            Database.
            '''
            # TODO: implement with map() instead (much faster!! see get_Evib_CDSD_* )

#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            # Get the Energy Level Database
            energies = self.get_energy_levels(molecule, iso, state)

            # only keep vibrational energies
            index = ['viblvl']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)

            # Calculate vibrational / rotational levels for all transitions
            def fillEvib123u(r):
                ''' Add vibrational energy Evib1, Evib2, Evib3 for the levels
                in group r.

                Group r corresponds to levels of a same (v1, v2, l2, v3): they
                have the same vibrational energy.

                Notes
                -----

                (v1, v2, l2, v3, j) is a partition and we just did a groupby(these)
                # so all r.vu are the same

                Implementation:

                How to fetch the corresponding rovib level in the Energy Database? ::

                    r.polyu.iloc[0],r.wangu.iloc[0],r.ranku.iloc[0]  : [0] because they're
                                all the same
                    r.ju.iloc[0]  not necessary (same Evib) but explicitely mentionning it
                             yields a x20 on performances (60s -> 3s)
                In 0.9.20 the energy database was reduced to vibrational energies only
                (probably faster since neq==0.9.20) (radis<1.0)
                '''
                viblvl = vib_lvl_name_hitran_class5(r.v1u.iloc[0],
                                                    r.v2u.iloc[0],
                                                    r.l2u.iloc[0],
                                                    r.v3u.iloc[0])

                # Fill group r with vibrational energy of 1st rovibrational
                # level in the group
                r['Evib1u'] = energies.at[viblvl, 'Evib1']
                r['Evib2u'] = energies.at[viblvl, 'Evib2']
                r['Evib3u'] = energies.at[viblvl, 'Evib3']

                return r

            def fillEvib123l(r):
                ''' cf description above. Same here for lower levels in energy'''
                # Not: (v1, v2, l2, v3, j) is a partition and we just did a groupby(these)
                # so all r.vl, etc. are the same
                viblvl = vib_lvl_name_hitran_class5(r.v1l.iloc[0],
                                                    r.v2l.iloc[0],
                                                    r.l2l.iloc[0],
                                                    r.v3l.iloc[0])

                r['Evib1l'] = energies.at[viblvl, 'Evib1']
                r['Evib2l'] = energies.at[viblvl, 'Evib2']
                r['Evib3l'] = energies.at[viblvl, 'Evib3']

                return r

            df = df.groupby(by=['v1u', 'v2u', 'l2u', 'v3u']).apply(
                fillEvib123u)
            df = df.groupby(by=['v1l', 'v2l', 'l2l', 'v3l']).apply(
                fillEvib123l)

            return df.loc[:, ['Evib1l', 'Evib2l', 'Evib3l', 'Evib1u', 'Evib2u', 'Evib3u']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib123_RADIS_cls5_1iso(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936

        # Slower than the version below:
        df['Evib1l'] = np.nan
        df['Evib2l'] = np.nan
        df['Evib3l'] = np.nan
        df['Evib1u'] = np.nan
        df['Evib2u'] = np.nan
        df['Evib3u'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evib1l', 'Evib2l', 'Evib3l', 'Evib1u', 'Evib2u', 'Evib3u']
            ] = get_Evib123_RADIS_cls5_1iso(df.loc[idx], iso)

        # Add total vibrational energy too (doesnt cost much, and can plot populations in spectrum)
        df['Evibu'] = df.Evib1u + df.Evib2u + df.Evib3u
        df['Evibl'] = df.Evib1l + df.Evib2l + df.Evib3l

        # Get rotational energy: better recalculate than look up the database (much faster!)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        assert np.isnan(df.Evib1u).sum() == 0
        assert np.isnan(df.Evib2u).sum() == 0
        assert np.isnan(df.Evib3u).sum() == 0
        assert np.isnan(df.Evib1l).sum() == 0
        assert np.isnan(df.Evib2l).sum() == 0
        assert np.isnan(df.Evib3l).sum() == 0
        
        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        return  # None: Dataframe updated

    def _add_Evib123Erot_RADIS_cls5_harmonicanharmonic(self, df):
        ''' Calculate Evib & Erot in dataframe for HITRAN class 5 (linear triatomic
        with Fermi degeneracy... = CO2! ) molecules

        Parameters
        ----------

        df: DataFrame
            list of transitions
        

        '''
        if __debug__:
            printdbg(
                'called _add_Evib123Erot_RADIS_cls5_harmonicanharmonic()')

        molecule = self.input.molecule
        state = self.input.state           # electronic state
        # TODO: for multi-molecule mode: add loops on molecules and states too

        if self.verbose>=2:
            printg('Fetching vib / rot energies for all {0} transitions'.format(len(df)))
            t0 = time()

        # Check energy levels are here
        for iso in self._get_isotope_list(molecule):
            if not iso in self.parsum_calc[molecule]:
                raise AttributeError('No Partition function calculator defined for isotope {0}'.format(iso)
                                     + '. You need energies to calculate a non-equilibrium spectrum!'
                                     + ' Fill the levels parameter in your database definition, '
                                     + ' with energies of known format: {0}'.format(KNOWN_LVLFORMAT)
                                     + '. See SpectrumFactory.load_databank() help for more details')

        def get_Evib123_RADIS_cls5_1iso_ah(df, iso):
            ''' Calculate Evib & Erot for a given isotope (energies are specific
            to a given isotope). Returns harmonic, anharmonic components

            Notes
            -----

            We comb the Line Database with groups of same vibrational level,
            and fetch the corresponding vibrational energy from the Energy Level
            Database.
            '''
            # TODO: implement with map() instead (much faster!! see get_Evib_CDSD_* )

#            # (dev) HACK pandas #2936
#            if iso == -1:
#                return df

            # Get the Energy Level Database
            energies = self.get_energy_levels(molecule, iso, state)

            # only keep vibrational energies
            index = ['viblvl']
            energies = energies.drop_duplicates(index, inplace=False)
            # (work on a copy)

            # reindexing to get a direct access to level database (instead of using df.v1==v1 syntax)
            energies.set_index(index, inplace=True)

            # Calculate vibrational / rotational levels for all transitions
            def fillEvib123u(r):
                ''' Treanor version of the parser above.

                Add both the harmonic and anharmonic components of the vibrational
                energies Evib1_h, Evib1_a, Evib2_h, etc. for the levels in group r

                Group r corresponds to levels of a same (v1, v2, l2, v3): they
                have the same vibrational energy.

                Notes
                -----

                (v1, v2, l2, v3, j) is a partition and we just did a groupby(these)
                # so all r.vu are the same

                Implementation:

                How to fetch the corresponding rovib level in the Energy Database? ::

                    r.polyu.iloc[0],r.wangu.iloc[0],r.ranku.iloc[0]  : [0] because they're
                                all the same
                    r.ju.iloc[0]  not necessary (same Evib) but explicitely mentionning it
                             yields a x20 on performances (60s -> 3s)
                    In 0.9.19 the energy database was reduced to vibrational energies only

                '''
                viblvl = vib_lvl_name_hitran_class5(r.v1u.iloc[0],
                                                    r.v2u.iloc[0],
                                                    r.l2u.iloc[0],
                                                    r.v3u.iloc[0])

                r['Evib1u_h'] = energies.at[viblvl, 'Evib1_h']
                r['Evib1u_a'] = energies.at[viblvl, 'Evib1_a']
                r['Evib2u_h'] = energies.at[viblvl, 'Evib2_h']
                r['Evib2u_a'] = energies.at[viblvl, 'Evib2_a']
                r['Evib3u_h'] = energies.at[viblvl, 'Evib3_h']
                r['Evib3u_a'] = energies.at[viblvl, 'Evib3_a']
                return r

            def fillEvib123l(r):
                ''' cf above '''
                viblvl = vib_lvl_name_hitran_class5(r.v1l.iloc[0],
                                                    r.v2l.iloc[0],
                                                    r.l2l.iloc[0],
                                                    r.v3l.iloc[0])

                r['Evib1l_h'] = energies.at[viblvl, 'Evib1_h']
                r['Evib1l_a'] = energies.at[viblvl, 'Evib1_a']
                r['Evib2l_h'] = energies.at[viblvl, 'Evib2_h']
                r['Evib2l_a'] = energies.at[viblvl, 'Evib2_a']
                r['Evib3l_h'] = energies.at[viblvl, 'Evib3_h']
                r['Evib3l_a'] = energies.at[viblvl, 'Evib3_a']
                return r

            df = df.groupby(by=['v1u', 'v2u', 'l2u', 'v3u']).apply(
                fillEvib123u)
            df = df.groupby(by=['v1l', 'v2l', 'l2l', 'v3l']).apply(
                fillEvib123l)
            
            return df.loc[:, ['Evib1l_h', 'Evib1l_a', 'Evib2l_h', 'Evib2l_a', 'Evib3l_h', 'Evib3l_a',
                              'Evib1u_h', 'Evib1u_a', 'Evib2u_h', 'Evib2u_a', 'Evib3u_h', 'Evib3u_a']]

#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = (-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby('iso').apply(lambda x: get_Evib123_RADIS_cls5_1iso_ah(x, x.name))
#        df = df.iloc[1:]                 # HACK pandas #2936

        # Slower than the version below:
        df['Evib1l_h'] = np.nan
        df['Evib1l_a'] = np.nan
        df['Evib2l_h'] = np.nan
        df['Evib2l_a'] = np.nan
        df['Evib3l_h'] = np.nan
        df['Evib3l_a'] = np.nan
        df['Evib1u_h'] = np.nan
        df['Evib1u_a'] = np.nan
        df['Evib2u_h'] = np.nan
        df['Evib2u_a'] = np.nan
        df['Evib3u_h'] = np.nan
        df['Evib3u_a'] = np.nan
        for iso, idx in df.groupby('iso').indices.items():
            df.loc[idx, ['Evib1l_h', 'Evib1l_a', 'Evib2l_h', 'Evib2l_a', 'Evib3l_h', 'Evib3l_a',
                       'Evib1u_h', 'Evib1u_a', 'Evib2u_h', 'Evib2u_a', 'Evib3u_h', 'Evib3u_a']
                ] = get_Evib123_RADIS_cls5_1iso_ah(df.loc[idx], iso)

        # Add total vibrational energy too (doesnt cost much, and can plot populations in spectrum)
        df['Evibu_a'] = df.Evib1u_a + df.Evib2u_a + df.Evib3u_a
        df['Evibu_h'] = df.Evib1u_h + df.Evib2u_h + df.Evib3u_h
        df['Evibl_a'] = df.Evib1l_a + df.Evib2l_a + df.Evib3l_a
        df['Evibl_h'] = df.Evib1l_h + df.Evib2l_h + df.Evib3l_h
        df['Evib1u'] = df.Evib1u_h + df.Evib1u_a
        df['Evib1l'] = df.Evib1l_h + df.Evib1l_a
        df['Evib2u'] = df.Evib2u_h + df.Evib2u_a
        df['Evib2l'] = df.Evib2l_h + df.Evib2l_a
        df['Evib3u'] = df.Evib3u_h + df.Evib3u_a
        df['Evib3l'] = df.Evib3l_h + df.Evib3l_a
        df['Evibu'] = df.Evib1u + df.Evib2u + df.Evib3u
        df['Evibl'] = df.Evib1l + df.Evib2l + df.Evib3l

        # Get rotational energy: better recalculate than look up the database (much faster!)
        df['Erotu'] = df.Eu - df.Evibu
        df['Erotl'] = df.El - df.Evibl

        assert np.isnan(df.Evib1u).sum() == 0
        assert np.isnan(df.Evib2u).sum() == 0
        assert np.isnan(df.Evib3u).sum() == 0
        assert np.isnan(df.Evib1l).sum() == 0
        assert np.isnan(df.Evib2l).sum() == 0
        assert np.isnan(df.Evib3l).sum() == 0
        
        if self.verbose>=2:
            printg('Fetched energies in {0:.0f}s'.format(time()-t0))

        return df

    def _add_ju(self, df):
        ''' Calculate J'    (upper state)

        Returns
        -------
        
        None
            df is updated automatically with column ``'ju'``

        Notes
        -----

        Reminder::

            P branch: J' - J'' = -1
            Q branch: J' - J'' = 0
            R branch: J' - J'' = 1
            
        P, Q, R are replaced by -1, 0, 1 in the DataFrame to ensure that all 
        terms are numeric (improves performances)

        '''
        if df.dtypes['branch'] != np.int64:
            raise DeprecationWarning('For performance purpose, numeric (-1, 0, 1) '+\
                                     'format for (P, Q, R) branch is now required. '+\
                                     'If using cache files, regenerate them?')

#        df['ju'] = df.jl
#        df.loc[df.branch=='P','ju'] -= 1
#        df.loc[df.branch=='R','ju'] += 1

        # slightly less readable but ~ 20% faster than above:
        dgb = df.groupby('branch')
        df['ju'] = df.jl
        for branch, idx in dgb.indices.items():
            if branch == -1:  # 'P':
                df.loc[idx, 'ju'] -= 1
            if branch == 1:   #'R':
                df.loc[idx, 'ju'] += 1

        return None

    def _add_Eu(self, df):
        ''' Calculate upper state energy 
        
        Returns
        -------
        
        None:
            df is updated automatically with new column ``'Eu'``
        '''

        # Get upper state energy
        df['Eu'] = df.El + df.wav

        return None

    def _check_noneq_parameters(self, vib_distribution, singleTvibmode):
        ''' Make sure database has non equilibrium quantities (Evib, Erot, etc.)
        '''

        df = self.df0
        if len(df) == 0:
            return      # no lines

        # Make sure database has pre-computed non equilibrium quantities
        # (Evib, Erot, etc.)
        calc_Evib_harmonic_anharmonic = (vib_distribution in ['treanor'])

        if singleTvibmode:
            if (not 'Evib' in df or
                    calc_Evib_harmonic_anharmonic and not all_in(['Evib_a', 'Evib_h'], df)):
                self._calc_noneq_parameters(calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)
        else:
            if (not all_in(['Evib1', 'Evib2', 'Evib3'], df) or
                calc_Evib_harmonic_anharmonic and not all_in(['Evib1_a', 'Evib1_h', 'Evib2_a',
                                         'Evib2_h', 'Evib3_a', 'Evib3_h'], df)):
                self._calc_noneq_parameters(
                    singleTvibmode=False, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)

        if not 'Aul' in df:
            self._calc_weighted_trans_moment()
            self._calc_einstein_coefficients()
            
    def _calc_noneq_parameters(self, singleTvibmode=True, calc_Evib_harmonic_anharmonic=False):
        ''' Update database with Evib, Erot, and degeneracies
        
        Parameters
        ----------
        
        singleTvibmode: boolean
            switch between 1 Tvib and 3 Tvib mode
        
        calc_Evib_harmonic_anharmonic: boolean
            if ``True``, calculate harmonic and anharmonic components of 
            vibrational energies (for Treanor distributions)

        Notes
        -----

        Update in 0.9.16: assign bands by default too '''

        if __debug__:
            printdbg('called _calc_noneq_parameters(singleTvibmode=' +
                     '{0},calc_Evib_harmonic_anharmonic={1})'.format(singleTvibmode, calc_Evib_harmonic_anharmonic))

        df = self.df0

        # ... Make sure upper J' is calculated  (needed to compute populations)
        if not 'ju' in df:
            self._add_ju(df)

        # ... Make sure upper energy level is calculated (needed to compute populations)
        if not 'Eu' in df:
            self._add_Eu(df)

        # ... Make sure Evib / Erot are calculated
        if singleTvibmode:
            if ((not all_in(['Evibu', 'Erotu', 'Evibl', 'Erotl'], df)) or 
                calc_Evib_harmonic_anharmonic and not all_in(['Evibu_a', 'Evibu_h', 'Erotu_a', 'Erotu_h',
                                         'Evibl_a', 'Evibl_h', 'Erotl_a', 'Erotl_h'], df)):
                self._add_EvibErot(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)
        else:
            if (not all_in(['Evib1u', 'Evib2u', 'Evib3u', 'Erotu',
                           'Evib1l', 'Evib2l', 'Evib3l', 'Erotl'], df) or
                calc_Evib_harmonic_anharmonic and not all_in(['Evib1u_a', 'Evib1u_h', 'Erotu_a', 'Erotu_h',
                                         'Evib1l_a', 'Evib1l_h', 'Erotl_a', 'Erotl_h',
                                         'Evib2u_a', 'Evib2u_h', 'Evib3u_a', 'Evib3u_h',
                                         'Evib2l_a', 'Evib2l_h', 'Erot3l_a', 'Erot3l_h'], df)):
                self._add_Evib123Erot(df, calc_Evib_harmonic_anharmonic=calc_Evib_harmonic_anharmonic)

#        # ... Assign bands

        # Look up results
        tol = -1e-4  # tolerance for negative energies (in cm-1)
        if not ((df.Erotu > tol).all() and (df.Erotl > tol).all()):
            self.warn('There are negative rotational energies in the database',
                      'NegativeEnergiesWarning')

        # ... Make sure degeneracies are calculated
        if not all_in(['gju', 'gjl', 'gvibu', 'gvibl', 'gu', 'gl'], df):
            df = self._calc_degeneracies(df)

        # Update main database
        self.df0 = df

        return

    def _calc_degeneracies(self, df):
        ''' Calculate vibrational and rotational degeneracies
        
        See Also
        --------
        
        :func:`~radis.db.degeneracies.gs`, :func:`~radis.db.degeneracies.gi`
        '''
        from radis.db.degeneracies import gs, gi

#        levelsfmt = self.params.levelsfmt
        dbformat = self.params.dbformat

        # Rotational + state specific degeneracy (J + isotope dependant)
        df['gju'] = (2*df.ju+1)
        df['gjl'] = (2*df.jl+1)

        dgb = df.groupby(by=['id', 'iso'])
        for (id, iso), idx in dgb.indices.items():
            _gs = gs(id, iso)
            # TODO: slightly wrong for the moment. There can be different degeneracies. 
            # Look up if level is symmetric()
            if isinstance(_gs, tuple):
                if id not in [2]: # CO2, CO
                    raise NotImplementedError
                # normally we should find whether the level is symmetric 
                # or asymmetric. Here we just assume it's symmetric, because 
                # CO2 asymmetric levels dont exist (gs=0) and they should be
                # in the line database. APPROXIMATION! (forbidden transitions?)
                _gs = _gs[0]
            
            dg = df.loc[idx]
            _gi = gi(id, iso)
            df.loc[idx, 'grotu'] = dg.gju * _gs * _gi
            df.loc[idx, 'grotl'] = dg.gjl * _gs * _gi
            
            if radis.DEBUG_MODE:
                assert (df.loc[idx, 'id'] == id).all()
                assert (df.loc[idx, 'iso'] == iso).all()
                


        # %%

        # A molecule dependant assignation of Vibrational degeneracy
        # Discarded as HITRAN is rovibrational complete (see below)
#        def add_gvib(r):
#            ''' Add degeneracies for lines in ``r``, which correspond to a
#            unique molecule (as ``add_gvib`` was applied to ``groupby('id')``) '''
#            # TODO: change to 1 in any case as HITRAN has complete assigment
#            # of rovibrational levels '''
#            M = r.id.iloc[0]
#            mol = get_molecule(M)
#
#            # CO2
#            if mol == 'CO2':
#                if levelsfmt == 'cdsd':
#                    raise NotImplementedError()
#                elif levelsfmt == 'cdsd-pcN':
#                    gvibu = 1          # (p,j,c,N) is an injective nomenclature
#                    gvibl = 1          # (p,j,c,N) is an injective nomenclature
#                elif levelsfmt == 'radis':
#                    gvibu = 1   # r.v2u+1   # v2 levels have a degeneracy
#                    gvibl = 1   # r.v2l+1   # v2 levels have a degeneracy
#                else:
#                    raise NotImplementedError('unknown format: {0}'.format(levelsfmt))
#            # Diatomic molecules
#            elif mol in HITRAN_CLASS1+HITRAN_CLASS2+HITRAN_CLASS3:
#                gvibu = 1
#                gvibl = 1
#            else:
#                raise NotImplementedError('Not implemented molecule: {0}'.format(mol))
#
#            r['gvibu'] = gvibu
#            r['gvibl'] = gvibl
#
#            return r
#        df = df.groupby(by=['id']).apply(add_gvib)

        if dbformat in ['hitran', 'cdsd', 'cdsd4000']:
            # In HITRAN, AFAIK all molecules have a complete assignment of rovibrational
            # levels hence gvib=1 for all vibrational levels.
            #
            # Complete rovibrational assignment would not be True, for instance, for
            # bending levels of CO2 if all levels are considered degenerated
            # (with a v2+1 degeneracy)
            df['gvibu'] = 1
            df['gvibl'] = 1
        else:
            raise NotImplementedError(
                'vibrational degeneracy assignation for dbformat={0}'.format(dbformat))

        # Total
        df['gu'] = df.gvibu * df.grotu
        df['gl'] = df.gvibl * df.grotl

        return df

    def _calc_weighted_trans_moment(self):
        ''' Calculate weighted transition-moment squared R (in ``Debye^2``)

        Returns
        -------

        None:
            ``self.df0`` is updated directly with new column ``Rs2``  .
            R is in ``Debye^2``   (1e-36 ergs.cm3)


        '''

        df = self.df0
        Tref = self.input.Tref

        if self.verbose >= 2:
            t0 = time()
            printg('Calculate weighted transition moment')
            
#        def fill_Qref(x):
#            (id, iso) = x.name
#            if (id, iso) == (-1, -1):   # HACK pandas #2936
#                return x
#            molecule = get_molecule(id)
#            state = self.input.state
#            parsum = self.get_partition_function_calculator(
#                molecule, iso, state)    # partition function
#            x['Qref'] = parsum.at(Tref, update_populations=False)
#            # ... note: do not update the populations here, so populations in the
#            # ... energy level list correspond to the one calculated for T and not Tref
#
#            return x
#            
#        # (dev) HACK pandas #2936
#        # apply() test twice the first group to determine the path to choose. 
#        # until we can force it not to do that (see #2936), we create a fake first 
#        # group
#        first_row = pd.DataFrame(df.iloc[0], index=[-1])     # HACK pandas #2936
#        first_row['iso'] = int(-1)            # HACK pandas #2936
#        first_row['id'] = int(-1)            # HACK pandas #2936
#        df = pd.concat((first_row, df))  # HACK pandas #2936
#        df = df.groupby(['id', 'iso']).apply(fill_Qref)
#        df = df.iloc[1:]                 # HACK pandas #2936

        id_set = df.id.unique()
        iso_set = self._get_isotope_list(self.input.molecule)  #df1.iso.unique()
        if len(id_set) == 1 and len(iso_set) == 1:
            
            # Shortcut if only 1 isotope. We attribute molar_mass & abundance
            # as attributes of the line database, instead of columns. Much 
            # faster!
            
            molecule = get_molecule(id_set[0])
            state = self.input.state
            parsum = self.get_partition_function_calculator(
                molecule, iso_set[0], state)    # partition function
            df.Qref = parsum.at(Tref, update_populations=False)     # stored as attribute, not column    
            assert 'Qref' not in df.columns
            
        else:
            
            # normal method
            # still much faster than the commented groupby().apply() method above
            # (tested + see https://stackoverflow.com/questions/44954514/efficient-way-to-conditionally-populate-elements-in-a-pandas-groupby-object-pos)
                
            dgb = df.groupby(by=['id', 'iso'])
            for (id, iso), idx in dgb.indices.items():
                molecule = get_molecule(id)
                state = self.input.state
                parsum = self.get_partition_function_calculator(
                    molecule, iso, state)    # partition function
                df.at[idx, 'Qref'] = parsum.at(Tref, update_populations=False)
                # ... note: do not update the populations here, so populations in the
                # ... energy level list correspond to the one calculated for T and not Tref
    
                if radis.DEBUG_MODE:
                    assert (df.loc[idx, 'id'] == id).all()
                    assert (df.loc[idx, 'iso'] == iso).all()
                    
        # Get moment
        gl = df.gl
        El = df.El
        nu = df.wav
        Ia = df.Ia
        h = h_CGS  # erg.s
        c = c_CGS
        S = df.int   # reference linetrength
        Qref = df.Qref

        weighted_trans_moment_sq = ((3*h*c/8/pi**3) / nu / (Ia*gl*exp(-hc_k*El/Tref)/Qref)
                                    / (1-exp(-hc_k*nu/Tref)) * 1e36) * S

        df['Rs2'] = weighted_trans_moment_sq

#        # Store lines with weighted trans momet under df0 again
#        self.df0 = df

        if self.verbose >= 2:
            printg('Calculated weighted transition moment in {0:.1f}'.format(time() - t0))
            
        return

    def _calc_einstein_coefficients(self):
        ''' Calculate A_ul, B_lu, B_ul Einstein coefficients from weighted
        transition moments

        Returns
        -------

        None:
            ``self.df0`` is updated directly with new columns ``Aul``, ``Blu``, ``Bul``

        Notes
        -----

        Einstein A coefficient already in database under df0.A
        Difference between df0.A and df0.Aul < 0.5%
        '''

        df = self.df0

        try:
            df['Rs2']
        except KeyError:
            raise KeyError('Weighted transition moment squared not calculated')

        Rs2 = df.Rs2
        gl = df.gl
        gu = df.gu
        nu = df.wav
        h = h_CGS  # erg.s

        # Calculate coefficients
        df['Blu'] = 8*pi**3/(3*h**2)*Rs2*1e-36*1e7      # cm3/(J.s^2)
        df['Bul'] = 8*pi**3/(3*h**2)*gl/gu*Rs2*1e-36*1e7  # cm3/(J.s^2)
        df['Aul'] = 64*pi**4/(3*h)*nu**3*gl/gu*Rs2*1e-36  # s-1

        # Store in first dataframe
        self.df0 = df

        return

    # %% ======================================================================
    # PRIVATE METHODS - APPLY ENVIRONMENT PARAMETERS
    # (all functions that depends upon T or P)
    # (calculates populations, linestrength & radiance, lineshift)
    # (computation: work on df1, called by or after eq_spectrum() )
    # ---------------------------------
    # _calc_lineshift
    # _calc_linestrength_eq
    # _calc_populations_eq
    # _calc_populations_noneq
    # _calc_linestrength_noneq
    # _calc_emission_integral
    # _cutoff_linestrength

    # XXX =====================================================================

    def _calc_lineshift(self):
        ''' Calculate lineshift due to pressure

        Returns
        -------

        None:
            ``self.df1`` is updated directly with new column ``shiftwav``
        '''
        
        if self.verbose >= 2:
            t0 = time()
            printg('Calculating lineshift')

        df = self.df1

        # Calculate
        air_pressure = self.input.pressure_mbar/1013.25  # convert from mbar to atm
        df['shiftwav'] = df.wav.values + (df.Pshft.values*air_pressure)

#        # Store lines with lineshift under df1
#        self.df1 = df

        if self.verbose >= 2:
            printg('Calculated lineshift in {0:.1f}s'.format(time()-t0))
            
        return

    def _calc_linestrength_eq(self, Tgas):
        ''' Calculate linestrength at temperature Tgas correcting the tabulating
        linestrength

        Parameters
        ----------

        Tgas: float (K)
            gas temperature

        Returns
        -------

        None:
            ``self.df1`` is updated directly with new column ``S``

        Notes
        -----

        Internals:

        (some more informations about what this function does)

        Starts with df1 which is still a copy of df0 loaded by
        :meth:`~radis.lbl.loader.DatabankLoader.load_databank`
        Updates linestrength in df1. Cutoff criteria is applied afterwards.

        '''

        Tref = self.input.Tref
        df1 = self.df1

        if len(df1) == 0:
            return      # no lines
        
        if self.verbose >= 2:
            t0 = time()
            printg('Scaling equilibrium linestrength')

        # %% Load partition function values
#        dgb = df1.groupby(by=['id', 'iso'])
#        
#        # ... optimize by filling all with first isotope first
#        id1, iso1 = list(dgb.indices.keys())[0]
#        molecule1 = get_molecule(id1)
#        state = self.input.state
#        parsum1 = self.get_partition_function_interpolator(
#            molecule1, iso1, state)
#        df1['Qref'] = parsum1.at(Tref)
#        df1['Qgas'] = parsum1.at(Tgas)
#        
#        # ... now fill the rest:
#        for (id, iso), idx in dgb.indices.items():
#            if (id, iso) == (id1, iso1):
#                continue
#            molecule = get_molecule(id)
#            state = self.input.state
#            parsum = self.get_partition_function_interpolator(
#                molecule, iso, state)
#            df1.loc[idx, 'Qref'] = parsum.at(Tref)
#            # ... note: do not update the populations here, so populations in the
#            # ... energy level list correspond to the one calculated for T and not Tref
#            df1.loc[idx, 'Qgas'] = parsum.at(Tgas)
        
        id_set = df1.id.unique()
        if len(id_set) == 1:
            id = list(id_set)[0]
            molecule = get_molecule(id)
            iso_set = self._get_isotope_list(molecule)  #df1.iso.unique()
            
            # Shortcut if only 1 molecule, 1 isotope. We attribute molar_mass & abundance
            # as attributes of the line database, instead of columns. Much 
            # faster!
            
            if len(iso_set) == 1:
                state = self.input.state
                parsum = self.get_partition_function_interpolator(
                    molecule, iso_set[0], state)
                df1.Qref = float(parsum.at(Tref))     # attribute, not column
                df1.Qgas = float(parsum.at(Tgas))     # attribute, not column
                assert 'Qref' not in df1.columns
                assert 'Qgas' not in df1.columns
                
            # Else, parse for all isotopes. Use np.take that is very fast
            # Use the fact that isotopes are int, and thus can be considered as 
            # index in an array.
            # ... in the following we exploit this to use the np.take function,
            # ... which is amazingly fast 
            # ... Read https://stackoverflow.com/a/51388828/5622825 to understand more
            
            else:
                    
                iso_arr = list(range(max(iso_set)+1))
                
                Qref_arr = np.empty_like(iso_arr, dtype=np.float64)
                Qgas_arr = np.empty_like(iso_arr, dtype=np.float64)
                for iso in iso_arr:
                    if iso in iso_set:
                        molecule = get_molecule(id)
                        state = self.input.state
                        parsum = self.get_partition_function_interpolator(
                            molecule, iso, state)
                        # ... the trick below is that iso is used as index in the array
                        Qref_arr[iso] = parsum.at(Tref)
                        Qgas_arr[iso] = parsum.at(Tgas)
        
                df1['Qref'] = Qref_arr.take(df1.iso) 
                df1['Qgas'] = Qgas_arr.take(df1.iso)
            
        else:
            raise NotImplementedError('>1 molecule. Can use the np.take trick. Need to '+\
                                      'fallback to pandas.map(dict)')
            # TODO: Implement. Read https://stackoverflow.com/a/51388828/5622825 to understand more
                
        # Note on performance: few times faster than doing a groupby().apply()
        # here. But may raise Keyerrors if base is reindexed ?

        # %% Calculate line strength at desired temperature
        # ----------------------------------------------------------------------

        # This calculation is based on equation (A11) in Rothman 1998: "JQSRT, vol.
        # 60, No. 5, pp. 665-710"
        
        # correct for Partition Function
        line_strength = df1.int*(df1.Qref/df1.Qgas)
        # ratio of Boltzman populations
        line_strength *= exp(-hc_k*df1.El/Tgas)
        # ratio of Boltzman populationsq
        line_strength /= exp(-hc_k*df1.El/Tref)
        # effect of stimulated emission
        line_strength *= (1 - exp(-hc_k*df1.wav/Tgas))
        # effect of stimulated emission
        line_strength /= (1 - exp(-hc_k*df1.wav/Tref))
        df1['S'] = line_strength                # [cm-1/(molecules/cm-2)]

        assert 'S' in self.df1
        
        if self.verbose >= 2:
            printg('Scaled equilibrium linestrength in {0:.1f}s'.format(time()-t0))

        return

    # %%
    def _calc_populations_eq(self, Tgas):
        ''' Calculate upper state population for all active transitions in equilibrium case
        (only used in total power calculation)

        Parameters
        ----------

        Tgas: float (K)
            temperature

        Returns
        -------

        None:
            `nu` is stored in self.df1

        Notes
        -----

        Isotopes: these populations are not corrected for the isotopic abundance,
        i.e, abundance has to be accounted for if used for emission density
        calculations (based on Einstein A coefficient), but not for linestrengths
        (that include the abundance dependency already)

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory._calc_populations_noneq`,
        :meth:`~radis.lbl.base.BaseFactory._calc_populations_noneq_multiTvib`,
        :meth:`~radis.levels.partfunc.RovibPartitionFunction.at`

        '''

        df1 = self.df1
        
        if self.verbose >= 2:
            t0 = time()
            printg('Calculating equilibrium populations')

        # Load partition function values
        dgb = df1.groupby(by=['id', 'iso'])
        
        # ... optimize by filling all with first isotope first
        id1, iso1 = list(dgb.indices.keys())[0]
        molecule1 = get_molecule(id1)
        state = self.input.state
        parsum1 = self.get_partition_function_interpolator(
            molecule1, iso1, state)
        df1['Qgas'] = parsum1.at(Tgas)
        
        # ... now fill the rest:
        for (id, iso), idx in dgb.indices.items():
            if (id, iso) == (id1, iso1):
                continue
            molecule = get_molecule(id)
            state = self.input.state
            parsum = self.get_partition_function_interpolator(
                molecule, iso, state)
            df1.loc[idx, 'Qgas'] = parsum.at(Tgas)

            if radis.DEBUG_MODE:
                assert (df1.loc[idx, 'id'] == id).all()
                assert (df1.loc[idx, 'iso'] == iso).all()
                
        # Calculate degeneracies
        # ----------------------------------------------------------------------

        if not 'ju' in df1:
            self._add_ju(df1)

        if not 'gu' in df1:
            df1 = self._calc_degeneracies(df1)

        # ... Make sure upper energy level is calculated (needed to compute populations)
        if not 'Eu' in df1:
            self._add_Eu(df1)

        # Calculate population
        # ----------------------------------------------------------------------
        # equilibrium: Boltzmann in any case
        df1['nu'] = df1.gu.values * exp(-hc_k*df1.Eu.values/Tgas) / df1.Qgas.values

        assert 'nu' in self.df1

        if self.verbose >= 2:
            printg('Calculated equilibrium populations in {0:.1f}s'.format(time()-t0))

        return

    # %%
    def _calc_populations_noneq(self, Tvib, Trot, vib_distribution='boltzmann',
                                rot_distribution='boltzmann', overpopulation=None):
        ''' Calculate upper and lower state population for all active transitions,
        as well as all levels (through :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq`)

        Parameters
        ----------

        Tvib, Trot: float (K)
            temperatures

        vib_distribution: ``'boltzmann'``, ``'treanor'``
            vibrational level distribution

        rot_distribution: ``'boltzmann'``
            rotational level distribution

        overpopulation: dict, or ``None``
            dictionary of overpopulation factors for vibrational levels

        Returns
        -------

        None
            `nu`, `nl`, `nu_vib`, `nl_vib` are stored in self.df1

        Notes
        -----

        Isotopic abundance:

        Note that these populations are not corrected for the isotopic abundance,
        i.e, abundance has to be accounted for if used for emission density
        calculations (based on Einstein A coefficient), but not for linestrengths
        (that include the abundance dependency already)

        All populations:

        This method calculates populations of emitting and absorbing levels.
        Populations of all levels (even the one not active on the spectral
        range considered) are calculated during the Partition function calculation.
        See: :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq`

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory._calc_populations_eq`,
        :meth:`~radis.lbl.base.BaseFactory._calc_populations_noneq_multiTvib`,
        :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq`

        '''

        # Check inputs
        if overpopulation is None:
            overpopulation = {}

        df = self.df1

        if self.verbose >= 2:
            t0 = time()
            printg('Calculating nonequilibrium populations')

        if len(df) == 0:
            return      # no lines in database, no need to go further

        # Get vibrational levels for both upper and lower states
        if not ('viblvl_u' in df and not 'viblvl_l' in df):
            from radis.lbl.bands import add_bands
            add_bands(df, dbformat=self.params.dbformat, lvlformat=self.params.levelsfmt,
                      verbose=self.verbose)
            assert 'viblvl_u' in df
            assert 'viblvl_l' in df
            
        # partition function
        # ... unlike the (tabulated) equilibrium case, here we recalculate it from
        # scratch
        # %%
        
        id_set = df.id.unique()
        iso_set = self._get_isotope_list()  #df1.iso.unique()
        if len(id_set) == 1 and len(iso_set) == 1:
            id = id_set[0]
            iso = iso_set[0]
            
            # Shortcut if only 1 molecule, 1 isotope. We attribute molar_mass & abundance
            # as attributes of the line database, instead of columns. Much 
            # faster!
            
            molecule = get_molecule(id)
            state = self.input.state
            parsum = self.get_partition_function_calculator(
                molecule, iso, state)
            Q, Qvib, dfQrot = parsum.at_noneq(Tvib, Trot,
                                              vib_distribution=vib_distribution,
                                              rot_distribution=rot_distribution,
                                              overpopulation=overpopulation,
                                              returnQvibQrot=True,
                                              update_populations=self.misc.export_populations)
            # ... make sure PartitionFunction above is calculated with the same
            # ... temperatures, rovibrational distributions and overpopulations
            # ... as the populations of active levels (somewhere below)
            df.Qvib = Qvib
            df.Q = Q
            assert 'Qvib' not in df.columns
            assert 'Q' not in df.columns

            # reindexing to get a direct access to Qrot database
            # create the lookup dictionary
            # dfQrot index is already 'viblvl'
            dfQrot_dict = dict(list(zip(dfQrot.index, dfQrot.Qrot)))
            
            dg = df.loc[:]

            # Add lower state Qrot
            dg_sorted = dg.set_index(['viblvl_l'], inplace=False)
            df.loc[:, 'Qrotl'] = dg_sorted.index.map(dfQrot_dict.get).values
            # Add upper state energy
            dg_sorted = dg.set_index(['viblvl_u'], inplace=False)
            df.loc[:, 'Qrotu'] = dg_sorted.index.map(dfQrot_dict.get).values 

            # ... note: the .map() version is about 3x faster than 
            # ... dg.groupby('viblvl_l').apply(lambda x: dfQrot_dict[x.name])

        else:
            
            # Normal version
            # TODO: optimize by filling for first isotope first (see equilibrium case).
            # TODO: use the np.take() trick if 1 molecule only
                    
            dgb = df.groupby(by=['id', 'iso'])
            
            for (id, iso), idx in dgb.indices.items():
                # Get partition function for all lines
                molecule = get_molecule(id)
                state = self.input.state
                parsum = self.get_partition_function_calculator(
                    molecule, iso, state)
                Q, Qvib, dfQrot = parsum.at_noneq(Tvib, Trot,
                                                  vib_distribution=vib_distribution,
                                                  rot_distribution=rot_distribution,
                                                  overpopulation=overpopulation,
                                                  returnQvibQrot=True,
                                                  update_populations=self.misc.export_populations)
                # ... make sure PartitionFunction above is calculated with the same
                # ... temperatures, rovibrational distributions and overpopulations
                # ... as the populations of active levels (somewhere below)
                df.at[idx, 'Qvib'] = Qvib
                df.at[idx, 'Q'] = Q
    
                # reindexing to get a direct access to Qrot database
                # create the lookup dictionary
                # dfQrot index is already 'viblvl'
                dfQrot_dict = dict(list(zip(dfQrot.index, dfQrot.Qrot)))
                
                dg = df.loc[idx]
    
                # Add lower state Qrot
                dg_sorted = dg.set_index(['viblvl_l'], inplace=False)
                df.loc[idx, 'Qrotl'] = dg_sorted.index.map(dfQrot_dict.get).values
                # Add upper state energy
                dg_sorted = dg.set_index(['viblvl_u'], inplace=False)
                df.loc[idx, 'Qrotu'] = dg_sorted.index.map(dfQrot_dict.get).values 
    
                # ... note: the .map() version is about 3x faster than 
                # ... dg.groupby('viblvl_l').apply(lambda x: dfQrot_dict[x.name])
    
                if radis.DEBUG_MODE:
                    assert (df.loc[idx, 'id'] == id).all()
                    assert (df.loc[idx, 'iso'] == iso).all()

# %%

        #  Derive populations
        # ... vibrational distribution
        if vib_distribution == 'boltzmann':
            df['nu_vib'] = (df.gvibu * exp(-hc_k*df.Evibu/Tvib) / df.Qvib)
            df['nl_vib'] = (df.gvibl * exp(-hc_k*df.Evibl/Tvib) / df.Qvib)
        elif vib_distribution == 'treanor':
            df['nu_vib'] = (
                df.gvibu * exp(-hc_k*(df.Evibu_h/Tvib+df.Evibu_a/Trot)) / df.Qvib)
            df['nl_vib'] = (
                df.gvibl * exp(-hc_k*(df.Evibl_h/Tvib+df.Evibl_a/Trot)) / df.Qvib)
        else:
            raise ValueError(
                'Unknown vibrational distribution: {0}'.format(vib_distribution))

        # ... Add vibrational-specific overpopulation factors
        if overpopulation != {}:
            for viblvl, ov in overpopulation.items():
                if ov != 1:
                    df.loc[df.viblvl_u == viblvl, 'nu_vib'] *= ov
                    df.loc[df.viblvl_l == viblvl, 'nl_vib'] *= ov

        # ... Rotational distributions
        if rot_distribution == 'boltzmann':
            df['nu_rot'] = df.grotu * exp(-df.Erotu*hc_k/Trot) / df.Qrotu
            df['nl_rot'] = df.grotl * exp(-df.Erotl*hc_k/Trot) / df.Qrotl
        else:
            raise ValueError(
                'Unknown rotational distribution: {0}'.format(rot_distribution))

        # ... Total
        df['nu'] = df.nu_vib * df.nu_rot * (df.Qrotu * df.Qvib / df.Q)
        df['nl'] = df.nl_vib * df.nl_rot * (df.Qrotl * df.Qvib / df.Q)

#        # Store lines with new populations under df1
#        self.df1 = df
        
        assert 'nu' in self.df1
        assert 'nl' in self.df1
        assert not pd.isna(df.nu).any()
        assert not pd.isna(df.nl).any()
        
        if self.verbose >= 2:
            printg('Calculated nonequilibrium populations in {0:.1f}s'.format(time()-t0))

        return

    # %%
    def _calc_populations_noneq_multiTvib(self, Tvib, Trot, vib_distribution='boltzmann',
                                          rot_distribution='boltzmann', overpopulation=None):
        ''' Calculate upper and lower state population for all active transitions,
        as well as all levels (through :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq`)

        Parameters
        ----------

        Tvib, Trot: float (K)
            temperatures

        vib_distribution: ``'boltzmann'``, ``'treanor'``
            vibrational level distribution

        rot_distribution: ``'boltzmann'``
            rotational level distribution

        overpopulation: dict, or ``None``
            dictionary of overpopulation factors for vibrational levels

        Notes
        -----

        Isotopic abundance:

        Note that these populations are not corrected for the isotopic abundance,
        i.e, abundance has to be accounted for if used for emission density
        calculations (based on Einstein A coefficient), but not for linestrengths
        (that include the abundance dependency already)

        All populations:

        This method calculates populations of emitting and absorbing levels.
        Populations of all levels (even the one not active on the spectral
        range considered) are calculated during the Partition function calculation.
        :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq`

        Todo someday:

        - so far it's a 3 Tvib model, hardcoded. make it a N-vibrational model,
          with lists / dictionary?

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory._calc_populations_eq`,
        :meth:`~radis.lbl.base.BaseFactory._calc_populations_noneq`,
        :meth:`~radis.levels.partfunc.RovibPartitionFunction.at_noneq_3Tvib`

        '''

        # Check inputs
        if overpopulation is None:
            raise NotImplementedError(
                'Overpopulation not implemented in multi-Tvib mode')
        Tvib1, Tvib2, Tvib3 = Tvib

        df = self.df1

        if self.verbose >= 2:
            t0 = time()
            printg('Calculating nonequilibrium populations (multiTvib)')

        if len(df) == 0:
            return      # no lines in database, no need to go further

        # partition function
        # ... unlike the (tabulated) equilibrium case, here we recalculate it from
        # scratch

        dgb = df.groupby(by=['id', 'iso'])

        # TODO: optimize with np.take trick (see equilibrium case)
        
        for (id, iso), idx in dgb.indices.items():
            molecule = get_molecule(id)
            state = self.input.state
            parsum = self.get_partition_function_calculator(
                molecule, iso, state)
            Q = parsum.at_noneq_3Tvib(Tvib, Trot,
                                      vib_distribution=vib_distribution,
                                      rot_distribution=rot_distribution,
                                      overpopulation=overpopulation,
                                      update_populations=self.misc.export_populations)
#            df.loc[idx, 'Qvib'] = Qvib
            df.loc[idx, 'Q'] = Q
#            dg_list.append(dg)
            
            if radis.DEBUG_MODE:
                assert (df.loc[idx, 'id'] == id).all()
                assert (df.loc[idx, 'iso'] == iso).all()

        #  Derive populations
        # ... vibrational distribution
        if vib_distribution == 'boltzmann':
            #            df['nu_vib1'] = (df.gvibu * exp(-df.Evib1u*hc_k/Tvib1) / df.Qvib1)
            #            df['nl_vib1'] = (df.gvibl * exp(-df.Evib1l*hc_k/Tvib1) / df.Qvib1)
            #            df['nu_vib2'] = (df.gvibu * exp(-df.Evib2u*hc_k/Tvib2) / df.Qvib2)
            #            df['nl_vib2'] = (df.gvibl * exp(-df.Evib2l*hc_k/Tvib2) / df.Qvib2)
            #            df['nu_vib3'] = (df.gvibu * exp(-df.Evib3u*hc_k/Tvib3) / df.Qvib3)
            #            df['nl_vib3'] = (df.gvibl * exp(-df.Evib3l*hc_k/Tvib3) / df.Qvib3)
            nu_vib1Qvib1 = df.gvibu * exp(-hc_k*df.Evib1u/Tvib1)
            nl_vib1Qvib1 = df.gvibl * exp(-hc_k*df.Evib1l/Tvib1)
            nu_vib2Qvib2 = df.gvibu * exp(-hc_k*df.Evib2u/Tvib2)
            nl_vib2Qvib2 = df.gvibl * exp(-hc_k*df.Evib2l/Tvib2)
            nu_vib3Qvib3 = df.gvibu * exp(-hc_k*df.Evib3u/Tvib3)
            nl_vib3Qvib3 = df.gvibl * exp(-hc_k*df.Evib3l/Tvib3)
        elif vib_distribution == 'treanor':
            nu_vib1Qvib1 = df.gvibu * exp(-hc_k*(df.Evib1u_h/Tvib1+df.Evib1u_a/Trot))
            nl_vib1Qvib1 = df.gvibl * exp(-hc_k*(df.Evib1l_h/Tvib1+df.Evib1l_a/Trot))
            nu_vib2Qvib2 = df.gvibu * exp(-hc_k*(df.Evib2u_h/Tvib2+df.Evib2u_a/Trot))
            nl_vib2Qvib2 = df.gvibl * exp(-hc_k*(df.Evib2l_h/Tvib2+df.Evib2l_a/Trot))
            nu_vib3Qvib3 = df.gvibu * exp(-hc_k*(df.Evib3u_h/Tvib3+df.Evib3u_a/Trot))
            nl_vib3Qvib3 = df.gvibl * exp(-hc_k*(df.Evib3l_h/Tvib3+df.Evib3l_a/Trot))
        else:
            raise ValueError(
                'Unknown vibrational distribution: {0}'.format(vib_distribution))

    # Not Implemented:
#        if overpopulation != {}:
#            if not ('viblvl_u' in df and not 'viblvl_l' in df):
#                from radis.lbl.bands import add_bands
#                df = add_bands(df, dbformat=self.params.dbformat, verbose=self.verbose)
#                assert 'viblvl_u' in df
#                assert 'viblvl_l' in df
#
#            for viblvl, ov in overpopulation.items():
#                if ov != 1:
#                    df.loc[df.viblvl_u==viblvl, 'nu_vib'] *= ov
#                    df.loc[df.viblvl_l==viblvl, 'nl_vib'] *= ov

        # ... Rotational distributions
        # that would require Qrot, which we dont have (NotImplemented
        # for 3 temperatures). Let's just get the total

        # ... Total
        if rot_distribution == 'boltzmann':
            # ... total
            df['nu'] = (nu_vib1Qvib1 * nu_vib2Qvib2 * nu_vib3Qvib3 * df.grotu *
                        exp(-df.Erotu*hc_k/Trot) / df.Q)
            df['nl'] = (nl_vib1Qvib1 * nl_vib2Qvib2 * nl_vib3Qvib3 * df.grotl *
                        exp(-df.Erotl*hc_k/Trot) / df.Q)
        else:
            raise ValueError(
                'Unknown rotational distribution: {0}'.format(rot_distribution))

##        # Store lines with new populations under df0
#        self.df1 = df   # (dev) need to reassign  because of pd.concat
            
        assert 'nu' in self.df1
        assert 'nl' in self.df1

        if self.verbose >= 2:
            printg('Calculated equilibrium populations (multiTvib) in {0:.1f}s'.format(time()-t0))

        return

    def get_lines(self):
        ''' Return lines if self.misc.export_lines is True, else get None '''

        if self.misc.export_lines:
            return self.df1
        else:
            return None

    # %% Get populations
    def get_populations(self, levels='vib'):
        ''' For all molecules / isotopes / electronic states, lookup energy levels
        as calculated in partition function calculators, and (if calculated)
        populations, and returns as a dictionary

        Parameters
        ----------

        levels: ``'vib'``, ``'rovib'``, list of these, or ``None``
            what levels to get. Note that ``'rovib'`` can yield large objects.

        Returns
        -------

        pops: dict
            Structure::

                {molecule: {isotope: {electronic_state: {'vib': pandas Dataframe,    # (copy of) vib levels
                                                         'rovib': pandas Dataframe,  # (copy of) rovib levels
                                                         'Ia': float    # isotopic abundance
                                                         }}}}

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory.get_energy_levels`

        '''

        # Check input
        if levels is None or levels is False:
            return {}
        if isinstance(levels, string_types):
            levels = [levels]

        # To get isotopic abundance
        # placeholder # TODO: replace with attributes of Isotope>ElectronicState objects
        molpar = MolParams()

        pops = {}
        # Loop over molecules, isotopes, electronic states
        for molecule in [self.input.molecule]:
            pops[molecule] = {}

            for isotope in self._get_isotope_list(molecule):
                pops[molecule][isotope] = {}

                id = get_molecule_identifier(molecule)
                # fetch all table directly
                params = molpar.df.loc[(id, isotope)]
                # placeholder # TODO: replace with attributes of Isotope>ElectronicState objects
                Ia = params.abundance

                for electronic_state in list(self.input.state):
                    pops[molecule][isotope][electronic_state] = {}

                    # Add vib or rovib levels
                    energies = self.get_energy_levels(
                        molecule, isotope, electronic_state)
                    for level_type in levels:

                        if level_type == 'vib':
                            assert 'viblvl' in list(energies.keys())
                            # only get one entry per vibrational level
                            pop = energies.drop_duplicates(
                                'viblvl')    # is a copy
                            # remove unecessary keys (all rotational specific)
                            for k in ['E', 'j', 'gj', 'Erot', 'grot', 'n']:
                                try:
                                    del pop[k]
                                except KeyError:
                                    pass

                        elif level_type == 'rovib':
                            pop = energies.copy()       # is a copy

                        else:
                            raise ValueError(
                                'Unknown level type: {0}'.format(level_type))

                        # Store
                        pops[molecule][isotope][electronic_state][level_type] = pop

                    # Add extra information (isotope - electronic state specific)
                    pops[molecule][isotope][electronic_state]['Ia'] = Ia

        # Note: all dataframes should be copies, else it gets dangerous if
        # exported in a Spectrum but still connected to the Factory
        return pops

#    def _get_active_vib_populations(self, df1):
#        ''' Return vibrational populations for all levels featured in given
#        line set.
#        Note that this doesnt give the populations of all levels as non visible
#        levels are not featured '''
#
#        def get_vib_populations_isotope(df1):
#            ''' Populations for one isotope
#
#            Assumes that 'viblvl' is a unique identifier for a vibrational
#            level
#            '''
#
#            if not ('viblvl_u' in df1 and not 'viblvl_l' in df1.keys()):
#                from radis.lbl.bands import add_bands
#                if self.verbose: print('Getting bands on already computed lines')
##                df1 = get_bands(df1, dbformat=self.params.dbformat, verbose=self.verbose)
#                add_bands(df1, dbformat=self.params.dbformat, verbose=self.verbose)
#
#            if not all_in(['viblvl_l', 'viblvl_u', 'nl_vib', 'nu_vib', 'Evibl', 'Evibu'], df1.keys()):
##                if __debug__: printdbg('Missing keys to compute vibrational populations')
#                if self.verbose: print('Missing keys to compute vibrational populations')
#                return {}
#
#            n_l = dict(zip(df1.viblvl_l, df1.nl_vib))  # removes duplicates in the process
#            n = dict(zip(df1.viblvl_u, df1.nu_vib))  # removes duplicates in the process
#            n.update(n_l)      # merge all
#            E_l = dict(zip(df1.viblvl_l, df1.Evibl))  # removes duplicates in the process
#            E = dict(zip(df1.viblvl_u, df1.Evibu))  # removes duplicates in the process
#            E.update(E_l)      # merge all
#            gvib_l = dict(zip(df1.viblvl_l, df1.gvibl))
#            gvib = dict(zip(df1.viblvl_u, df1.gvibu))
#            gvib.update(gvib_l)
#
#            # Export
#            levels = pd.DataFrame({#'viblvl':list(n_u.keys()),
#                               'nvib':list(n.values()),
#                               'gvib':list(gvib.values()),
#                               'Evib':list(E.values())},
#                index=list(E.keys())
#                )
#
#            return levels
#
#        levels = []
#        # Stock by abundance
#        for Ia, dg in df1.groupby(by=['Ia']):
#            dg.is_copy = False  # removes pandas SettingWithCopyWarning
#            levels_iso = get_vib_populations_isotope(dg)
#            if len(levels_iso) > 0:
#                levels_iso['Ia'] = Ia
#                levels.append(levels_iso)
#        if len(levels) > 0:
#            levels = pd.concat(levels)
#        else:
#            levels = {}
#
#        return levels

#    def _get_active_rovib_populations(self, df1):
#        ''' Return rovibrational populations for all levels featured in given
#        line set.
#        Note that this doesnt give the populations of all levels as non visible
#        levels are not featured '''
#
#        def get_rovib_populations_isotope(df1):
#            ''' Populations for one isotope
#
#            Assumes that ('viblvl','j') is a unique identifier for a rovibrational level
#            '''
#
#            if not ('viblvl_u' in df1 and not 'viblvl_l' in df1.keys()):
#                from radis.lbl.bands import add_bands
#                if self.verbose: print('Getting bands on already computed lines')
#                add_bands(df1, dbformat=self.params.dbformat, verbose=self.verbose)
#
#            if not all_in(['viblvl_l', 'viblvl_u', 'jl', 'ju', 'nl', 'nu', 'El', 'Eu'], df1.keys()):
#                if __debug__: printdbg('Missing keys to compute rovibrational populations')
#                return {}
#
#            from radis.misc.basics import merge_rename_columns
#
#            levels = merge_rename_columns(df1, ['viblvl_u', 'ju', 'Eu', 'nu', 'gu', 'gju'],
#                                               ['viblvl_l', 'jl', 'El', 'nl', 'gl', 'gjl'],
#                                               ['viblvl',   'j',  'E',  'n',  'g',  'gj']
#                                               )
#            return levels.set_index(['viblvl', 'j'])
#
#        levels = []
#        # Stock by abundance
#        for Ia, dg in df1.groupby(by=['Ia']):
#            dg.is_copy = False  # removes pandas SettingWithCopyWarning
#            levels_iso = get_rovib_populations_isotope(dg)
#            if len(levels_iso) > 0:
#                levels_iso['Ia'] = Ia
#                levels.append(levels_iso)
#        if len(levels) > 0:
#            levels = pd.concat(levels)
#        else:
#            levels = {}
#
#        return levels

#    def _get_vib_populations_3Tvib(self, df1):
#        ''' Return vibrational populations for all levels featured in given
#        line set.
#        Note that this doesnt give the populations of all levels as non visible
#        levels are not featured '''
#
#        if not ('viblvl_l' in df1 and 'viblvl_u' in df1 and 'nl_vib' in df1 and
#                'nu_vib' in df1 and 'Evibl' in df1 and 'Evibu' in df1):
#            if __debug__: printdbg('Missing keys to compute populations')
#            return {}
#
#        n_l = dict(zip(df1.viblvl_l, df1.nl_vib))  # removes duplicates in the process
#        n_u = dict(zip(df1.viblvl_u, df1.nu_vib))  # removes duplicates in the process
#        n_u.update(n_l)      # merge all
#        E_l = dict(zip(df1.viblvl_l, df1.Evibl))  # removes duplicates in the process
#        E_u = dict(zip(df1.viblvl_u, df1.Evibu))  # removes duplicates in the process
#        E_u.update(E_l)      # merge all
#        #df = pd.DataFrame({'viblvl':n_u.keys(), 'n_vib':n_u.values(), 'Evib':E_u.values()})
#        levels = pd.DataFrame({#'viblvl':list(n_u.keys()),
#                           'nvib':list(n_u.values()),
#                           'Evib':list(E_u.values())},
#            index=list(E_u.keys())
#            )
#
#        return levels

    def _calc_linestrength_noneq(self):
        '''
        Parameters
        ----------

        Pre-requisite:

            lower state population `nl` has already been calculated by
            :meth:`~radis.lbl.base.BaseFactory.calc_populations_noneq`


        Returns
        -------

        None
            Linestrength `S` added in self.df


        Notes
        -----

        Internals:

        (some more informations about what this function does)

        Starts with df1 which is was a copy of df0 loaded by load_databank(),
        with non-equilibrium quantities added and populations already calculated.
        Updates linestrength in df1. Cutoff criteria is applied afterwards.

        See Also
        --------

        :meth:`~radis.lbl.base.BaseFactory.calc_populations_noneq`

        '''

        df = self.df1
        Tref = self.input.Tref

        if len(df) == 0:
            return      # no lines in database, no need to go further

        if self.verbose >= 2:
            t0 = time()
            printg('scale nonequilibrium linestrength')

        try:
            df['nl']
        except KeyError:
            raise KeyError('Calculate populations first')

        # %% Calculation
        
        id_set = df.id.unique()
        iso_set = self._get_isotope_list()  #df1.iso.unique()
        # TODO for multi-molecule code: add above line in the loop
        if len(id_set) == 1 and len(iso_set) == 1:
            
            # Shortcut if only 1 isotope. We attribute molar_mass & abundance
            # as attributes of the line database, instead of columns. Much 
            # faster!
            
            molecule = get_molecule(id_set[0])
            state = self.input.state
            parsum = self.get_partition_function_calculator(
                molecule, iso_set[0], state)    # partition function
            df.Qref = parsum.at(Tref, update_populations=False)     # stored as attribute, not column    
            assert 'Qref' not in df.columns
            
        else:
                    
#            def fill_Qref(r):
#    #            print(r.name)
#                id, iso = r.name
#                if (id, iso) == (-1, -1):    # HACK pandas #2936s
#                    return r
#                molecule = get_molecule(id)
#                state = self.input.state
#                parsum = self.get_partition_function_calculator(
#                    molecule, iso, state)
#                r['Qref'] = parsum.at(Tref, update_populations=False)
#                # ... note: do not update the populations here, so populations in the
#                # ... energy level list correspond to the one calculated for T and not Tref
#                return r
#
#            # (dev) HACK pandas #2936
#            # apply() test twice the first group to determine the path to choose. 
#            # until we can force it not to do that (see #2936), we create a fake first 
#            # group
#            new_row = pd.DataFrame(df.iloc[-1])     # HACK pandas #2936
#            new_row['iso'] = int(-1)            # HACK pandas #2936
#            new_row['id'] = int(-1)            # HACK pandas #2936
#            df = df.append(new_row, ignore_index=True)
#            df = df.groupby(['id', 'iso']).apply(fill_Qref)
#            df = df.iloc[:-1]                 # HACK pandas #2936
            
#            # normal method
#            # still much faster than the commented groupby().apply() method above
#            # (tested + see https://stackoverflow.com/questions/44954514/efficient-way-to-conditionally-populate-elements-in-a-pandas-groupby-object-pos)
#                
            # partition function
            dgb = df.groupby(by=['id', 'iso'])
            for (id, iso), idx in dgb.indices.items():
                molecule = get_molecule(id)
                state = self.input.state
                parsum = self.get_partition_function_calculator(
                    molecule, iso, state)
                df.at[idx, 'Qref'] = parsum.at(Tref, update_populations=False)
                
                if radis.DEBUG_MODE:
                    assert (df.loc[idx, 'id'] == id).all()
                    assert (df.loc[idx, 'iso'] == iso).all()
                
        # Correct linestrength

        # ... populations without abundance dependance (already in linestrength)
        nu = df.nu       # Note: populations are not corrected for abundance
        nl = df.nl
        # ... remove Qref, nref, etc.
        # start from for tabulated linestrength
        line_strength = df.int.copy()

        # ... correct for lower state population
        line_strength /= (df.gl * exp(-hc_k*df.El/Tref)/df.Qref)
        line_strength *= nl

        # ... correct effect of stimulated emission
        line_strength /= (1 - exp(-hc_k*df.wav/Tref))
        line_strength *= (1 - df.gl / df.gu * nu / nl)
        df['S'] = line_strength

#        # %% Store lines with linestrengths under df1
#        self.df1 = df

        if self.verbose >= 2:
            printg('scaled nonequilibrium linestrength in {0:.1f}s'.format(time()-t0))

        return

    # %%
    def _calc_emission_integral(self):
        ''' Calculate Emission Integral

        Emission Integral is a non usual quantity introduced here to have an
        equivalent of Linestrength in emission calculation

        Returns
        -------

        None
            Emission integral `Ei` added in self.df


        emission_integral: (mW/sr)
            emission integral is defined as
            Ei = n_u * A_ul / 4π * DeltaE_ul
                  :      :     :      :
                (#/#)  (s-1) (sr)    (mJ)

            So that the radiance ϵ is:

                ϵ(λ)   =      Ei  *   Phi(λ)  * ntot   * path_length
                 :             :         :       :          :
            mW/cm2/sr/nm    (mW/sr)   (1/nm)   (cm-3)      (cm)


        '''

        df = self.df1

        if self.verbose >= 2:
            t0 = time()
            printg('calculated emission integral')

        if len(df) == 0:
            return      # no lines in database, no need to go further

        try:
            df['nu']
        except KeyError:
            raise KeyError('Calculate populations first')

        # Calculation

        # adim. (#/#) (multiplied by n_tot later)
        n_u = df['nu']
        # correct for abundance
        n_ua = n_u * df.Ia

        A_ul = df['Aul']                # (s-1)

        DeltaE = cm2J(df.wav)           # (cm-1) -> (J)
        Ei = n_ua * A_ul/4/pi * DeltaE   # (W/sr)

        Ei *= 1e3   # (W/sr) -> (mW/sr)
        df['Ei'] = Ei

#        # Store lines with emission integrals under df0
#        self.df1 = df

        if self.verbose >= 2:
            printg('calculated emissionh integral in {0:.1f}s'.format(time()-t0))

        return

    # %%
    def _cutoff_linestrength(self, cutoff=None):
        '''
        Discard linestrengths that are lower that this, to reduce calculation
        times. Set the number of lines cut in ``self._Nlines_cutoff``

        Parameters
        ----------

        cutoff: float (unit of linestrength:  cm-1/(molecule.cm-2))
            discard linestrengths that are lower that this, to reduce calculation
            times. If 0, no cutoff. Default 0

        Notes
        -----

        # TODO:

        turn linestrength cutoff criteria in 'auto' mode that adjusts linestrength
        calculations based an error percentage criteria

        '''

        # Update defaults
        if cutoff is not None:
            self.params.cutoff = cutoff

        # Load variables
        cutoff = self.params.cutoff
        verbose = self.verbose
        df = self.df1

        if len(df) == 0:  # no lines
            self._Nlines_cutoff = None
            return      

        if cutoff <= 0:
            self._Nlines_cutoff = 0
            return      # dont update self.df1

        if self.verbose >= 2:
            printg('Applying linestrength cutoff')
        t0 = time()

        # Cutoff:
        b = df.S <= cutoff
        Nlines_cutoff = b.sum()
        
        # Estimate time gained
        expected_broadening_time_gain = (self._broadening_time_ruleofthumb*
                                         Nlines_cutoff*
                                         len(self.wbroad_centered))
        
        # Estimate error being made:
        if self.warnings['LinestrengthCutoffWarning'] != 'ignore':
            
            error = df.S[b].sum()/df.S.sum()*100

            if verbose>=2:
                print('Discarded {0:.2f}% of lines (linestrength<{1}cm-1/(#.cm-2))'.format(
                    Nlines_cutoff/len(df.S)*100, cutoff) +
                    ' Estimated error: {0:.2f}%, Expected time saved: {1:.1f}s'.format(
                    error, expected_broadening_time_gain))
            if error > self.misc.warning_linestrength_cutoff:
                self.warn('Estimated error after discarding lines is large: {0:.2f}%'.format(error) +
                          '. Consider reducing cutoff',
                          'LinestrengthCutoffWarning')

        try:
            assert sum(~b) > 0
        except AssertionError:
            self.plot_linestrength_hist()
            raise AssertionError('All lines discarded! Please increase cutoff. ' +
                                 'In your case: (min,max,mean)=({0:.2e},{1:.2e},{2:.2e}'.format(
                                     df.S.min(), df.S.max(), df.S.mean()) +
                                 'cm-1/(#.cm-2)). See histogram')
        
        # update df1:
        self.df1 = df[~b]
#        df.drop(b.index, inplace=True)   # performance: was not faster
        # ... performance: quite long to select here, but I couldn't find a faster
        # ... alternative 
        # Ensures abundance, molar mass and partition functions are transfered
        # (needed if they are attributes and not isotopes)
        transfer_metadata(df, self.df1, [k for k in df_metadata if hasattr(df, k)])
        
        # Store number of lines cut (for information)
        self._Nlines_cutoff = Nlines_cutoff
        
        time_spent = time() - t0
        if self.verbose >= 2:
            printg('Applied linestrength cutoff in {0:.1f}s (expected time saved ~ {1:.1f}s)'.format(
                    time_spent, expected_broadening_time_gain))

        # Raise a warning if we dont expect any performance improvement
        if time_spent > 0.3 and time_spent > 3*expected_broadening_time_gain:
                self.warn('Your linestrength cutoff is too high. '+\
                          'Time spent on applying cutoff '+\
                          '({0:.1f}s) is much longer than expected gain ({1:.1f}s). '.format(
                           time_spent, expected_broadening_time_gain)+\
                          'If the number of lines is low, you can consider '+\
                          'using cutoff=0',
                          'PerformanceWarning')
                
        return

    # %% ======================================================================
    # PRIVATE METHODS - UTILS
    # (cleaning)
    # ---------------------------------
    # _reinitialize_factory
    # _check_inputs
    # plot_populations()

    # XXX =====================================================================

    def _reinitialize(self):
        ''' Reinitialize Factory before a new spectrum is calculated. It does:

        - create new line Dataframe ``df1`` that will be scaled later with new populations
        - clean some objects if needed to save memory
        - delete populations from RovibrationalPartitionFunction objects

        If in save_memory mode, removes the line database (``self.df0``). This
        function is called after the scaled line database (``self.df1``) has been
        created.
        It saves a lot of memory but prevents the user from calculating a new
        spectrum without reloading the database.
        
        Returns
        -------
        
        None:
            but creates ``self.df1`` from ``self.df0`` 

        '''
        if __debug__:
            printdbg('called ._clean_factory()')

        # Create new line Dataframe
        # ... Operate on a duplicate dataframe to make it possible to do different
        # ... runs without reloading database
        self.df1 = self.df0.copy()
        
        # abundance and molar_mass should have been copied even if they are attributes 
        # (only 1 molecule, 1 isotope) and not a column (line specific) in the database
        # @dev: this brings a lot of performance improvement, but sometimes fail. 
        # | here we ensure that the DataFrame has the values:
        transfer_metadata(self.df0, self.df1, [k for k in df_metadata if hasattr(self.df0, k)])
        assert hasattr(self.df1, 'molar_mass')
        assert hasattr(self.df1, 'Ia')
        
        # Clean objects to save memory
        if self.save_memory:
            del self.df0
            self.df0 = None
        else:
            try:
                if sys.getsizeof(self.df1) > 500e6:
                    self.warn('Line database is large: {0:.0f} Mb'.format(
                        sys.getsizeof(self.df1)*1e-6)+'. Consider using save_memory ' +
                        "option, if you don't need to reuse this factory to calculate new spectra",
                        'MemoryUsageWarning')
            except ValueError:  # had some unexplained ValueError: __sizeof__() should return >= 0
                pass

        # Reset populations from RovibrationalPartitionFunctions objects
        molecule = self.input.molecule
        state = self.input.state
        for isotope in self._get_isotope_list(molecule):
            # ... Get partition function calculator
            try:
                parsum = self.get_partition_function_calculator(
                    molecule, isotope, state)
            except KeyError:
                # Partition function calculator not defined but maybe it wont
                # be needed (ex: only equilibrium calculations). Continue
                if __debug__:
                    printdbg('parsum[{0}][{1}][{2}]'.format(molecule,
                                                            isotope, state)+' not defined.')
            else:
                # ... Reset it
                parsum.reset_populations()

    def _check_inputs(self, mole_fraction, Tmax):
        ''' Check spectrum inputs, add warnings if suspicious values. 
        
        Also check that line databases look appropriate for the temperature Tmax
        considered

        Parameters
        ----------
        
        Tmax: float
            Tgas at equilibrium, or max(Tgas, Tvib, Trot) at nonequilibrium

        '''

        # Check mole fractions
        if mole_fraction is None:
            raise ValueError('Set mole_fraction')
        if mole_fraction > 1:
            self.warn('mole_fraction is > 1',
                      'InputConditionsWarning')

        # Check temperature range
        if Tmax > 700 and self.params.dbformat in ['hitran', 'hitran_tab']:
            self.warn("HITRAN is valid for low temperatures (typically < 700 K). "+\
                 "For higher temperatures you may need HITEMP or CDSD. See the "+\
                 "'databank=' parameter", "HighTemperatureWarning")

    def plot_populations(self, what='vib', isotope=None, nfig=None):
        ''' Plot populations currently calculated in factory.

        Plot populations of all levels that participate in the partition function.
        Output is different from the
        Spectrum :py:meth:`~radis.spectrum.spectrum.Spectrum.plot_populations` method,
        where only the levels that directly contribute to the spectrum are shown

        Note: only valid after calculating non_eq spectrum as it uses the
        partition function calculator object

        Parameters
        ----------

        what: 'vib', 'rovib'
            what levels to plot

        isotope: int, or ``None``
            which isotope to plot. If ``None`` and if there are more than one isotope,
            raises an error.

        Other Parameters
        ----------------

        nfig: int, or str
            on which Figure to plot. Default ``None``



        '''

        import matplotlib.pyplot as plt
        from publib import set_style, fix_style

        # Check inputs
        assert what in ['vib', 'rovib']
        if isotope is None:
            if type(self.input.isotope) is int:  # only one isotope. Use it.
                isotope = self.input.isotope
            else:
                raise ValueError('isotope number is needed')

        # Get levels
        molecule = self.input.molecule
        state = self.input.state
        levels = self.get_partition_function_calculator(
            molecule, isotope, state).df
        if what == 'vib':
            E, n, g = levels['Evib'], levels['nvib'], levels['gvib']
        elif what == 'rovib':
            E, n = levels['E'], levels['n']
            if 'g' in levels.keys():
                g = levels['g']
            elif all_in(['gvib', 'grot'], levels.keys()):
                g = levels['gvib'] * levels['grot']
            else:
                raise ValueError('either g, or gvib+grot must be defined to ' +
                                 'calculate total degeneracy. Got: {0}'.format(list(levels.keys())))

        # Plot
        set_style('origin')
        plt.figure(num=nfig)
        plt.plot(E, n/g, 'ok')
        plt.xlabel('Energy (cm-1)')
        plt.ylabel('Population (n / g)')
        plt.yscale('log')
        fix_style('origin')


def get_all_waveranges(medium, wavenum_min=None, wavenum_max=None, wavelength_min=None, wavelength_max=None):
    ''' Give either lambda_min, lambda_max or nu_min, nu_max and you get 
    everything, in the request propagation ``medium`` 

    Parameters
    ----------

    medium: ``'air'``, ``'vacuum'``
        propagation medium

    wavenum_min, wavenum_max: float, or None
        wavenumbers

    wavelength_min, wavelength_max: float, or None
        wavelengths in given ``medium``

    Returns
    -------

    wavenum_min, wavenum_max, wavelength_min, wavelength_max: float
        wavenumbers, wavelengths in given ``medium``
    '''

    # Check input
    if (wavelength_min is None and wavelength_max is None and
            wavenum_min is None and wavenum_max is None):
        raise ValueError('Give wavenumber or wavelength')
    if ((wavelength_min is not None or wavelength_max is not None) and
            (wavenum_min is not None or wavenum_max is not None)):
        raise ValueError('Cant give both wavenumber and wavelength as input')
    assert medium in ['air', 'vacuum']

    # Get all waveranges

    # ... Input is in wavelength:
    if (wavenum_min is None and wavenum_max is None):
        assert wavelength_max is not None
        assert wavelength_min is not None
        # Test range is correct:
        assert wavelength_min < wavelength_max

        # In wavelength mode, the propagating medium matters. Convert to
        # calculation medium (vacuum) if needed:
        if medium == 'air':
            wavelength_min_vac = air2vacuum(wavelength_min)
            wavelength_max_vac = air2vacuum(wavelength_max)
        else:
            wavelength_min_vac = wavelength_min
            wavelength_max_vac = wavelength_max

        wavenum_min = nm2cm(wavelength_max_vac)
        wavenum_max = nm2cm(wavelength_min_vac)
    # ... or input is in wavenumber:
    else:
        assert wavenum_min is not None
        assert wavenum_max is not None
        # Test range is correct:
        assert wavenum_min < wavenum_max

        wavelength_min_vac = cm2nm(wavenum_max)
        wavelength_max_vac = cm2nm(wavenum_min)

        # Convert to expected medium if needed:
        if medium == 'air':
            wavelength_min = vacuum2air(wavelength_min_vac)
            wavelength_max = vacuum2air(wavelength_max_vac)

    return wavenum_min, wavenum_max, wavelength_min, wavelength_max


if __name__ == '__main__':
    from radis.test.lbl.test_base import _run_testcases
    _run_testcases()

    _, _, wlmin, wlmax = get_all_waveranges('air', 2000, 2400)
    np.allclose((wlmin, wlmax), (4165.53069, 4998.6369))
