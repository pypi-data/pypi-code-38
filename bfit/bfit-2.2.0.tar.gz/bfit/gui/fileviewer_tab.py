# File viewer tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk
from multiprocessing import Process, Pipe
from bfit.gui.zahersCalculator import current2field
from bfit.gui.fitdata import fitdata
from bdata import bdata
from bfit import logger_name

import numpy as np
import matplotlib.pyplot as plt
import sys,os,time,glob,datetime
import logging


__doc__ = """
    View file contents tab.
    
    To-do:
        2e mode viewing
        NBM viewing
        cumulative count viewing
    """

# =========================================================================== #
class fileviewer(object):
    """
        Data fields:
            year: IntVar() year of exp 
            runn: IntVar() run number
            entry_asym_type: combobox for asym calculations
            text: Text widget for displaying run information
            bfit: bfit object
            fig_list: list of figures
            asym_type: drawing style
            is_updating: True if update draw
            data: bdata object for drawing
    """
    
    asym_dict = {"Combined Helicity"        :'c',
                 "Split Helicity"           :'h',
                 "Matched Helicity"         :'hm',
                 "Shifted Split"            :'hs',
                 "Shifted Combined"         :'cs',
                 "Matched Peak Finding"     :'hp',
                 "Raw Scans"                :'r',
                 "Raw Histograms"           :'rhist',
                 "Combined Hel Raw"         :'2e_rw_c',
                 "Combined Hel Slopes"      :'2e_sl_c',
                 "Combined Hel Diff"        :'2e_di_c',
                 "Split Hel Raw"            :'2e_rw_h',
                 "Split Hel Slopes"         :'2e_sl_h',
                 "Split Hel Diff"           :'2e_di_h',
                 "Alpha Diffusion"          :'ad',
                 "Combined Hel (Alpha Tag)" :"at_c",
                 "Split Hel (Alpha Tag)"    :"at_h",
                 "Combined Hel (!Alpha Tag)":"nat_c",
                 "Split Hel (!Alpha Tag)"   :"nat_h",
                 }
    default_export_filename = "%d_%d.csv" # year_run.csv
    
    # ======================================================================= #
    def __init__(self,file_tab,bfit):
        """ Position tab tkinter elements"""
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')
        
        # year and filenumber entry ------------------------------------------
        entry_frame = ttk.Frame(file_tab,borderwidth=1)
        self.year = IntVar()
        self.runn = IntVar()
        self.rebin = IntVar()
        self.bfit = bfit
        
        self.year.set(self.bfit.get_latest_year())
        self.rebin.set(1)
        
        entry_year = Spinbox(entry_frame,\
                from_=2000,to=datetime.datetime.today().year,
                textvariable=self.year,width=5)
        self.entry_runn = Spinbox(entry_frame,\
                from_=0,to=50000,
                textvariable=self.runn,width=7)
        self.runn.set(40000)
        
        # fetch button
        fetch = ttk.Button(entry_frame,text='Fetch',command=self.get_data)
            
        # draw button
        draw = ttk.Button(entry_frame,text='Draw',command=self.draw)
        
        # grid and labels
        entry_frame.grid(column=0,row=0,sticky=N)
        ttk.Label(entry_frame,text="Year:").grid(column=0,row=0,sticky=E)
        entry_year.grid(column=1,row=0,sticky=E)
        ttk.Label(entry_frame,text="Run Number:").grid(column=2,row=0,sticky=E)
        self.entry_runn.grid(column=3,row=0,sticky=E)
        fetch.grid(column=4,row=0,sticky=E)
        draw.grid(column=5,row=0,sticky=E)
        
        # padding 
        for child in entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        # viewer frame -------------------------------------------------------
        view_frame = ttk.Frame(file_tab,borderwidth=2)
        
        self.text_nw = Text(view_frame,width=80,height=20,state='normal')
        self.text_ne = Text(view_frame,width=80,height=20,state='normal')
        self.text_sw = Text(view_frame,width=80,height=20,state='normal')
        self.text_se = Text(view_frame,width=80,height=20,state='normal')
        
        ttk.Label(view_frame,text="Run Info").grid(column=0,row=0,sticky=N)
        ttk.Label(view_frame,text="PPG Parameters").grid(column=1,row=0,sticky=N)
        ttk.Label(view_frame,text="Camp").grid(column=0,row=2,sticky=N)
        ttk.Label(view_frame,text="EPICS").grid(column=1,row=2,sticky=N)
        
        self.text_nw.grid(column=0,row=1,sticky=(N))
        self.text_ne.grid(column=1,row=1,sticky=(N))
        self.text_sw.grid(column=0,row=3,sticky=(N))
        self.text_se.grid(column=1,row=3,sticky=(N))
        
        view_frame.grid(column=0,row=1,sticky=(N,E,W))
        
        # details frame: stuff at the bottom ----------------------------------
        details_frame = ttk.Frame(file_tab)
        entry_rebin = Spinbox(details_frame,from_=1,to=100,width=3,\
                textvariable=self.rebin)
        
        # update check box
        self.is_updating = BooleanVar()
        self.is_updating.set(False)
        update_box = Checkbutton(details_frame,text='Periodic Redraw',
                command=self.do_update,variable=self.is_updating,onvalue=True,
                offvalue=False)

        # asymmetry type combobox
        self.asym_type = StringVar()
        self.asym_type.set('')
        self.entry_asym_type = ttk.Combobox(details_frame,\
                textvariable=self.asym_type,state='readonly',width=25)
        self.entry_asym_type['values'] = ()
                
        # gridding
        ttk.Label(details_frame,text="Rebin:").grid(column=0,row=0,sticky=E)
        entry_rebin.grid(column=1,row=0,sticky=E)
        self.entry_asym_type.grid(column=2,row=0,sticky=E)
        update_box.grid(column=3,row=0,sticky=E)
        details_frame.grid(column=0,row=2,sticky=S)
        
        # padding 
        for child in details_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
            
        # resizing
        file_tab.grid_rowconfigure(1,weight=1)
        file_tab.grid_columnconfigure(0,weight=1)
        
        entry_frame.grid_columnconfigure(0,weight=2)
        entry_frame.grid_columnconfigure(2,weight=1)
        entry_frame.grid_rowconfigure(0,weight=1)
        
        for i in range(4):
            view_frame.grid_columnconfigure(i,weight=1)
        view_frame.grid_rowconfigure(1,weight=1)
        view_frame.grid_rowconfigure(3,weight=1)
        
        for t in [self.text_nw,self.text_ne,self.text_sw,self.text_se]:
            for i in range(5):
                t.grid_columnconfigure(i,weight=1)
                t.grid_rowconfigure(i,weight=1)
            
        self.logger.debug('Initialization success.')
            
    # ======================================================================= #
    def __del__(self):
        pass
        
    # ======================================================================= #
    def draw(self):
        """Get data then draw."""
        if self.get_data():
            self.bfit.draw(self.data,\
                    self.asym_dict[self.asym_type.get()],rebin=self.rebin.get(),
                    label=self.bfit.get_label(self.data))
            
    # ======================================================================= #
    def export(self):
        """Export data as csv"""
        
        self.logger.info('Export button pressed')
        
        # get data
        if not self.get_data():
            return
        data = self.data
        
        # get filename 
        filename = filedialog.asksaveasfilename(
                initialfile=self.default_export_filename%(data.year,data.run))
        
        # write to file
        self.bfit.export(data,filename)
    
    # ======================================================================= #
    def get_data(self):
        """Display data and send bdata object to bfit draw list. 
        Return True on success, false on Failure
        """
        
        # settings
        mode_dict = {"20":"SLR","1f":"Frequency Scan","1n":"Rb Cell Scan",
                    '2h':'SLR with Alpha Tracking','2s':'Spin Echo',
                    '2e':'Randomized Frequency Scan'}
        
        # fetch year
        try:
            year = self.year.get()
        except ValueError:
            for t in [self.text_nw,self.text_ne,self.text_sw,self.text_se]:
                self.set_textbox_text(t,'Year input must be integer valued')  
                self.logger.exception('Year input must be integer valued')
            return False
        
        # fetch run number
        run = self.runn.get()
        
        self.logger.debug('Parsing run input %s',run)
        
        if run < 40000:
            
            # look for latest run by run number
            runlist = []
            for d in [self.bfit.bnmr_archive_label,self.bfit.bnqr_archive_label]:
                dirloc = os.environ[d]
                runlist.extend(glob.glob(os.path.join(dirloc,str(year),'0'+str(run))+'*.msr'))
            runlist = [int(os.path.splitext(os.path.basename(r))[0]) for r in runlist]
            
            # get latest run by max run number
            try:
                run = max(runlist)
            except ValueError:
                self.logger.exception('Run fetch failed')
                for t in [self.text_nw,self.text_ne,self.text_sw,self.text_se]:
                    self.set_textbox_text(t,'Run not found.')  
                return False
        
        self.logger.info('Fetching run %s from %s',run,year)
        
        # get data
        try: 
            data = fitdata(self.bfit,bdata(run,year=year))
        except ValueError:
            self.logger.exception('File read failed.')
            for t in [self.text_nw,self.text_sw,self.text_se,self.text_ne]:
                self.set_textbox_text(t,'File read failed.')
            return False
        except RuntimeError:
            self.logger.exception('File does not exist.')
            for t in [self.text_nw,self.text_sw,self.text_se,self.text_ne]:
                self.set_textbox_text(t,'File does not exist.')
            return False
        
        # set draw parameters
        self.bfit.set_asym_calc_mode_box(data.mode)
        
        # NE -----------------------------------------------------------------
        
        # get data: headers
        mode = mode_dict[data.mode]
        try:
            if data.ppg.rf_enable.mean and data.mode == '20':
                mode = "Hole Burning"
        except AttributeError:
            pass
        
        mins,sec = divmod(data.duration, 60)
        duration = "%dm %ds" % (mins,sec)
        
        # set dictionary
        data_nw =  {"Run":'%d (%d)' % (data.run,data.year),
                    "Area": data.area,
                    "Run Mode": "%s (%s)" % (mode,data.mode),
                    "Title": data.title,
                    "Experimenters": data.experimenter,
                    "Sample": data.sample,
                    "Orientation":data.orientation,
                    "Experiment":str(data.exp),
                    "Run Duration": duration,
                    "Start": data.start_date,
                    "End": data.end_date,
                    "":"",
                    }
        
        # set key order 
        key_order_nw = ['Run','Run Mode','Title','',
                        'Start','End','Run Duration','',
                        'Sample','Orientation','',
                        'Experiment','Area','Experimenters',
                        ]
        
        # SW -----------------------------------------------------------------
        data_sw = {'':''}
        key_order_sw = []
                        
        # get data: temperature and fields
        try:
            temp = data.camp.smpl_read_A.mean
            temp_stdv = data.camp.smpl_read_A.std
            data_sw["Temperature"] = "%.2f +/- %.2f K" % (temp,temp_stdv)
            key_order_sw.append('Temperature')
        except AttributeError:
            pass
        
        try:
            curr = data.camp.smpl_current
            data_sw["Heater Current"] = "%.2f +/- %.2f A" % (curr.mean,curr.std)
            key_order_sw.append('Heater Current')
        except AttributeError:
            pass
        
        try:
            temp = data.camp.oven_readC.mean
            temp_stdv = data.camp.oven_readC.std
            data_sw['Oven Temperature'] = "%.2f +/- %.2f K" % (temp,temp_stdv)
            key_order_sw.append('Oven Temperature')
        except AttributeError:
            pass
        
        try:
            curr = data.camp.oven_current
            data_sw['Oven Current'] = "%.2f +/- %.2f A" % (curr.mean,curr.std)
            key_order_sw.append('Oven Current')
        except AttributeError:
            pass
        
        try: 
            field = np.around(data.camp.b_field.mean,3)
            field_stdv = np.around(data.camp.b_field.std,3)
            data_sw['Magnetic Field'] = "%.3f +/- %.3f T" % (field,field_stdv)
            key_order_sw.append('Magnetic Field')
        except AttributeError:
            pass
            
        key_order_sw.append('')
                
        # cryo options
        try: 
            mass = data.camp.mass_read
            data_sw['Mass Flow'] = "%.3f +/- %.3f" % (mass.mean,mass.std)
            key_order_sw.append('Mass Flow')
        except AttributeError:
            pass
    
        try: 
            cryo = data.camp.cryo_read
            data_sw['CryoEx Mass Flow'] = "%.3f +/- %.3f" % (cryo.mean,cryo.std)
            key_order_sw.append('CryoEx Mass Flow')
        except AttributeError:
            pass    
            
        try: 
            data_sw['Needle Setpoint'] = "%.3f turns" % data.camp.needle_set.mean
            key_order_sw.append('Needle Setpoint')
        except AttributeError:
            pass    
            
        try: 
            data_sw['Needle Readback'] = "%.3f turns" % data.camp.needle_pos.mean
            key_order_sw.append('Needle Readback')
        except AttributeError:
            pass    
            
        try:
            lift_set = np.around(data.camp.clift_set.mean,3)
            data_sw['Cryo Lift Setpoint'] = "%.3f mm" % lift_set
            key_order_sw.append('Cryo Lift Setpoint')
        except AttributeError:
            pass
        
        try:
            lift_read = np.around(data.camp.clift_read.mean,3)
            data_sw['Cryo Lift Readback'] = "%.3f mm" % lift_read
            key_order_sw.append('Cryo Lift Readback')
        except AttributeError:
            pass
            
        # rf dac
        if mode != 'SLR':
            key_order_sw.append('')
            try: 
                data_sw['rf_dac'] = "%d" % int(data.camp.rf_dac.mean)
                key_order_sw.append('rf_dac')
            except AttributeError:
                pass
            
            try: 
                data_sw['RF Amplifier Gain'] = "%.2f" % data.camp.rfamp_rfgain.mean
                key_order_sw.append('RF Amplifier Gain')
            except AttributeError:
                pass    
                
                
        # SE -----------------------------------------------------------------
        data_se = {'':''}
        key_order_se = []
            
        # get data: biases 
        try:
            if 'nqr_bias' in data.epics.keys():
                bias =      data.epics.nqr_bias.mean/1000.
                bias_std =  data.epics.nqr_bias.std/1000.
            elif 'nmr_bias' in data.epics.keys():
                bias =      data.epics.nmr_bias.mean
                bias_std =  data.epics.nmr_bias.std
            
            data_se["Platform Bias"] = "%.3f +/- %.3f kV" % \
                    (np.around(bias,3),np.around(bias_std,3))
            key_order_se.append("Platform Bias")
            
        except UnboundLocalError:
            pass
        
        try:
            data_se["BIAS15"] = "%.3f +/- %.3f V" % \
                    (np.around(data.epics.bias15.mean,3),
                     np.around(data.epics.bias15.std,3))
            key_order_se.append('BIAS15')
        except AttributeError:
            pass
        
        # get data: beam energy
        try: 
            init_bias = data.epics.target_bias.mean
            init_bias_std = data.epics.target_bias.std
        except AttributeError:
            try:
                init_bias = data.epics.target_bias.mean
                init_bias_std = data.epics.target_bias.std
            except AttributeError:
                pass
            
        try:
            val = np.around(init_bias/1000.,3)
            std = np.around(init_bias_std/1000.,3)
            data_se["Initial Beam Energy"] = "%.3f +/- %.3f keV" % (val,std)
            key_order_se.append('Initial Beam Energy')
        except UnboundLocalError:
            pass
        
        # Get final beam energy
        try: 
            val = np.around(data.beam_kev(),3)
            std = np.around(data.beam_kev(get_error=True),3)
            data_se['Implantation Energy'] = "%.3f +/- %.3f keV" % (val,std)
            key_order_se.append('Implantation Energy')
        except AttributeError:
            pass
        
        key_order_se.append('')
        
        # laser stuff
        try: 
            val = data.epics.las_pwr
            data_se['Laser Power'] = "%.3f +/- %.3f A" % (val.mean,val.std)
            key_order_se.append('Laser Power')
        except AttributeError:
            pass
        
        # magnet stuff
        try: 
            val = data.epics.hh_current.mean
            std = data.epics.hh_current.std
            data_se['Magnet Current'] = "%.3f +/- %.3f A" % (val,std)
            key_order_se.append('Magnet Current')
            
            val = current2field(val)
            data_se['Magnetic Field'] = "%.3f Gauss" % val
            key_order_se.append('Magnetic Field')
        except AttributeError:
            pass
        
        # NE -----------------------------------------------------------------
        data_ne = {'':''}
        key_order_ne = []
        
        # get data: SLR data
        if data.mode in ['20','2h']:
            try:
                dwell = int(data.ppg.dwelltime.mean)
                data_ne['Dwell Time'] = "%d ms" % dwell
                key_order_ne.append('Dwell Time')
            except AttributeError:
                pass
            
            try:    
                beam = int(data.ppg.prebeam.mean)            
                data_ne['Number of Prebeam Dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of Prebeam Dwelltimes')
            except AttributeError:
                pass
            
            try:    
                beam = int(data.ppg.beam_on.mean)            
                data_ne['Number of Beam On Dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of Beam On Dwelltimes')
            except AttributeError:
                pass
            
            try: 
                beam = int(data.ppg.beam_off.mean)
                data_ne['Number of Beam Off Dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of Beam Off Dwelltimes')
            except AttributeError:
                pass
            
            try:    
                rf = int(data.ppg.rf_on_delay.mean)
                data_ne['RF On Delay'] = "%d dwelltimes" % rf
                key_order_ne.append('RF On Delay')
            except AttributeError:
                pass
            
            try:    
                rf = int(data.ppg.rf_on.mean)
                data_ne['RF On Duration'] = "%d dwelltimes" % rf
                key_order_ne.append('RF On Duration')
            except AttributeError:
                pass
            
            try:    
                hel = bool(data.ppg.hel_enable.mean)
                data_ne['Flip Helicity'] = str(hel)
                key_order_ne.append('Flip Helicity')
            except AttributeError:
                pass
            
            try:    
                hel = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity Flip Sleep'] = "%d ms" % hel
                key_order_ne.append('Helicity Flip Sleep')
            except AttributeError:
                pass
        
            key_order_ne.append('')
            
            try:
                rf = bool(data.ppg.rf_enable.mean)
                data_ne['RF Enable'] = str(rf)
                key_order_ne.append('RF Enable')
                
                if rf:
                    freq = int(data.ppg.freq.mean)    
                    data_ne['Frequency'] = "%d Hz" % freq
                    key_order_ne.append('Frequency')
            except AttributeError:
                pass
            
        # get 1F specific data
        elif data.mode in ['1f']:
            try:
                val = int(data.ppg.dwelltime.mean)
                data_ne['Bin Width'] = "%d ms" % val
                key_order_ne.append('Bin Width')
            except AttributeError:
                pass
            
            try:    
                val = int(data.ppg.nbins.mean)
                data_ne['Number of Bins'] = "%d" % val
                key_order_ne.append('Number of Bins')
            except AttributeError:
                pass
            
            try:
                val = bool(data.ppg.const_t_btwn_cycl.mean)
                data_ne['Enable Const Time Between Cycles'] = str(val)
                key_order_ne.append('Enable Const Time Between Cycles')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.freq_start.mean)
                data_ne['Frequency Scan Start'] = '%d Hz' % val
                key_order_ne.append('Frequency Scan Start')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.freq_stop.mean)
                data_ne['Frequency Scan End'] = '%d Hz' % val
                key_order_ne.append('Frequency Scan End')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.freq_incr.mean)
                data_ne['Frequency Scan Increment'] = '%d Hz' % val
                key_order_ne.append('Frequency Scan Increment')
            except AttributeError:
                pass
            
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip Helicity'] = str(val)
                key_order_ne.append('Flip Helicity')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity Flip Sleep'] = "%d ms" % val
                key_order_ne.append('Helicity Flip Sleep')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.ncycles.mean)
                data_ne['Number of Cycles per Scan Increment'] = '%d' % val
                key_order_ne.append('Number of Cycles per Scan Increment')
            except AttributeError:
                pass
            
        # get Rb Cell specific data
        elif data.mode in ['1n']:
            
            try:
                dwell = int(data.ppg.dwelltime.mean)
                data_ne['Bin Width'] = "%d ms" % dwell
                key_order_ne.append('Bin Width')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.volt_start.mean)
                data_ne['Start Rb Scan'] = '%d Volts' % val
                key_order_ne.append('Start Rb Scan')
            except AttributeError:
                pass
            
            try:    
                val = int(data.ppg.volt_stop.mean)
                data_ne['Stop Rb Scan'] = '%d Volts' % val
                key_order_ne.append('Stop Rb Scan')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.volt_incr.mean)
                data_ne['Scan Increment'] = '%d Volts' % val
                key_order_ne.append('Scan Increment')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.nbins.mean)
                data_ne['Number of Bins'] = '%d' % val
                key_order_ne.append('Number of Bins')
            except AttributeError:
                pass
            
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip Helicity'] = str(val)
                key_order_ne.append('Flip Helicity')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity Flip Sleep'] = "%d ms" % val
                key_order_ne.append('Helicity Flip Sleep')
            except AttributeError:
                pass
        
        # get 2e mode specific data
        elif data.mode in ['2e']:
            
            try:
                val = int(data.ppg.rf_on_ms.mean)
                data_ne['RF On Time'] = "%d ms" % val
                key_order_ne.append('RF On Time')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.rf_on_delay.mean)
                data_ne['Number of RF On Delays'] = "%d" % val
                key_order_ne.append('Number of RF On Delays')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.beam_off_ms.mean)
                data_ne['Beam Off Time'] = "%d ms" % val
                key_order_ne.append('Beam Off Time')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.ndwell_post_on.mean)
                data_ne['Number of post RF BeamOn Dwelltimes'] = "%d" % val
                key_order_ne.append('Number of post RF BeamOn Dwelltimes')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.ndwell_per_f.mean)
                data_ne['Number of Dwelltimes per Frequency'] = "%d" % val
                key_order_ne.append('Number of Dwelltimes per Frequency')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.freq_start.mean)
                data_ne['Frequency Scan Start'] = "%d Hz" % val
                key_order_ne.append('Frequency Scan Start')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.freq_stop.mean)
                data_ne['Frequency Scan Stop'] = "%d Hz" % val
                key_order_ne.append('Frequency Scan Stop')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.freq_incr.mean)
                data_ne['Frequency Scan Increment'] = "%d Hz" % val
                key_order_ne.append('Frequency Scan Increment')
            except AttributeError:
                pass
                
            try:
                val = bool(data.ppg.rand_freq_val.mean)
                data_ne['Randomize Frequency Scan Increments'] = str(val)
                key_order_ne.append('Randomize Frequency Scan Increments')
            except AttributeError:
                pass
                
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip Helicity'] = str(val)
                key_order_ne.append('Flip Helicity')
            except AttributeError:
                pass
                
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Helicity Flip Sleep'] = "%d ms" % val
                key_order_ne.append('Helicity Flip Sleep')
            except AttributeError:
                pass
                
            key_order_ne.append('')
            
        
        # set viewer string
        def set_str(data_dict,key_order,txtbox):
        
            m = max(max(map(len, list(data_dict.keys()))) + 1,5)
            s = '\n'.join([k.rjust(m)+': ' + data_dict[k] for k in key_order])
            self.set_textbox_text(txtbox,s)
        
        set_str(data_nw,key_order_nw,self.text_nw)
        set_str(data_ne,key_order_ne,self.text_ne)
        set_str(data_sw,key_order_sw,self.text_sw)
        set_str(data_se,key_order_se,self.text_se)
        
        # set data field
        self.data = data
        
        return True
   
    # ======================================================================= #
    def set_textbox_text(self,textbox,text):
        """Set the text in a tkinter Text widget"""
        textbox.delete('1.0',END)
        textbox.insert('1.0',text)
        
    # ======================================================================= #
    def do_update(self):
        
        self.logger.debug('Draw via periodic update')
        if self.is_updating.get():
            self.draw()
            print('\rLast update:',str(datetime.datetime.now()).split('.')[0],
                  end='',flush=True)
            self.bfit.root.after(self.bfit.update_period*1000,self.do_update)
        
# =========================================================================== #

