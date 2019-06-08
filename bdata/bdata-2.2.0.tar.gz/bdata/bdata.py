# Python object for reading msr data files, in particular with respect to BNMR. 
# Requires use of the mudpy package.
# Derek Fujimoto
# July 2017

import bdata.mudpy as mp
import numpy as np
import socket, os, time, sys
import datetime
import warnings

if sys.version_info[0] >= 3:
    xrange = range

__doc__="""
    Beta-data module. The bdata object is largely a data container, designed to 
    read out the MUD data files and to provide user-friendly access to reliably 
    corrected BNMR/BNQR data. Data files are read either from a directory 
    specified by environment variable (see below), or from a passed filename 
    for easy external user access. In this case, data files can be downloaded 
    from musr.ca. The MUD data file is read and closed on object construction. 
    
    Requires the installation of mudpy. See mudpy docstring for installation
    instructions. 
    
    Constructor: bdata(run_number,year=0,filename='')
    
    Example usage: 
        bd = bdata(40001)           # read run 40001 from the default year. 
        bd = bdata(40001,year=2009) # read run 40001 from 2009.
        bd = bdata(0,filename='file.msr') # read file from local memory, run 
                                            number unused 
        
    if year==0 then default is the current year. For scripts analysing a 
    specific data set, it is advised that this be set so that the script does 
    not break as time passes. 
        
    Asymmetry: 
        bd.asym() # for details and options see bdata.asym docstring. 
        
    Beam energy: 
        bd.beam_kev()   # returns beam energy in keV
               
    Pulse-off time for SLR measurements: 
        pulse_off_s()
                                      
    For a nicely-formatted list of all data fields call the fields method: 
        bd.fields()
        
        Note that the object representation has been nicely formatted as well, 
        so that typing
        
        bd
        
        into the interpreter produces nice output. 
        
    Note that bdict objects allow for the calling of dictionary keys like an 
    object attribute. For example, bd.ppg.beam_on or bd.ppg['beam_on'] have the 
    exact same output. Note that reserved characters such as '+' cannot be used 
    in this manner. 
            
    One can also set the location of the data archive via environment 
    variables "BNMR_ARCHIVE" and "BNQR_ARCHIVE". This would be something 
    like "/data1/bnmr/dlog/" on linbnmr2 or "/data/bnmr/" on muesli or 
    lincmms
        
    Derek Fujimoto
    August 2017
    
    Last updated: December 2017
"""

# =========================================================================== #
class bdata(object):
    """
        Class fields 
            dkeys
            evar_bnmr
            evar_bnqr
        
        Data fields using raw values: 
            exp
            run
            duration
            start_time
            end_time
            title
            lab
            area
            method
            sample
            orientation
            das
            mode
            experimenter
        
        Data fields using lists of objects (see docstrings for fields):
            hist_list
            scaler_list
            var_list
            
        Data fields using dictionaries of objects (by name/title):
            ppg
            epics
            camp
            hist
            sclr
            
        Calculated or converted data fields
            year
            start_date  (human-readable)
            end_date    (human-readable)
            
        Public functions
            asym
            beam_kev
            fields
            help
            pulse_off_s
            
        Private worker functions
            __init__
            _get_area_data
            _get_asym_hel
            _get_asym_comb
            _rebin
            __repr__
    """
    
    # set nice dictionary keys based on 2017 titles and names, for independent
    # variables
    dkeys = {
        
        # PPG (just the stuff after the last "/")
            "e20 beam on dwelltimes"            :"beam_on",
            "e20  beam off dwelltimes"          :"beam_off",
            "e20 beam off dwelltimes"           :"beam_off",   
            "beam off time (ms)"                :"beam_off_ms",
                                                        
            "constant time between cycles"      :"const_t_btwn_cycl",
            "e1f const time between cycles"     :"const_t_btwn_cycl",
                                                        
            "DAQ drives sampleref"              :"smpl_ref_daq_drive",
            "DAQ service time (ms)"             :"service_t",
            "Dwell time (ms)"                   :"dwelltime",
            "Bin width (ms)"                    :"dwelltime",
                                                        
            "Enable helicity flipping"          :"hel_enable",
            "Enable RF"                         :"rf_enable",
            "enable sampleref mode"             :"smpl_ref_enable",
                                                        
            "frequency increment (Hz)"          :"freq_incr",
            "frequency start (Hz)"              :"freq_start",
            "frequency stop (Hz)"               :"freq_stop",
            
            "init mode file"                    :"init_mode",
            "init mode"                         :"init_mode",
                                                        
            "Helicity flip sleep (ms)"          :"hel_sleep",
            "helicity flip sleep (ms)"          :"hel_sleep",
            "Helicity flip sleep(ms)"           :"hel_sleep",
                                                                                                    
            "NaVolt start (volts)"              :"volt_start",
            "NaVolt stop (volts)"               :"volt_stop",
            "NaVolt inc (volts)"                :"volt_incr",
                                                        
            "num bins"                          :"nbins",
            "num cycles per supercycle"         :"ncycles",
            "Number dwelltimes per freq"        :"ndwell_per_f",
            "number of midbnmr regions"         :"nregion",
            "num post RF beamOn dwelltimes"     :"ndwell_post_on",
                                                        
            "PPG mode"                          :"mode",     
            "e20 prebeam dwelltimes"            :"prebeam", 
            "psm onef enabled"                  :"onef_enable",
            "psm onef scale factor"             :"onef_scale",
            "psm fREF enabled"                  :"fref_enable",
            "psm fREF scale factor"             :"fref_scale",
            "psm scale factor"                  :"psm_scale", 
            "psm scaler factor"                 :"psm_scale", 
                                                        
            "randomize freq increments"         :"rand_freq_incr",
            "Randomize freq values"             :"rand_freq_val",
            "Ref tuning freq (Hz)"              :"ref_tune_freq",
            "Ref tuning frequency (Hz)"         :"ref_tune_freq",
            "e20 rf frequency (Hz)"             :"freq",
            "RFon delay (dwelltimes)"           :"rf_on_delay",
            "num RF on delays (dwell times)"    :"rf_on_delay",
            "RFon duration (dwelltimes)"        :"rf_on",
            "RF on time (ms)"                   :"rf_on_ms",
            "RF enabled"                        :"rf_enable",
            
            "Single tone simulated"             :"sgle_tone_sim",
                                                        
            "use defaults for midbnmr"          :"defaults",
             
        # CAMP
            "/biasV/input1"                             :"rb_cell_bias_set",
            "/biasV/output1"                            :"rb_cell_bias_read",
        
            "/CryoEx_MassFlow/read_flow"                :"cryo_read",
            "/CryoEx_MassFlow/set_flow"                 :"cryo_set",
            "/Cryo_level/He_level"                      :"cryo_he",
            "/Cryo_level/N2_level"                      :"cryo_n2",
            "/cryo_lift/set_position"                   :"clift_set",  
            "/cryo_lift/read_position"                  :"clift_read",
            
            "/Cryo_oven/current_read_1"                 :"oven_current",
            "/Cryo_oven/output_1/D"                     :"oven_out_d",
            "/Cryo_oven/output_1/I"                     :"oven_out_i",
            "/Cryo_oven/output_1/P"                     :"oven_out_p",
            "/Cryo_oven/read_A"                         :"oven_readA",
            "/Cryo_oven/read_B"                         :"oven_readB",
            "/Cryo_oven/read_C"                         :"oven_readC",
            "/Cryo_oven/read_D"                         :"oven_readD",
            "/Cryo_oven/setpoint_1"                     :"oven_set1",
                        
            "/Dac0/dac_set"                             :"daq_set",
            "/Dewar/He_level"                           :"he_level",
             
            "/flow_set/output"                          :"flow_set_out",
                                                    
            "/He_flow/read_flow"                        :"he_read",
            "/He_flow/set_flow"                         :"he_set",
                                                    
            "/lock-in/R"                                :"lockin_r",
            "/lock-in/theta"                            :"lockin_theta",
            "/lock-in/X"                                :"lockin_x",
            "/lock-in/Y"                                :"lockin_y",
                                                    
            "/Magnet/mag_field"                         :"b_field",     
            "/Magnet/mag_read"                          :"mag_current",
            "/mass_flow/read_flow"                      :"mass_read",
            "/mass_flow/set_flow"                       :"mass_set",   
                                                    
            "/needle-valve/set_position"                :"needle_set",
            "/needle-valve/read_position"               :"needle_read",
            "/Needle_Valve/set_position"                :"needle_set",
            "/Needle/read_position"                     :"needle_pos",
            "/Needle/set_position"                      :"needle_set",
            
            "/PVac/adc_read"                            :"vac",
                                                    
            "/rfamp/fwd_max"                            :"rfamp_fwd",
            "/rfamp/fwd_power"                          :"rfamp_fpwr",
            "/rfamp/refl_max"                           :"rfamp_rfl",
            "/rfamp/RF_gain"                            :"rfamp_rfgain",
            "/rf_level_cont/dac_set"                    :"rf_dac",
                                                    
            "/Sample/current_read_1"                    :"smpl_current",
            "/Sample/current_read"                      :"smpl_current",
            "/Sample1/current_read"                     :"smpl_current",
            "/Sample/read_A"                            :"smpl_read_A",
            "/Sample1/read_A"                           :"smpl_read_A",
            "/Sample/read_B"                            :"smpl_read_B",
            "/Sample1/read_B"                           :"smpl_read_B",
            "/Sample/read_C"                            :"smpl_read_C",
            "/Sample/read_D"                            :"smpl_read_D",
            "/Sample/set_current"                       :"smpl_set_current",
            "/Sample/setpoint"                          :"smpl_set",
            "/Sample1/setpoint"                         :"smpl_set",
            "/Sample/setpoint_1"                        :"smpl_set",
            "/sample2/heat_range"                       :"smpl2_heat",
            "/sample2/sample_read"                      :"smpl2_read",
            "/sample_volts/reading"                     :"smpl_volts",
            "/Shield/read_1"                            :"shield_read1",
            "/signal_gen/amplitude"                     :"sig_gen_amp",
            "/signal_gen/frequency"                     :"sig_gen_freq",
            "/signal_gen/power_level"                   :"sig_gen_pwr",
            "/signal_gen/rf_on"                         :"sig_gen_rfon",
            "/stealth/fwd_max"                          :"stealth_fwd_max",
            "/stealth/fwd_power"                        :"stealth_fwd_pwr",
            "/stealth/rev_max"                          :"stealth_rev_max",
            "/stealth/rev_power"                        :"stealth_rev_pwr",
            
        # EPICS
            "BNMR:HVBIAS:P"                             :"nmr_bias",
            "BNMR:HVBIAS:PO"                            :"nmr_bias",
            "BNMR:HVBIAS:POS"                           :"nmr_bias",
            "BNMR:HVBIAS:POS:"                          :"nmr_bias",
            "BNMR:HVBIAS:POS:R"                         :"nmr_bias",
            "BNMR:HVBIAS:POS:RDVO"                      :"nmr_bias",
            "BNMR:HVBIAS:POS:RDVOL"                     :"nmr_bias",
            "BNMR:HVBIAS:POS:RDVOL1"                    :"nmr_bias",
                                                  
            "BNMR:HVBIAS:N"                             :"nmr_bias_n",
            "BNMR:HVBIAS:NE"                            :"nmr_bias_n",
            "BNMR:HVBIAS:NEG"                           :"nmr_bias_n",
            "BNMR:HVBIAS:NEG:"                          :"nmr_bias_n",
            "BNMR:HVBIAS:NEG:R"                         :"nmr_bias_n",
            "BNMR:HVBIAS:NEG:RDVO"                      :"nmr_bias_n",
            "BNMR:HVBIAS:NEG:RDVOL"                     :"nmr_bias_n",
            "BNMR:HVBIAS:NEG:RDVOL1"                    :"nmr_bias_n",
                                                  
            "BNQR:HVBIAS:RD"                            :"nqr_bias",
            "BNQR:HVBIAS:RDVOL"                         :"nqr_bias",
                                                  
            "ITE:BIAS:RDVO"                             :"target_bias",  
            "ITE:BIAS:RDVOL"                            :"target_bias",  
            "ITE:BIAS:RDVOLER"                          :"target_bias",  
            "ITE:BIAS:RDVOLVOL"                         :"target_bias",
            "ITW:BIAS:R"                                :"target_bias",
            "ITW:BIAS:RD"                               :"target_bias",
            "ITW:BIAS:RDV"                              :"target_bias",
            "ITW:BIAS:RDVO"                             :"target_bias",
            "ITW:BIAS:RDVOL"                            :"target_bias",
            "ITW:BIAS:RDVOL1"                           :"target_bias",
            "ITW:BIAS:RDVOLVOL"                         :"target_bias",
                                                  
            "ILE2:BIAS15:R"                             :"bias15",
            "ILE2:BIAS15:RD"                            :"bias15",
            "ILE2:BIAS15:RDV"                           :"bias15",
            "ILE2:BIAS15:RDVO"                          :"bias15",    
            "ILE2:BIAS15:RDVOL"                         :"bias15",
                                                  
            "ILE2:LAS:RDPO"                             :"las_pwr",
            "ILE2:LAS:RDPOW"                            :"las_pwr",
            "ILE2:LAS:RDPOWE"                           :"las_pwr",
            "ILE2:LAS:RDPOWER"                          :"las_pwr",
            "ILE2:LAS:RDPOWERL"                         :"las_pwr",
             
            "ILE2:BIASTUBE:"                            :"biastube",
            "ILE2:BIASTUBE:V"                           :"biastube",
            "ILE2:BIASTUBE:VOL"                         :"biastube",
             
            "ILE2A1:HH:CUR"                             :"hh_current",
            "ILE2A1:HH:RDCU"                            :"hh_current",
            "ILE2A1:HH:RDCUR"                           :"hh_current",
            "":""
            }
    
    # set environment variable same to get data archive location
    # should point to something like
    # "/data1/bnmr/dlog/" on linbnmr2
    # "/data/bnmr/" on muesli or lincmms
    evar_bnmr = "BNMR_ARCHIVE"
    evar_bnqr = "BNQR_ARCHIVE"

    # ======================================================================= #
    def __init__(self,run_number,year=0,filename=""):
        """Constructor. Reads file, stores and sorts data."""
        
        # Get the current year
        if year == 0:   year = datetime.datetime.now().year
        
        # read file if not provided
        if filename == "":
            
            # Get spectrometer directory. Based on rmlm's bnmr_20a.cpp.
            if run_number >= 40000 and run_number <= 44999:
                spect_dir = "bnmr/"
            elif run_number >= 45000 and run_number <= 49999:
                spect_dir = "bnqr/"
            else:
                raise ValueError("Run number out of range") 
                
            # look for environment variable
            if spect_dir == "bnmr/" and self.evar_bnmr in list(os.environ.keys()):
                filename = os.environ[self.evar_bnmr]
                
            elif spect_dir == "bnqr/" and self.evar_bnqr in list(os.environ.keys()):
                filename = os.environ[self.evar_bnqr]
                    
            # finalize file name
            if filename[-1] != '/':
                filename += '/'
            filename += repr(year) + "/0" + repr(run_number) + ".msr"
        
        # check file existence
        if not os.path.isfile(filename):
            raise RuntimeError("File %s does not exist" % filename)
        
        # Open file ----------------------------------------------------------
        fh = mp.open_read(filename)
        
        if fh < 0: 
            raise RuntimeError("__init__: open file failed. ")
        try:
            # Read run description
            self.exp = mp.get_exp_number(fh)
            self.run = mp.get_run_number(fh)
            self.duration = mp.get_elapsed_seconds(fh)
            self.start_time = mp.get_start_time(fh)
            self.end_time = mp.get_end_time(fh)
            
            try:
                self.title = str(mp.get_title(fh))
                self.lab = str(mp.get_lab(fh))
                self.area = str(mp.get_area(fh))
                self.method = str(mp.get_method(fh))
                self.sample = str(mp.get_sample(fh))
                self.orientation = str(mp.get_orientation(fh))
                self.das = str(mp.get_das(fh))
                self.mode = str(mp.get_insert(fh))
                self.experimenter = str(mp.get_experimenter(fh))
            except UnicodeEncodeError:
                self.title = mp.get_title(fh)
                self.lab = mp.get_lab(fh)
                self.area = mp.get_area(fh)
                self.method = mp.get_method(fh)
                self.sample = mp.get_sample(fh)
                self.orientation = mp.get_orientation(fh)
                self.das = mp.get_das(fh)
                self.mode = mp.get_insert(fh)
                self.experimenter = mp.get_experimenter(fh)
            
            # Read histograms
            n_hist = mp.get_hists(fh)[1]
            self.hist_list = []
            for i in range(1,n_hist+1):
                self.hist_list.append(bhist())
                self.hist_list[-1].id_number = i
                self.hist_list[-1].htype = mp.get_hist_type(fh,i)
                
                self.hist_list[-1].data = mp.get_hist_data(fh,i)
                
                self.hist_list[-1].n_bytes = mp.get_hist_n_bytes(fh,i)
                self.hist_list[-1].n_bins = mp.get_hist_n_bins(fh,i)
                self.hist_list[-1].n_events = mp.get_hist_n_events(fh,i)
                
                self.hist_list[-1].fs_per_bin = mp.get_hist_fs_per_bin(fh,i)
                self.hist_list[-1].s_per_bin = mp.get_hist_sec_per_bin(fh,i)
                self.hist_list[-1].t0_ps = mp.get_hist_t0_ps(fh,i)
                self.hist_list[-1].t0_bin = mp.get_hist_t0_bin(fh,i)
                
                self.hist_list[-1].good_bin1 = mp.get_hist_good_bin1(fh,i)
                self.hist_list[-1].good_bin2 = mp.get_hist_good_bin2(fh,i)
                self.hist_list[-1].background1 = mp.get_hist_background1(fh,i)
                self.hist_list[-1].background2 = mp.get_hist_background2(fh,i)
                
                try:
                    self.hist_list[-1].title = str(mp.get_hist_title(fh,i))
                except UnicodeEncodeError:
                    self.hist_list[-1].title = mp.get_hist_title(fh,i)
                
            # Read scalers
            #~ n_scaler = mp.get_scalers(fh)[1]
            #~ self.scaler_list = []
            #~ for i in range(1,n_scaler+1):
                #~ self.scaler_list.append(bscaler())
                #~ self.scaler_list[-1].counts = mp.get_scaler_counts(fh,i)
                #~ self.scaler_list[-1].id_number = i
                #~ try:
                    #~ self.scaler_list[-1].title = str(mp.get_scaler_label(fh,i))
                #~ except UnicodeEncodeError as e:
                    #~ self.scaler_list[-1].title = repr(e)
           
            # Read independent variables
            n_var = mp.get_ivars(fh)[1]
            self.var_list = []
            for i in range(1,n_var+1):
                self.var_list.append(bvar())
                self.var_list[-1].id_number = i
                self.var_list[-1].low = mp.get_ivar_low(fh,i)
                self.var_list[-1].high = mp.get_ivar_high(fh,i)
                self.var_list[-1].mean = mp.get_ivar_mean(fh,i)
                self.var_list[-1].std = mp.get_ivar_std(fh,i)
                self.var_list[-1].skew = mp.get_ivar_skewness(fh,i)
                
                try:
                    self.var_list[-1].title = str(mp.get_ivar_name(fh,i))
                    self.var_list[-1].description = str(\
                                                mp.get_ivar_description(fh,i))
                    self.var_list[-1].units = str(mp.get_ivar_units(fh,i))
                except UnicodeEncodeError:
                    self.var_list[-1].title = mp.get_ivar_name(fh,i)
                    self.var_list[-1].description =mp.get_ivar_description(fh,i)
                    self.var_list[-1].units = mp.get_ivar_units(fh,i)
            
        # Close file ----------------------------------------------------------
        finally:
            mp.close_read(fh)
        
        # Sort independent variables into dictionaries by title
        self.ppg = bdict()
        self.camp = bdict()
        self.epics = bdict()
        for v in self.var_list: 
            try:
                if 'PPG' in v.title:
                    self.ppg[self.dkeys[v.title.split("/")[-1]]] = v
                elif v.title[0] == "/":
                    self.camp[self.dkeys[v.title]] = v
                else:
                    self.epics[self.dkeys[v.title]] = v
            except (KeyError,IndexError):
                    message = '"' + v.title + '" not found in dkeys. '+\
                                "Data in list, but not sorted to dict."
                    warnings.warn(message,RuntimeWarning,stacklevel=2)
                    
        # Sort histograms into dictionaries by title and convert to doubles
        self.hist = bdict()
        for h in self.hist_list:
            self.hist[h.title] = h
            self.hist[h.title].data = self.hist[h.title].data.astype(float)
        
        # Sort scalers into dictionaries by title
        #~ self.sclr = bdict()
        #~ for s in self.scaler_list:
            #~ new_key = s.title.split("%")[-1].replace(" ","")
            #~ self.sclr[new_key] = s
            
        # set the date
        self.start_date = time.ctime(self.start_time)
        self.end_date = time.ctime(self.end_time)
        self.year = time.gmtime(self.start_time).tm_year

    # ======================================================================= #
    def _get_area_data(self):
        """Get histogram list based on area type. 
        List pattern: [type1_hel+,type2_hel+,type1_hel-,type2_hel-]
        where type1/2 = F/B or R/L in that order.
        """
        
        if self.mode == '1n':
            data = [self.hist['NBMF+'].data,\
                    self.hist['NBMF-'].data,\
                    self.hist['NBMB+'].data,\
                    self.hist['NBMB-'].data]
            
        elif self.area == 'BNMR':
            data = [self.hist['F+'].data,\
                    self.hist['F-'].data,\
                    self.hist['B+'].data,\
                    self.hist['B-'].data]
        
        elif self.area == 'BNQR':
            data = [self.hist['R+'].data,\
                    self.hist['R-'].data,\
                    self.hist['L+'].data,\
                    self.hist['L-'].data]
        else:
            data = []
        
        if self.mode == '2h':
            data.extend([self.hist['AL1+'].data,self.hist['AL1-'].data,
                        self.hist['AL0+'].data,self.hist['AL0-'].data,
                        self.hist['AL3+'].data,self.hist['AL3-'].data,
                        self.hist['AL2+'].data,self.hist['AL2-'].data])
        
        # copy
        return [np.copy(d) for d in data]

    # ======================================================================= #
    def _get_asym_hel(self,d):
        """
            Find the asymmetry of each helicity. 
        """
        
        # get data 1+ 2+ 1- 2-
        d0 = d[0]; d1 = d[2]; d2 = d[1]; d3 = d[3]

        # pre-calcs
        denom1 = d0+d1; 
        denom2 = d2+d3
        
        # check for div by zero
        denom1[denom1==0] = np.nan          
        denom2[denom2==0] = np.nan
        
        # asymmetries in both helicities
        asym_hel = [(d0-d1)/denom1,
                    (d2-d3)/denom2]
                    
        # errors 
        # https://www.wolframalpha.com/input/?i=%E2%88%9A(F*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+F)%5E2+%2B+B*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+B)%5E2)
        asym_hel_err = [2*np.sqrt(d0*d1/np.power(denom1,3)),
                        2*np.sqrt(d2*d3/np.power(denom2,3))]
        
        # remove nan            
        for i in range(2):
            asym_hel[i][np.isnan(asym_hel[i])] = 0.
            asym_hel_err[i][np.isnan(asym_hel_err[i])] = 0.
        
        # exit
        return [[asym_hel[1],asym_hel_err[1]],  # something wrong with file?
                [asym_hel[0],asym_hel_err[0]]]  # I shouldn't have to switch
                
    # ======================================================================= #
    def _get_asym_comb(self,d):
        """
        Find the combined asymmetry for slr runs. Elegant 4-counter method.
        """
        
        # get data
        d0 = d[0]; d1 = d[2]; d2 = d[1]; d3 = d[3]
        
        # pre-calcs
        r_denom = d0*d3
        r_denom[r_denom==0] = np.nan
        r = np.sqrt((d1*d2/r_denom))
        r[r==-1] = np.nan
    
        # combined asymmetry
        asym_comb = (r-1)/(r+1)
        
        # check for div by zero
        d0[d0==0] = np.nan                  
        d1[d1==0] = np.nan
        d2[d2==0] = np.nan
        d3[d3==0] = np.nan
        
        # error in combined asymmetry
        asym_comb_err = r*np.sqrt(1/d1 + 1/d0 + 1/d3 + 1/d2)/np.square(r+1)
        
        # replace nan with zero 
        asym_comb[np.isnan(asym_comb)] = 0.
        asym_comb_err[np.isnan(asym_comb_err)] = 0.
        
        return [asym_comb,asym_comb_err]

    # ======================================================================= #
    def _get_asym_alpha(self,a,b):
        """
            Find alpha diffusion ratios from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)
            b: list of beta  detector histograms (each helicity)
        """
        
        # just  use AL0
        try:
            a = a[2:4]
        except IndexError:
            a = a[:2]
            
        # sum counts in alpha detectors
        asum = np.sum(a,axis=0)
        
        # sum counts in beta detectors
        bsum = np.sum(b,axis=0)
        
        # check for dividing by zero 
        asum[asum == 0] = np.nan
        bsum[bsum == 0] = np.nan
        
        # asym calcs
        asym = asum/bsum
        
        # errors
        dasym = asym*np.sqrt(1/asum + 1/bsum)
        
        return [asym,dasym]

    # ======================================================================= #
    def _get_asym_alpha_tag(self,a,b):
        """
            Find asymmetry from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)  
            b: list of beta  detector histograms (each helicity)  1+ 1- 2+ 2-
        """

        # beta in coincidence with alpha
        coin = a[:4]
        
        # beta coincidence with no alpha
        no_coin = a[4:8]

        # get split helicity asym from 
        hel_coin =      self._get_asym_hel(coin)
        hel_no_coin =   self._get_asym_hel(no_coin)
        hel_reg =       self._get_asym_hel(b)
        
        # get combined helicities
        com_coin =      self._get_asym_comb(coin)
        com_no_coin =   self._get_asym_comb(no_coin)
        com_reg =       self._get_asym_comb(b)

        # make output
        return (hel_coin,hel_no_coin,hel_reg,com_coin,com_no_coin,com_reg)

    # ======================================================================= #
    def _get_1f_sum_scans(self,d,freq):
        """
            Sum counts in each frequency bin over 1f scans. 
        """
        
        # combine scans: values with same frequency 
        unique_freq = np.unique(freq)
        
        sum_scans = [[] for i in range(len(d))]
        
        for f in unique_freq: 
            tag = freq==f
            for i in range(len(d)):
                sum_scans[i].append(np.sum(d[i][tag]))
            
        return (np.array(unique_freq),np.array(sum_scans))

    # ======================================================================= #
    def _get_2e_asym(self):
        """
            Get asymmetries for 2e random-frequency scan. 
            Based on bnmr_2e.cpp by rmlm (Oct 4, 2017).
        """
        
        # get needed PPG parameters for splitting 1D histos into 2D histos
        try:        
            # get frequency vector
            freq = np.arange(self.ppg['freq_start'].mean,\
                             self.ppg['freq_stop'].mean+\
                                    self.ppg['freq_incr'].mean,\
                             self.ppg['freq_incr'].mean)
                             
            # number of dwelltimes per frequency bin 
            ndwell = 2*int(self.ppg['ndwell_per_f'].mean)-1
            
            # number of RF on delays for the start bin. 
            start_bin = int(self.ppg['rf_on_delay'].mean)
            
            # get bin centers in ms
            time = self.ppg['rf_on_ms'].mean*(np.arange(ndwell)+0.5-ndwell/2.)
            
            # get the time and index of the middle time 
            mid_time_i = int(np.floor(ndwell/2.))
            mid_time = time[mid_time_i]
        
            # beam off time after pulse in ms
            beam_off = int(self.ppg['beam_off_ms'].mean)
        
        except KeyError:
            raise RuntimeError("Not all dictionary variables read out to "+\
                               "proper locations")
            
        # setup output
        out = bdict()
        out['freq'] = freq
        out['time'] = time
            
        # get data
        data = np.array(self._get_area_data()) # [[fp], [bfm], [bp], [bm]]
        
        # discared initial bad bins, and beam-off trailing bins
        data = data[:,start_bin:len(freq)*ndwell+start_bin]
        
        # split data by frequency
        nsplit = len(data[0])/ndwell
        
        fp = np.array(np.split(data[0],nsplit))
        fm = np.array(np.split(data[1],nsplit))
        bp = np.array(np.split(data[2],nsplit))
        bm = np.array(np.split(data[3],nsplit))
        
        # get raw asymmetries 
        asym_p_2cntr = (bp-fp)/(bp+fp)      # two counter
        asym_m_2cntr = (bm-fm)/(bm+fm)      # two counter
        r = np.sqrt(bp*fm/(bm*fp))
        asym_4cntr = (r-1)/(r+1)            # four counter
        
        # get raw asymmetry errors
        asym_p_2cntr_err = 2*np.sqrt(bp*fp)/((bp+fp)**1.5)
        asym_m_2cntr_err = 2*np.sqrt(bm*fm)/((bm+fm)**1.5)
        asym_4cntr_err = r*np.sqrt(1./bp+1./bm+1./fp+1./fm)/((r+1)**2)

        # save to output
        out['raw_p'] = np.array([asym_p_2cntr,asym_p_2cntr_err])
        out['raw_n'] = np.array([asym_m_2cntr,asym_m_2cntr_err])
        out['raw_c'] = np.array([asym_4cntr,asym_4cntr_err])

        # wrap asymmetry arrays into one for calculations [p,m,4]
        # indexing is now [pm4][freq][time bin]
        asym     = np.array([asym_p_2cntr,    asym_m_2cntr,    asym_4cntr])
        asym_err = np.array([asym_p_2cntr_err,asym_m_2cntr_err,asym_4cntr_err])

        # compute differenced asymmetries via slopes from weighted least squares 
        # minimization.
        if ndwell >= 5:
            
            # calculate needed components element-wise
            w = asym_err**-2
            x = time
            y = asym
            
            wx = w*x
            wy = w*y
            wxy = w*x*y
            wxx = w*x*x
        
            # sum over values i < mid_time_i within each asymmetry and frequency 
            # Indexing: [pm4][freq]
            w_pre   = np.sum(w  [:,:,:mid_time_i],2)    
            wx_pre  = np.sum(wx [:,:,:mid_time_i],2)
            wy_pre  = np.sum(wy [:,:,:mid_time_i],2)
            wxy_pre = np.sum(wxy[:,:,:mid_time_i],2)
            wxx_pre = np.sum(wxx[:,:,:mid_time_i],2)
            
            # sum over values i > mid_time_i
            w_pst   = np.sum(w  [:,:,-mid_time_i:],2)
            wx_pst  = np.sum(wx [:,:,-mid_time_i:],2)
            wy_pst  = np.sum(wy [:,:,-mid_time_i:],2)
            wxy_pst = np.sum(wxy[:,:,-mid_time_i:],2)
            wxx_pst = np.sum(wxx[:,:,-mid_time_i:],2)
            
            # calculate slopes and intercepts
            delta_pre = w_pre*wxx_pre - wx_pre**2
            delta_pst = w_pst*wxx_pst - wx_pst**2
            
            sl_pre = (w_pre*wxy_pre - wx_pre*wy_pre)/delta_pre
            sl_pst = (w_pst*wxy_pst - wx_pst*wy_pst)/delta_pst
            dsl_pre = np.sqrt(w_pre/delta_pre)
            dsl_pst = np.sqrt(w_pst/delta_pst)
            
            intr_pre = (wy_pre*wxx_pre - wx_pre*wxy_pre)/delta_pre
            intr_pst = (wy_pst*wxx_pst - wx_pst*wxy_pst)/delta_pst
            dintr_pre = np.sqrt(wxx_pre/delta_pre)
            dintr_pst = np.sqrt(wxx_pst/delta_pst)
            
            # extrapolate to middle time bin
            asym_slopes = intr_pst-intr_pre+(sl_pst-sl_pre)*mid_time
            asym_slopes_err = np.sqrt(dintr_pre**2 + dintr_pst**2 + \
                                      (dsl_pre**2 + dsl_pst**2) * mid_time**2)
            
            # save to output        
            out['sl_p'] = np.array([asym_slopes[0],asym_slopes_err[0]])
            out['sl_n'] = np.array([asym_slopes[1],asym_slopes_err[1]])
            out['sl_c'] = np.array([asym_slopes[2],asym_slopes_err[2]])
        
        # calculate asymmetry using differences
        asym_diff = asym[:,:,mid_time_i+1] - asym[:,:,mid_time_i-1]
        asym_diff_err = np.sqrt(asym_err[:,:,mid_time_i+1]**2+\
                                asym_err[:,:,mid_time_i-1]**2)
        
        # save to output
        out['dif_p'] = np.array([asym_diff[0],asym_diff_err[0]])
        out['dif_n'] = np.array([asym_diff[1],asym_diff_err[1]])
        out['dif_c'] = np.array([asym_diff[2],asym_diff_err[2]])   
            
        return out

    # ======================================================================= #
    def _rebin(self,xdx,rebin):
        """
            Rebin array x with weights 1/dx**2 by factor rebin.
            
            Inputs: 
                xdx = [x,dx]
                rebin = int
            Returns [x,dx] after rebinning. 
        """

        x = xdx[0]
        dx = xdx[1]
        rebin = int(rebin)
        
        # easy end condition
        if rebin <= 1:
            return (x,dx)
        
        # Rebin Discard unused bins
        lenx = len(x)
        x_rebin = []
        dx_rebin = []
        
        # avoid dividing by zero
        dx[dx==0] = np.inf
        
        # weighted mean
        for i in np.arange(0,lenx,rebin):
            w = 1./dx[i:i+rebin-1]**2
            wsum = np.sum(w)
            
            if wsum == 0:
                x_rebin.append(np.mean(x[i:i+rebin-1]))
                dx_rebin.append(np.std(x[i:i+rebin-1]))
            else:
                x_rebin.append(np.sum(x[i:i+rebin-1]*w)/wsum)
                dx_rebin.append(1./wsum**0.5)
        return np.array([x_rebin,dx_rebin])
            
    # ======================================================================= #
    def __repr__(self):
        """
            Nice printing of parameters.
        """
        
        d = self.__dict__
        dkeys = list(d.keys())
        if dkeys:
            items = []
            dkeys.sort()
            for key in dkeys:
                if not hasattr(d[key],'__iter__') or d[key].__class__ == bdict:
                    items.append([key,d[key]])                
                elif d[key].__class__ == str:
                    items.append([key,d[key]])                
                else:
                    items.append([key,d[key].__class__])
                
                            
            m = max(map(len,dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"

    # ======================================================================= #
    def asym(self,option="",omit="",rebin=1,hist_select=''):
        """Calculate and return the asymmetry for various run types. 
           
        usage: asym(option="",omit="",rebin=1,hist_select='')
            
        Inputs:
            option:         see below for details
            omit:           1f bins to omit if space seperated string in options 
                                is not feasible. See options description below.
            rebin:          SLR only. Weighted average over 'rebin' bins to 
                                reduce array length by a factor of rebin. 
            hist_select:    string to specify which histograms get combined into 
                                making the asymmetry calculation. Deliminate 
                                with [,] or [;]. Histogram names cannot 
                                therefore contain either of these characters.
            
        Asymmetry calculation outline (with default detectors) ---------------
        
            Split helicity      (NMR): (F-B)/(F+B) for each
            Combined helicity   (NMR): (r-1)/(r+1)
                where r = sqrt([(B+)(F-)]/[(F+)(B-)])
            
            Split helicity      (NQR): (R-L)/(R+L) for each
            Combined helicity   (NQR): (r-1)/(r+1)
                where r = sqrt([(L+)(R-)]/[(R+)(L-)])
            
            Alpha diffusion     (NQR) sum(AL0)/sum(L+R)
            Alpha tagged        (NQR) same as NQR, but using the tagged counters
            
        Histogram Selection ---------------------------------------------------
        
            If we wished to do a simple asymmetry calculation in the form of 
                                    
                                    (F-B)/(F+B)
            
            for each helicity, then 
                                       |--|  |--|   paired counter location
                        hist_select = 'F+,F-,B+,B-'
                                        |-----|       paired helicities
                                           |-----|
            
            for alpha diffusion calculations append the two alpha counters
            
                hist_select = 'R+,R-,L+,L-,A+,A-
            
            for alpha tagged calculations do the following
            
                hist_select = 'R+,R-,L+,L-,TR+,TR-,TL+,TL-,nTR+,nTR-,nTL+,nTL-'
                    
                where TR is the right counter tagged (coincident) with alphas, 
                      TL is the left  counter tagged with alphas, 
                     nTR is the right counter tagged with !alphas (absence of), 
                     nLR is the right counter tagged with !alphas, 
                                          
                  
        Status of Data Corrections --------------------------------------------
            SLR/2H: 
                Removes prebeam bins. 
                
                Rebinning: 
                    returned time is average time over rebin range
                    returned asym is weighted mean
                
            1F: 
                Allows manual removal of unwanted bins. 
                
                Scan Combination:
                    Multiscans are considered as a single scan with long 
                    integration time. Histogram bins are summed according to 
                    their frequency bin, errors are Poisson.
            
            1N:
                Same as 1F. Uses the neutral beam monitor values to calculate 
                asymetries in the same manner as the NMR calculation. 
             
            2E: 
                Prebeam bin removal. 
                Postbeam bin removal. Assumes beamoff time is 0. 
                Splits saved 1D histograms into 2D.
                
                Asymmetry calculations: 
                    raw: calculated through differences method (as described in 
                        the asymmetry calculation outline)
                    dif: let 0 be the index of the centermost scan in time. dif 
                        asymmetries are then calculated via raw[i+1]-raw[i-1], 
                        where "raw" is as calculated in the above line, for each 
                        of the three types: +,-,combined 
                    sl: take a weighted least squares fit to the two bins prior 
                        and the two bins after the center bin (in time). For 
                        each find the value of the asymmetry at the center time 
                        position. Take the difference: post-prior
                    
        Option List
        
            SLR DESCRIPTIONS --------------------------------------------------
            
            "":     dictionary of 2D numpy arrays keyed by 
                        {"p","n","c","time_s"} for each helicity and combination 
                        (val,err). Default return state for unrecognized options
            "h":    dictionary 2D numpy arrays keyed by {"p","n","time_s"} for 
                        each helicity (val,err).
            "p":    2D np array of up helicity state [time_s,val,err].
            "n":    2D np array of down helicity state [time_s,val,err].
            "c":    2D np array of combined asymmetry [time_s,val,err].
            "ad":   2D np array of alpha diffusion ratio [time_s,val,err].
            "at":   dictionary of alpha tagged asymmetries key:[val,err]. 
                    Keys:
                        
                        'time_s'               : 1D array of times in seconds   
                        'p_wiA','n_wiA','c_wiA': coincident with alpha
                        'p_noA','n_noA','c_noA': coincident with no alpha
                        'p_noT','n_noT','c_noT': untagged
                        
                where p,n,c refer to pos helicity, neg helicity, combined 
                helicity respectively. Only in 2h mode. 
                        
            
            1F DESCRIPTIONS ---------------------------------------------------
            
                all options can include a space deliminated list of bins or 
                ranges of bins which will be omitted. ex: "raw 1 2 5-20 3"
            
            "":     dictionary of 2D numpy arrays keyed by {p,n,c,freq} for each 
                        helicity and combination [val,err]. Default return state 
                        for unrecognized options.
            "r":    Dictionary of 2D numpy arrays keyed by {p,n} for each 
                        helicity (val,err), but listed by bin, not combined by 
                        frequency. 
            "h":    get unshifted +/- helicity scan-combined asymmetries as a 
                        dictionary {'p':(val,err),'n':(val,err),'freq'}
            "p":    get pos helicity states as tuple, combined by frequency 
                        (freq,val,err)
            "n":    similar to p but for negative helicity states
            "c":    get combined helicity states as tuple (freq,val,err)
            
                        
            2E DESCRIPTIONS ---------------------------------------------------
            
                Takes no options. Returns a dictionary with the keys: 
             
            'dif_p':    [val,err][frequency] of pos. helicity asymmetry 
            'dif_n':    [ve][f] of negative helicity asymmetry
            'dif_c':    [ve][f] of combined helicity asymmetry
            
            'raw_p':    [ve][f][time] raw asymmetries of each time bin. Pos hel. 
            'raw_n':    [ve][f][t] negative helicity.
            'raw_c':    [ve][f][t] combined helicity
            
            'freq':     [f] frequency values
            'time':     [t] time bin values
                
            'sl_p':     [ve][f] pos. hel. of asymmetry calcuated through slopes 
                            of pre and post middle time bin. Slope method only 
                            for >= 5 time bins, corresponds to >= 3 RF on delays
            'sl_n':     [ve][f] negative helicity.
            'sl_c':     [ve][f] combined helicity.
        """
        
        # check rebin factor
        if type(rebin) not in (int,np.int64) or rebin < 1:
            raise RuntimeError('Rebinning factor must be int >= 1.')
        
        # check for additonal options (1F)
        if omit != '':
            further_options = list(map(str.strip,omit.split(' ')))
        else:
            further_options = list(map(str.strip,option.split(' ')[1:]))
        option = option.split(' ')[0].strip()
        
        # Option reduction
        option = option.lower()
        if option == ""                                     : pass
        elif option in ['+','up','u','p','pos','positive']  : option = 'positive'
        elif option in ['-','down','d','n','neg','negative']: option = 'negative'
        elif option in ["c","com","combined"]               : option = "combined"
        elif option in ["h","hel","helicity"]               : option = 'helicity'
        elif option in ["r","raw"]                          : option = 'raw'
        elif option in ['adif','ad','adiff']                : option = 'alpha_diffusion'
        elif option in ['atag','at']                        : option = 'alpha_tagged'
        else:
            raise RuntimeError("Option not recognized.")
        
        # get data
        if hist_select != '':
            
            # split into parts
            hist_select_temp = []
            for histname in hist_select.split(','):
                hist_select_temp.extend(histname.split(';'))
            hist_select = [h.strip() for h in hist_select_temp]
            
            # check for user error
            if len(hist_select) < 4:
                raise RuntimeError('hist_select must be a string of at least '+\
                        'four [,]-seperated or [;]-seperated histogram names')
            
            # get data
            d = [self.hist[h].data for h in hist_select]
            d_all = d
            
        # get default data
        else:
            d = self._get_area_data() # 1+ 2+ 1- 2-
            d_all = d
            
        # get alpha diffusion data
        if self.mode == '2h':
            d_alpha = d[4:]
            d = d[:4]
        
        # SLR -----------------------------------------------------------------
        if self.mode in ["20",'2h']:
            
            # calculate background
            n_prebeam = int(self.ppg['prebeam'].mean)
            
            # remove negative count values,
            # delete prebeam entries
            for i in range(len(d)):
                d[i][d[i]<0] = 0.
                d[i] = np.delete(d[i],np.arange(n_prebeam))

            # do alpha background subtractions
            if self.mode == '2h':    
                for i in range(len(d_alpha)):
                    d_alpha[i][d_alpha[i]<0] = 0.
                    d_alpha[i] = np.delete(d_alpha[i],np.arange(n_prebeam))
                
            # get helicity data
            if option != 'combined':
                h = np.array(self._get_asym_hel(d))
                
            # rebin time
            time = (np.arange(len(d[0]))+0.5)*self.ppg['dwelltime'].mean/1000
            if rebin > 1:
                len_t = len(time)
                new_time = (np.average(time[i:i+rebin-1]) for i in np.arange(0,len_t,rebin))
                time = np.fromiter(new_time,dtype=float,count=int(len_t/rebin))

            # mode switching
            if option == 'positive': # ---------------------------------------
                return np.vstack([time,self._rebin(h[0],rebin)])
                
            elif option == 'negative': # -------------------------------------
                return np.vstack([time,self._rebin(h[1],rebin)])

            elif option == 'helicity': # -------------------------------------
                out = bdict()
                out['p'] = self._rebin(h[0],rebin)
                out['n'] = self._rebin(h[1],rebin)
                out['time_s'] = time
                return out

            elif option == 'combined': # -------------------------------------
                c = np.array(self._get_asym_comb(d))
                return np.vstack([time,self._rebin(c,rebin)])
                
            elif option == 'alpha_diffusion': # ------------------------------
                try:
                    asym = self._get_asym_alpha(d_alpha,d)
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise RuntimeError('Run is not in 2h mode.')
                return np.vstack([time,self._rebin(asym,rebin)])
            
            elif option == 'alpha_tagged': # ---------------------------------
                try:
                    asym = self._get_asym_alpha_tag(d_alpha,d)  
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise RuntimeError('Run is not in 2h mode.')
                    else:
                        raise err
                
                out = bdict()
                out['p_wiA'] = self._rebin(asym[0][0],rebin)
                out['n_wiA'] = self._rebin(asym[0][1],rebin)
                out['p_noA'] = self._rebin(asym[1][0],rebin)
                out['n_noA'] = self._rebin(asym[1][1],rebin)
                out['p_noT'] = self._rebin(asym[2][0],rebin)
                out['n_noT'] = self._rebin(asym[2][1],rebin)
                out['c_wiA'] = self._rebin(asym[3],rebin)
                out['c_noA'] = self._rebin(asym[4],rebin)
                out['c_noT'] = self._rebin(asym[5],rebin)
                out['time_s'] = time
                
                return out
            
            else:
                c = np.array(self._get_asym_comb(d))
                
                out = bdict()
                out['p'] = self._rebin(h[0],rebin)
                out['n'] = self._rebin(h[1],rebin)
                out['c'] = self._rebin(c,rebin)  
                out['time_s'] = time
                return out
        
        # 1F ------------------------------------------------------------------
        elif self.mode in ['1f','1n']:
            
            # get xaxis label and data key
            if self.mode == '1f':
                xlabel = 'Frequency'
                xlab = 'freq'
            elif self.mode == '1n':
                xlabel = 'Rb Cell mV set'
                xlab = 'mV'
            
            # get bins to kill
            bin_ranges_str = further_options 
            bin_ranges = []
            for b in bin_ranges_str:
                if not '-' in b:
                    bin_ranges.append(int(b))
                else:
                    one = int(b.split('-')[0])
                    two = int(b.split('-')[1])
                    bin_ranges.extend(np.arange(one,two+1))
            
            # kill bins
            for i in range(len(d)):

                # get good bin range
                if len(bin_ranges) > 0:
                    bin_ranges = np.array(bin_ranges)
                    idx = (bin_ranges>=0)*(bin_ranges<len(d[i]))
                    bin_ranges = bin_ranges[idx]

                # kill
                d[i][bin_ranges] = 0.
            
            # get frequency
            freq = self.hist[xlabel].data
            
            # mode switching
            if option =='raw':
                a = self._get_asym_hel(d)
                out = bdict()
                out['p'] = np.array(a[0])
                out['n'] = np.array(a[1])
                out[xlab] = np.array(freq)
                return out 
            else:
                freq,d = self._get_1f_sum_scans(d,freq)
                                       
            # rebin frequency
            if rebin>1:
                len_f = len(freq)
                newf = (np.average(freq[i:i+rebin-1]) for i in np.arange(0,len_f,rebin))
                freq = np.fromiter(newf,dtype=float,count=int(np.ceil(len_f/rebin)))
                                       
            # swtich between remaining modes
            if option == 'helicity':
                a = self._get_asym_hel(d)
                out = bdict()
                out['p'] = self._rebin(a[0],rebin)
                out['n'] = self._rebin(a[1],rebin)
                out[xlab] = np.array(freq)
                return out
            
            elif option == 'positive':
                a = self._get_asym_hel(d)
                return np.vstack([freq,self._rebin(a[0],rebin)])
            
            elif option == 'negative':
                a = self._get_asym_hel(d)
                return np.vstack([freq,self._rebin(a[1],rebin)])
            
            elif option in ['combined']:
                a = self._get_asym_comb(d)
                return np.vstack([freq,self._rebin(a,rebin)])
            else:
                ah = self._get_asym_hel(d)
                ac = self._get_asym_comb(d)
                
                out = bdict()
                out['p'] = self._rebin(ah[0],rebin)
                out['n'] = self._rebin(ah[1],rebin)
                out['c'] = self._rebin(ac,rebin)  
                out[xlab] = np.array(freq)
                return out
            
        # 2E ------------------------------------------------------------------
        elif self.mode in ['2e']:
            return self._get_2e_asym()
        
        # unknown entry -------------------------------------------------------
        else:
            print("Unknown run type.")
            return

    # ======================================================================= #
    def beam_kev(self,get_error=False):
        """
            Get the beam energy in kev, based on typical biases: 
                itw (or ite bias) - bias15 - platform bias
                
            if get_error: fetch error in value, rather than value
        """
        
        # get epics pointer
        epics = self.epics
        
        # fetch stds
        if get_error:
            attr = 'std'
        else:
            attr = 'mean'
        
        # get inital beam energy in keV
        beam = getattr(epics.target_bias,attr)/1000.
            
        # get RB cell voltage
        bias15 = getattr(epics.bias15,attr)/1000.
        
        # get platform bias 
        if self.area == 'BNMR':
            platform = getattr(epics.nmr_bias,attr)
        elif self.area == 'BNQR':
            platform = getattr(epics.nqr_bias,attr)/1000.
        else:
            raise RuntimeError('Area not recognized')
        
        if get_error:
            return np.sqrt(np.sum(np.square((beam,bias15,platform)))) # keV
        else:
            return beam-bias15-platform # keV

    # ======================================================================= #
    def get_pulse_s(self):
        """Get pulse duration in seconds, for pulsed measurements."""
        
        try:
            dwelltime = self.ppg.dwelltime.mean
            beam_on = self.ppg.beam_on.mean
        except AttributeError:
            raise AttributeError("Missing logged ppg parameter: dwelltime "+\
                    "or beam_on")
        return dwelltime*beam_on/1000.
    
# =========================================================================== #
# DATA CONTAINERS
# =========================================================================== #
class bcontainer(object):
    """
        Provides common functions for data containers
    """

    def __repr__(self):
        if list(self.__dict__.keys()):
            m = max(map(len,self.__dict__.keys())) + 1
            s = ''
            s += '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.__dict__.items())])
            return s
        else:
            return self.__class__.__name__ + "()"

# =========================================================================== #
class bdict(dict):
    """
        Provides common functions for dictionaries of data containers
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
    def __repr__(self):
        klist = list(self.keys())
        if klist:
            klist.sort()
            s = self.__class__.__name__+': {'
            for k in self.keys():
                s+="'"+k+"'"+', '
            s = s[:-2]
            s+='}'
            return s
        else:
            return self.__class__.__name__ + "()"
    
    def __dir__(self):
        return list(self.keys())

# =========================================================================== #
class bvar(bcontainer):
    """
        Independent variable associated with bdata object.
        
        Data fields:
            id_number
            low
            high
            mean
            std
            skew
            title
            description
            units
    """
        
    # arithmatic operators
    def __add__(self,other):        return self.mean+other
    def __sub__(self,other):        return self.mean-other
    def __mul__(self,other):        return self.mean*other
    def __truediv__(self,other):    return self.mean/other
    def __floordiv__(self,other):   return self.mean//other
    def __mod__(self,other):        return self.mean%other
    def __divmod__(self,other):     return divmod(self.mean,other)
    def __pow__(self,other):        return pow(self.mean,other)
    def __lshift__(self,other):     return self.mean<<other
    def __rshift__(self,other):     return self.mean>>other
    def __neg__(self):              return -self.mean
    def __pos__(self):              return +self.mean
    def __abs__(self):              return abs(self.mean)
    def __invert__(self):           return ~self.mean
    def __round__(self):            return round(self.mean)
    
    # casting operators
    def __complex__(self):          return complex(self.mean)
    def __int__(self):              return int(self.mean)
    def __float__(self):            return float(self.mean)
    def __str__(self):              return str(self.mean)
    
    # logic operators
    def __eq__(self,other):     
        if isinstance(other,bvar):  return self==other
        else:                       return self.mean==other
    def __lt__(self,other):     
        if isinstance(other,bvar):  return self.mean<other.mean
        else:                       return self.mean<other
    def __le__(self,other):
        if isinstance(other,bvar):  return self.mean<=other.mean
        else:                       return self.mean<=other
    def __gt__(self,other):
        if isinstance(other,bvar):  return self.mean>other.mean
        else:                       return self.mean>other
    def __ge__(self,other):
        if isinstance(other,bvar):  return self.mean>=other.mean
        else:                       return self.mean>=other
    
    def __and__(self,other):
        if isinstance(other,bvar):  return self&other
        else:                       return self.mean&other
    def __xor__(self,other):
        if isinstance(other,bvar):  return self^other
        else:                       return self.mean^other
    def __or__(self,other):
        if isinstance(other,bvar):  return self|other
        else:                       return self.mean|other
    
# =========================================================================== #
class bscaler(bcontainer):
    """
        Scaler associated with bdata object.
        
        Data fields:
            id_number
            title
            counts
    """
    
    # arithmatic operators
    def __add__(self,other):            return self.counts+other
    def __sub__(self,other):            return self.counts-other
    def __mul__(self,other):            return self.counts*other
    def __truediv__(self,other):        return self.counts/other
    def __floordiv__(self,other):       return self.counts//other
    def __mod__(self,other):            return self.counts%other
    def __divmod__(self,other):         return divmod(self.counts,other)
    def __pow__(self,other):            return pow(self.counts,other)
    def __lshift__(self,other):         return self.counts<<other
    def __rshift__(self,other):         return self.counts>>other
    def __neg__(self):                  return -self.counts
    def __pos__(self):                  return +self.counts
    def __abs__(self):                  return abs(self.counts)
    def __invert__(self):               return ~self.counts
    def __round__(self):                return round(self.counts)
        
    # casting operators 
    def __complex__(self):              return complex(self.counts)
    def __int__(self):                  return int(self.counts)
    def __float__(self):                return float(self.counts)
    def __str__(self):                  return str(self.counts)
    
    # logic operators
    def __eq__(self,other):     
        if isinstance(other,bscaler):   return self==other
        else:                           return self.counts==other
    def __lt__(self,other):     
        if isinstance(other,bscaler):   return self.counts<other.counts
        else:                           return self.counts<other
    def __le__(self,other):
        if isinstance(other,bscaler):   return self.counts<=other.counts
        else:                           return self.counts<=other
    def __gt__(self,other):
        if isinstance(other,bscaler):   return self.counts>other.counts
        else:                           return self.counts>other
    def __ge__(self,other):
        if isinstance(other,bscaler):   return self.counts>=other.counts
        else:                           return self.counts>=other
    
    def __and__(self,other):
        if isinstance(other,bscaler):   return self&other
        else:                           return self.counts&other
    def __xor__(self,other):
        if isinstance(other,bscaler):   return self^other
        else:                           return self.counts^other
    def __or__(self,other):
        if isinstance(other,bscaler):   return self|other
        else:                           return self.counts|other
        
# =========================================================================== #
class bhist(bcontainer):
    """
        Histogram associated with bdata object.
        
        Data fields:
            id_number
            htype 
            title
            data
            n_bytes
            n_bins
            n_events
            fs_per_bin
            s_per_bin
            t0_ps
            t0_bin
            good_bin1
            good_bin2
            background1
            background2
    """
    
    # arithmatic operators
    def __add__(self,other):        
        if isinstance(other,bhist): return self.data+other.data
        else:                       return self.data+other
    def __sub__(self,other):
        if isinstance(other,bhist): return self.data-other.data
        else:                       return self.data-other
    def __mul__(self,other):
        if isinstance(other,bhist): return self.data*other.data
        else:                       return self.data*other
    def __truediv__(self,other):
        if isinstance(other,bhist): return self.data/other.data
        else:                       return self.data/other
    def __floordiv__(self,other):
        if isinstance(other,bhist): return self.data//other.data
        else:                       return self.data//other
    def __mod__(self,other):
        if isinstance(other,bhist): return self.data%other.data
        else:                       return self.data%other
    def __divmod__(self,other):     
        if isinstance(other,bhist): return np.divmod(self.data,other.data)
        else:                       return np.divmod(self.data,other)
    def __pow__(self,other):        
        if isinstance(other,bhist): return np.pow(self.data,other.data)
        else:                       return np.pow(self.data,other)
    def __neg__(self):              return -self.data
    def __abs__(self):              return np.abs(self.data)
    def __invert__(self):           return ~self.data
    def __round__(self):            return np.round(self.data)
    
    # casting operators
    def astype(self,type):          return self.data.astype(type)
    
    # logic operators
    def __eq__(self,other):     
        if isinstance(other,bhist): return self==other
        else:                       return self.data==other
    def __lt__(self,other):     
        if isinstance(other,bhist): return self.data<other.data
        else:                       return self.data<other
    def __le__(self,other):
        if isinstance(other,bhist): return self.data<=other.data
        else:                       return self.data<=other
    def __gt__(self,other):
        if isinstance(other,bhist): return self.data>other.data
        else:                       return self.data>other
    def __ge__(self,other):
        if isinstance(other,bhist): return self.data>=other.data
        else:                       return self.data>=other
    
    def __and__(self,other):
        if isinstance(other,bhist): return self.data&other.data
        else:                       return self.data&other
    def __xor__(self,other):       
        if isinstance(other,bhist): return self.data^other.data
        else:                       return self.data^other
    def __or__(self,other):         
        if isinstance(other,bhist): return self.data|other.data
        else:                       return self.data|other

# set lifetimes for various particles in seconds, with errors (ref: rmlm slr_v2.cpp)
# commented out isotopes with multiple decay products not taken into account by bfit
life = bdict({
            "Li8"       :1.2096,    # http://journals.aps.org/prc/abstract/10.1103/PhysRevC.82.027309
            "Li8_err"   :0.0005, 
            "Li9"       :0.2572,    # http://journals.aps.org/prc/abstract/10.1103/PhysRevC.13.835
            "Li9_err"   :0.0006, 
#            "Li11"      :0.0126,   # http://www.sciencedirect.com/science/article/pii/S0375947412000413
#            "Li11_err"  :0.0020, 
            "Be11"      :19.85,     # http://www.sciencedirect.com/science/article/pii/S0375947412000413
            "Be11_err"  :0.10,   
            "F20"       :16.105,    # http://www.sciencedirect.com/science/article/pii/037594749290251E
            "F20_err"   :0.012,  
#            "Mg29"      :1.88,     # http://www.sciencedirect.com/science/article/pii/S0375947403018074
#            "Mg29_err"  :0.17,   
            "Mg31"      :0.332,     # http://www.sciencedirect.com/science/article/pii/S0375947403018074
            "Mg31_err"  :0.029,   
            "Ac230"     :121.8,     # N. E. Table of the isotopes, Brookhaven National Laboratory, Upton, New York, 2002.
            "Ac234"     :40,        # N. E. Table of the isotopes, Brookhaven National Laboratory, Upton, New York, 2002.
        })
