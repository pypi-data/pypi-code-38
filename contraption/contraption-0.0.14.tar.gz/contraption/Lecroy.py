import visa
import time
from time import sleep
import sys
from .LecroyTRCReader import *
from .Instrument import Instrument

class LecroyWavepro725zi(Instrument):
    '''
    Class for Lecroy Wavepro 725zi Oscilloscope
    '''

    active_channels = []

    def __init__(self, ip_address):
        '''
        initial a scope object with ethernet connection.
        '''
        self._model = "LECROY"
        self.inst=self._connect(ip_address)
        self.set_timeout(100000000)
        self.inst.write("Comm_ForMaT DEF9,WORD,BIN") #output binary
        
        #self.inst.write("SEQ ON, 5, 40e+12")
    #***************************************************************************
    # Private
    def _connect(self, ip_address,device=0):
        if not ip_address: raise Exception("ERROR: No ip address given for Lecroy Wavepro")
        rm=visa.ResourceManager("@py")
        
        try:
            inst = rm.open_resource("TCPIP%d::%s::inst0::INSTR"%(device,ip_address))
            name = inst.query("*IDN?;")
            if 'LECROY' in name:
                print("Sucessfully connected to %s: %s"%(ip_address,name))
                return inst
            else:
                print("Connected but not to a Lecroy; Probably the wrong device.")
                return None
        except Exception as e:
            print(e)
            print("Failed to connect to TCPIP%d at %s; trying again"%(device,ip_address))
            time.sleep(.01)
            return self._connect(ip_address,device+1)
            

    #===========================================================================
    def _set_screen_display(self, channel, switch):
        self.inst.write("C{}:TRA {}".format(channel, switch))

    #===========================================================================
    def _set_internal_display(self, channel, switch):
        self.inst.write("C{}:DISP {}".format(channel, switch))

    #===========================================================================
    def _set_trigger_mode(self, channel, mode):
        mode_list = ["AUTO", "NORM", "SINGLE", "STOP"]
        if mode in mode_list:
            self.inst.write("TRig_MoDe {};WAIT;".format(mode))
            self.inst.write("TRSE EDGE,SR,{},HT,OFF;WAIT;".format(channel))
        else:
            self.inst.write("TRig_MoDe {};WAIT;".format(mode_list[0]))

    #===========================================================================
    def _set_trigger_slope(self, channel, slope):
        slope_list = ["POS", "NEG", "WINDOW"]
        if slope in slope_list:
            self.inst.write("{}:TRig_SLope {};".format(channel, slope))
        else:
            #take default [0] if slope is not one of the mode in trig_slope
            self.inst.write("{}:TRig_SLope {};".format(channel, slope_list[0]))

    #===========================================================================
    def _set_trigger_level(self, channel, threshold):
        self.inst.write("{}:TRig_LeVel {}V;".format(channel, threshold))


    #***************************************************************************
    # Public

    def close(self):
        self.inst.close()

    #===========================================================================
    def set_channel_display(self, channel, switch):
        self._set_internal_display(channel, switch)
        self._set_screen_display(channel, switch)

    #===========================================================================
    def set_timeout(self, timeout):
        self.inst.timeout=timeout

    #===========================================================================
    def arm_trigger(self, channel_number, threshold, slope="NEG", mode="NORM"):
        '''
        '''
        self._set_trigger_mode(channel_number, mode)
        self._set_trigger_slope(channel_number, slope)
        self._set_trigger_level(channel_number, threshold)

    #===========================================================================
    def create_dir(self, dirc): #dont use it, it is garbage.
        self.inst.write(r"DIR DISK,HDD,ACTION,CREATE,'C:\Users\lecroy\Desktop\{}'".format(dirc))
        self.inst.write(r"DIR DISK,HDD,ACTION,SWITCH,'C:\Users\lecroy\Desktop\{}'".format(dirc))

    def local_store_setup(self,on_off="OFF"):
        self.inst.write("STST ALL_DISPLAYED,HDD,AUTO,on_off,FORMAT,BINARY".format(on_off))

    def save_waveform_local(self):
        self.inst.write("STO ALL_DISPLAYED,FILE")


    #===========================================================================
    def _get_wavefrom_ascii(self, channel):
        looper = 0
        voltage = self.inst.query("C{}:INSPECT? SIMPLE;".format(channel))
        voltage = voltage.split()
        voltage = voltage[2:len(voltage)-2]
        while voltage == []:
            looper += 1
            print("Empty V, retrying {}".format(looper))
            voltage = self.inst.query("C{}:INSPECT? SIMPLE;".format(channel))
            #if voltage == []:
                #print "Empty Event"
                #return [[0],[0]]
            voltage = voltage.split()
            voltage = voltage[2:len(voltage)-2]

        t_offset = self.inst.query("C{}:INSPECT? HORIZ_OFFSET;".format(channel))
        t_offset = t_offset.split()
        while t_offset == "" or t_offset == []:
            looper += 1
            print("Empty offset, retrying {}".format(looper))
            #print t_offset
            t_offset = self.inst.query("C{}:INSPECT? HORIZ_OFFSET;".format(channel))
            t_offset = t_offset.split()
            #if t_offset == "":
                #print "Empty Event"
                #return [[0],[0]]
        t_offset = float(t_offset[3])
        t_bin = self.inst.query("C{}:INSPECT? HORIZ_INTERVAL;".format(channel))
        t_bin = t_bin.split()
        while t_bin == "" or t_bin == []:
            looper += 1
            print("Empty bin, retrying {}".format(looper))
            #print t_offset
            t_bin = self.inst.query("C{}:INSPECT? HORIZ_INTERVAL;".format(channel))
            t_bin = t_bin.split()
            #if t_bin == "":
            #    print "Empty Event"
            #    return [[0],[0]]
        t_bin = float(t_bin[3])
        #print t_bin
        time = []
        for i in range(len(voltage)):
            time.append(t_offset + i*t_bin)
        #print "Good Event"
        return [time, voltage]

    #===========================================================================
    def _get_waveform_ascii_all(self, channel_list):
        '''
        Get waveform using ascii format. Loop through list of channels.
        depreciated method. see _get_waveform_binary_All
        '''
        looper = 0

        waveform_query_string = "WAIT;"
        toffset_query_string = "WAIT;"
        tbin_query_string = "WAIT;"
        for channel in channel_list:
            waveform_query_string += "C{}:INSPECT? SIMPLE;".format(channel)
            toffset_query_string += "C{}:INSPECT? HORIZ_OFFSET;".format(channel)
            tbin_query_string += "C{}:INSPECT? HORIZ_INTERVAL;".format(channel)

        voltage_list = []
        #t1 = time.time()
        voltage = self.inst.query(waveform_query_string)
        #t2 = time.time()
        #print("Query Time: {}".format(t2-t1))
        voltage = voltage.split()
        while voltage == []:
            looper += 1
            print("Empty V, retrying {}".format(looper))
            voltage = self.inst.query(waveform_query_string)
            voltage = voltage.split()


        voltage_size_num_ch_ratio = len(voltage)/len(channel_list)
        for i in range(len(channel_list)):
            #print("voltage = {}".format(len(voltage)))
            voltage_temp = voltage[2:voltage_size_num_ch_ratio-1]
            voltage = voltage[voltage_size_num_ch_ratio:]
            voltage_list.append(voltage_temp)
            #print("voltage_temp = {}".format(len(voltage_temp)))
            #print(voltage_temp)

        t_offset_list = []
        #t1 = time.time()
        t_offset = self.inst.query(toffset_query_string)
        #t2 = time.time()
        #print("Query t offset {}".format(t2-t1))
        t_offset = t_offset.split()
        while t_offset == "" or t_offset == []:
            looper += 1
            print("Empty offset, retrying {}".format(looper))
            t_offset = self.inst.query(toffset_query_string)
            t_offset = t_offset.split()

        for i in range(len(channel_list)):
            t_offset_list.append(float(t_offset[3]))
            t_offset = t_offset[4:]

        t_bin_list = []
        t_bin = self.inst.query(tbin_query_string)
        t_bin = t_bin.split()
        while t_bin == "" or t_bin == []:
            looper += 1
            print("Empty bin, retrying {}".format(looper))
            t_bin = self.inst.query(tbin_query_string)
            t_bin = t_bin.split()

        for i in range(len(channel_list)):
            t_bin_list.append(float(t_bin[3]))
            t_bin = t_bin[4:]
        #print t_bin

        time_list = []
        for ch in range(len(voltage_list)):
            time_v = []
            for i in range(len(voltage_list[ch])):
                time_v.append(t_offset_list[ch] + i*t_bin_list[ch])
            time_list.append(time_v)
            #print(len(time_v))

        #print "Good Event"
        return [time_list, voltage_list]

    #===========================================================================
    def _get_waveform_binary(self, channel, raw=False, seq_mode=False):
        '''
        Get waveform with binary format. Loop through list of channels.
        '''

        voltage_list = []
        time_list = []
        raw_data = []
        segmentCount = ""
        waveCount = ""

        if isinstance(channel, list):
            for ch in channel:
                self.inst.write("C{}:WF?".format(ch))
                binary_stream = self.inst.read_raw()
                if raw:
                    raw_data.append(binary_stream)
                    continue
                voltage_data = trcReader(binary_stream, "WAV_DATA", ch)
                horizontal_offset = trcReader(binary_stream, "HORIZ_OFFSET", ch)
                horizontal_inter = trcReader(binary_stream, "HORIZ_INTERVAL", ch)
                if seq_mode:
                    segmentCount = trcReader(binary_stream, "NOM_SUBARRAY_COUNT", ch, seq_mode)
                    waveCount = trcReader(binary_stream, "WAVE_ARRAY_COUNT", ch, seq_mode)
                trigger_timestamp = []
                time_data = []
                for i in range(len(voltage_data)):
                    t = horizontal_offset + i*horizontal_inter
                    time_data.append(t)
                voltage_list.append(voltage_data)
                time_list.append(time_data)
            if raw:
                return raw_data
            else:
                if seq_mode:
                    return [time_list, voltage_list, segmentCount, waveCount]
                else:
                    return [time_list, voltage_list]
        elif isinstance(channel, int):
            channel_list = []
            channel_list.append(channel)
            return self._get_waveform_binary(channel_list, raw)
        else:
            raise ValueError("Non-supported channel input. Please feed in list of int of single int.")

    #===========================================================================
    def get_waveform(self, channel, mode="binary", seq_mode=False):
        if "binary" in mode and "raw" in mode:
            try:
                return self._get_waveform_binary(channel, raw=True)
            except ValueError as error:
                print(error)
        elif "binary" in mode:
            try:
                return self._get_waveform_binary(channel, False, seq_mode)
            except ValueError as error:
                print(error)
        elif "ascii" in mode:
            if isinstance(channel, list):
                return self._get_wavefrom_ascii_All(channel)
            else:
                return self._get_wavefrom_ascii(channel)
        else:
            raise ValueError("Non-supported mode or channels")

    #===========================================================================

    def wait_for_next_trigger(self, timeout = 0.0, trigger_scan = None):
        #self.inst.write("ARM;")
        #self.inst.write("ARM;")#" WAIT;")
        #self.inst.write("ARM; WAIT;")
        #self.inst.write("ARM;")
        #self.inst.write("WAIT;")
        #self.inst.write("ARM;WAIT;") #this one??
        #self.inst.query("ARM;WAIT;")
        if trigger_scan is None:
            return self.inst.query("ARM;WAIT;*OPC?")#.format(str(timeout))) #or this oone??
        else:
            return self.inst.query("TRMD SINGLE;WAIT {};FRTR;*OPC?".format(timeout))
        #self.inst.write("ARM;*OPC?")


    def _test(self):
        self.inst.write("C2:TRig_LeVel 50V;")
        self.inst.write("C2:TRig_SLope NEG;TRIG:EDGE:SLOP %s")
