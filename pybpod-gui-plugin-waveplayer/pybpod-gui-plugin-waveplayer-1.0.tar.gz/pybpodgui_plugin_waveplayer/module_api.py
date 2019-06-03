from pybpodapi.com.arcom import ArCOM, ArduinoTypes
from pybpodapi.bpod_modules.bpod_module import BpodModule
import struct
import numpy as np
import wave
import time

class WavePlayerModule(object):
    
    COM_HANDSHAKE            = 227
    COM_PLAY_WAVEFORM        = ord('P')
    COM_STOP_PLAYBACK        = ord('X')
    COM_LOAD_WAVEFORM        = ord('L')
    COM_SET_OUTPUT_RANGE     = ord('R')
    COM_SET_SAMPLING_PERIOD  = ord('S')
    COM_SET_LOOP             = ord('O')
    COM_SET_BPOD_EVENTS      = ord('V')
    COM_SET_TRIGGER          = ord('T')
    COM_LOAD_TRIGGER_PROFILE = ord('F')
    COM_GET_PARAMETERS       = ord('N')
    
    CURRENT_FIRMWARE_VERSION = 1

    TRIGGER_MODE_NORMAL = 0
    TRIGGER_MODE_MASTER = 1
    TRIGGER_MODE_TOGGLE = 2

    RANGE_VOLTS = ['0V:5V', '0V:10V', '0V:12V', '-5V:5V', '-10V:10V', '-12V:12V']
    RANGE_VOLTS_0_5  = 0
    RANGE_VOLTS_0_10 = 1
    RANGE_VOLTS_0_12 = 2
    RANGE_VOLTS_MINUS5_5   = 3
    RANGE_VOLTS_MINUS10_10 = 4
    RANGE_VOLTS_MINUS12_12 = 5


    def __init__(self, serial_port = None):

        self.is_open = False

        if serial_port:
            self.open(serial_port)



    def open(self, serialport):

        self.arcom = ArCOM().open(serialport,115200)

        self.arcom.write_array( ArduinoTypes.get_uint8_array([self.COM_HANDSHAKE]) )

        ack = self.arcom.read_uint8()
        if ack!=228:
            raise Exception('Could not connect =( ')
        
        version = self.arcom.read_uint32()
        if version < self.CURRENT_FIRMWARE_VERSION:
            raise Exception("""Error: old firmware detected - v{0}.
                The current version is: {1}.
                Please update the I2C messenger firmware using Arduino.""".format(
                version, self.CURRENT_FIRMWARE_VERSION
            ))
        self.firmware_version = version
        
        self.get_parameters()
        self.is_open = True

        return True


    def disconnect(self):
        if hasattr(self,'arcom'):
            self.arcom.close()
            del self.arcom
        self.is_open = False


    def play(self, channels, wave_index):
        self.arcom.write_array(ArduinoTypes.get_uint8_array([self.COM_PLAY_WAVEFORM, channels, wave_index]))


    def stop(self):
        self.arcom.write_array(ArduinoTypes.get_uint8_array([self.COM_STOP_PLAYBACK]))


    def load_waveform(self, wave_index, wavform):
        
        data2send  = ArduinoTypes.get_uint8_array([self.COM_LOAD_WAVEFORM, wave_index])
        data2send += ArduinoTypes.get_uint32_array([len(wavform)])

        wavform = np.array(wavform)

        if self.output_range==0:
            positive_only = 1.0
            voltage_width = 5.0
        elif self.output_range==1:
            positive_only = 1.0
            voltage_width = 10.0
        elif self.output_range==2:
            positive_only = 1.0
            voltage_width = 12.0
        elif self.output_range==3:
            positive_only = 0.0
            voltage_width = 10.0
        elif self.output_range==4:
            positive_only = 0.0
            voltage_width = 20.0
        elif self.output_range==5:
            positive_only = 0.0
            voltage_width = 24.0 
        else:
            positive_only = 0.0
            voltage_width = 10.0
        
        min_wave  = min(wavform);
        max_wave  = max(wavform);
        max_range = voltage_width+(positive_only*0.5);
        min_range = ( (voltage_width/2.0) * -1.0 ) * ( 1.0 - positive_only )

        if (min_wave < min_range) or (max_wave > max_range):
            raise Exception("""Error setting waveform: All voltages must be within the current range: {0}.""".format(
                self.RANGE_VOLTS[self.output_range]
            ))
        
        offset = (voltage_width/2.0)*(1.0-positive_only)
        wavbits = np.ceil(((wavform+offset)/voltage_width)*( (2.0**16.0) -1.0));

        data2send += ArduinoTypes.get_uint16_array(wavbits)

        self.arcom.write_array(data2send)
        
        ack = self.arcom.read_uint8()
        return ack==1


    def set_output_range(self, value):
        self.arcom.write_array(ArduinoTypes.get_uint8_array( [self.COM_SET_OUTPUT_RANGE, value] ))
        ack = self.arcom.read_uint8()
        return ack==1

    def set_sampling_period(self, value):

        if value < 1 or value > 200000:
            raise Exception('Error setting sampling rate: valid rates are in range: [1;200000] Hz')
            
        sampling_period_microseconds = (1.0/value)*1000000.0

        data2send  = ArduinoTypes.get_uint8_array([self.COM_SET_SAMPLING_PERIOD])
        data2send += ArduinoTypes.get_float(sampling_period_microseconds)
        
        self.arcom.write_array(data2send)
       

    def set_loop_duration(self, loop_duration):

        if len(self.loop_mode)!=self.n_channels:
            raise Exception('Wrong loop modes')

        if len(loop_duration)!=self.n_channels:
            raise Exception('Wrong loop durations')

        bytes2send =  ArduinoTypes.get_uint8_array([self.COM_SET_LOOP] + self.loop_mode)
        bytes2send += ArduinoTypes.get_uint32_array(np.array(loop_duration))

        self.arcom.write_array(bytes2send)

        ack = self.arcom.read_uint8()
        if ack==1: self._loop_duration = loop_duration
        return ack==1



    def set_loop_mode(self, loop_mode):

        if len(loop_mode)!=self.n_channels:
            raise Exception('Wrong loop modes')

        if len(self.loop_duration)!=self.n_channels:
            raise Exception('Wrong loop durations')

        for i, mode in enumerate(loop_mode):
            if mode and self.loop_duration[i]==0:
                raise Exception('Error: before enabling loop mode, each enabled channel must have a valid loop duration.')

        bytes2send =  ArduinoTypes.get_uint8_array([self.COM_SET_LOOP] + loop_mode)
        bytes2send += ArduinoTypes.get_uint32_array(self.loop_duration)

        self.arcom.write_array(bytes2send)

        ack = self.arcom.read_uint8()
        if ack==1: self._loop_mode = loop_mode
        return ack==1


    def set_bpod_events(self, values):
        bytes2send = ArduinoTypes.get_uint8_array(
            [self.COM_SET_BPOD_EVENTS] + values
        )
        self.arcom.write_array(bytes2send)
        ack = self.arcom.read_uint8()

        if ack==1:
            self._bpod_events = values
        return ack==1
        
    def set_trigger_mode(self, value):
        self.arcom.write_array(
            ArduinoTypes.get_uint8_array([self.COM_SET_TRIGGER, value])
        )
        ack = self.arcom.read_uint8()
        
        if ack==1:
            self._trigger_mode = value
        return ack==1
        

    def set_trigger_profiles(self, trigger_profiles):

        length, width = trigger_profiles.shape

        if length!=self.n_trigger_profiles or width!=self.n_channels:
            raise Exception(
                'Error setting trigger profiles: matrix of trigger profiles must be {0} profiles X {1} channels.'.format(
                self.n_trigger_profiles, self.n_channels
            ))

        """ TODO
        if sum(sum((profileMatrix > 0)') > obj.maxSimultaneousChannels) > 0
                error(['Error setting trigger profiles: the current sampling rate only allows ' num2str(obj.maxSimultaneousChannels) ' channels to be triggered simultaneously. Your profile matrix contains at least 1 profile with too many channels.']);
            end
        """
        profile_matrix_out = trigger_profiles
        profile_matrix_out[profile_matrix_out==0] = 256
        
        self.arcom.write_array(
            ArduinoTypes.get_uint8_array([self.COM_LOAD_TRIGGER_PROFILE, profile_matrix_out-1])
        )
        ack = self.arcom.read_uint8()
        
        if ack==1:
            self._trigger_profiles = trigger_profiles
        return ack==1
         
            



    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    
    @property
    def trigger_mode(self):
        return self._trigger_mode
    
    @property
    def bpod_events(self):
        return self._bpod_events
    
    @property
    def loop_mode(self):
        return self._loop_mode
    
    @property
    def loop_duration(self):
        return self._loop_duration
        
    @property
    def trigger_profile_enable(self):
        return self._trigger_profile_enable
    
    @property
    def trigger_profiles(self):
        return self._trigger_profiles
    
    @property
    def output_range(self):
        return self._output_range
    
    @property
    def sampling_rate(self):
        return self._sampling_rate

    @property
    def max_waves(self):
        return self._max_waves
    
    @property
    def n_channels(self):
        return self._n_channels

    @property
    def n_trigger_profiles(self):
        return self._n_trigger_profiles
    

    ######################################################################
    ### PRIVATE FUNCTIONS ################################################
    ######################################################################

    def get_parameters(self):
        self.arcom.write_array([self.COM_GET_PARAMETERS])
        # number of output channels
        self._n_channels             = self.arcom.read_uint8()
        # maximum number of waveforms supported
        self._max_waves              = self.arcom.read_uint16()
        # current trigger mode
        self._trigger_mode           = self.arcom.read_uint8()
        # 0 = standard trigger mode, 1 = trigger profile mode
        self._trigger_profile_enable = self.arcom.read_uint8()==1
        # maximum number of trigger profiles supported
        self._n_trigger_profiles     = self.arcom.read_uint8()
        # index of the currently selected range 
        self._output_range           = self.arcom.read_uint8()
        # sampling period (in microseconds)
        sampling_period_microseconds = self.arcom.read_float32()
        # 0 = off, 1 = bpod event reporting
        self._bpod_events   = [v==1 for v in self.arcom.read_uint8_array(self.n_channels)]
        
        # 0 = off, 1 = on
        self._loop_mode     = [v==1 for v in self.arcom.read_uint8_array(self.n_channels)]

        self._sampling_rate = round((1/sampling_period_microseconds)*1000000)

        # duration of loop playback in samples
        self._loop_duration = np.array(self.arcom.read_uint32_array(self.n_channels))*self.sampling_rate
        
        #self.is_playing       = [False for i in range(self.n_channels)]
        self._trigger_profiles = np.zeros( (self.n_trigger_profiles, self.n_channels) )
        



    def _print_parameters(self):
        print('Number of channels:',self.n_channels)
        print('Max waves:',self.max_waves)
        print('Trigger mode:',self.trigger_mode)
        print('Trigger profile enabled:',self.trigger_profile_enable)
        print('Number of trigger profiles:',self.n_trigger_profiles)
        print('Output range:',self.output_range)
        print('Bpod events:',self.bpod_events)
        print('Loop mode',self.loop_mode)
        print('Sampling rates:',self.sampling_rate)
        print('Loop durations:',self.loop_duration)


    def debug(self):
        self.get_parameters()
        self._print_parameters()