import ivi
import collections



def grl_script():
    c = 0
    while c <= 20:
        print 'count = ', c
        tek = ivi.tektronix.tektronixMDO3012("USB::0x0699::0x0408::INSTR")
        #tek._write("*CLS")
        tek._interface.timeout = 1000
        tek.ce_dict = collections.defaultdict(int)
        tek.channel_index = {
            'ch1': 0,
            'ch2': 1,
            'ch3': 2,
            'ch4': 3,
        }
        tek.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'record_length': '',
        }
        config_excerpt = {}
        tek.channel_list = ['ch1', 'ch2']
        tek.enabled_list = []
        for ch in tek.channel_list:
            ch_dict = collections.defaultdict(str)
            print "requesting channel enabled data for %s" % ch
            ch_dict['channel_enabled'] = tek.channels[tek.channel_index[ch]].enabled
            if ch_dict['channel_enabled']:
                print "response %s enabled" % ch
                ch_dict['channel_offset'] = tek.channels[tek.channel_index[ch]].offset
                ch_dict['channel_range'] = tek.channels[tek.channel_index[ch]].range
                ch_dict['channel_coupling'] = tek.channels[tek.channel_index[ch]].coupling
                cii = tek.channels[tek.channel_index[ch]].input_impedance
                ch_dict['channel_input_impedance'] = cii
                tek.enabled_list.append(ch)
            else:
                print "response: %s NOT enabled" % ch
            config_excerpt[ch] = ch_dict

        print ("getting trigger")
        trigger_dict = {
            'type': '',
            'coupling': '',
            'source': '',
            'level': '',
        }
        for name in trigger_dict:
            trigger_dict[name] = getattr(tek.trigger, name)
        tek.ce_dict['trigger_edge_slope'] = tek.trigger.edge.slope



        print ("getting acquisition")
        for key in tek.acq_dict:
            tek.acq_dict[key] = getattr(tek.acquisition, key)



        print ("getting outputs")
        outputs = None
        index = 0
        try:
            outputs = tek.outputs[index]
        except Exception:
            print ("getting outputs exception")
        output_dict = {
            'impedance': '',
            'enabled': '',
        }
        if not outputs:
            return output_dict

        for key in output_dict:
            output_dict[key] = getattr(outputs, key)
            print ("output from instr: %s %s" % (key, output_dict[key]))
        print ("set standard_waveform")
        standard_waveform = tek.outputs[index].standard_waveform
        if not standard_waveform:
            print ("no standard_waveform to set")
            print ("outputs[0] dir: %s" % dir(tek.outputs[0]))
            output_dict['standard_waveform'] = False

        #for key in waveform_dict:
       #    tek._setinstr(standard_waveform, key, waveform_dict[key],
        #        label='standard_waveform_')
        output_dict['standard_waveform'] = True


        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = tek.timebase.position
        except Exception:
            print ("get timebase position exception")
        tek._write("SELECT:CH1 ON")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("SELECT:CH2 ON")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:MODE AUTO")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQUIRE:STOPAFTER RUNSTOP")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        print tek._ask("*OPC?")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQUIRE:STATE 1")
        print tek._ask("*OPC?")
        tek._write("AUTOSet EXECute")
        print tek._ask("*OPC?")
        tek._write("ACQuire:MODE HiRes")
        print tek._ask("*ESR?")
        print tek._ask("ALLEv?")
        tek._write("SELECT:CH1 ON")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("SELECT:CH2 ON")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQuire:MODE HiRes")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("HORizontal:POSition 10")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:SCALE 0.3")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:POSition 0")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:OFFSET 0.9")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:SCALE 2")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:POSition 0")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:OFFSET 7.4")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQuire:MODE HIRes")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:MODE NORMAL")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:EDGE:SOURCE CH2")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:EDGE:SLOPE RISE")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:LEVEL:CH2 2.5")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:SCALE 0.16")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:POSition 0")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH1:OFFSET 0.56")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQuire:MODE HiRes")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("HORizontal:POSition 10")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:SCALE 3")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:POSition 0")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("CH2:OFFSET 11.1")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:MODE NORMAL")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:EDGE:SOURCE CH1")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:EDGE:SLOPE EITHER")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("TRIGGER:A:LEVEL:CH1 0.6")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("DISPLAY:PERSISTENCE CLEAR")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQUIRE:STOPAFTER SEQUENCE")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        tek._write("ACQUIRE:STATE 1")
        print tek._ask("*ESR?")
        print tek._ask("allev?")
        wave1 = tek.channels[0].measurement.fetch_waveform()
        #print tek._ask("*OPC?")
        print 'length = ', len(wave1.x)

        raw_setup = tek.system.fetch_setup()
        tek.channel_list = ['ch1', 'ch2']
        tek.enabled_list = []
        for ch in tek.channel_list:
            ch_dict = collections.defaultdict(str)
            print "requesting channel enabled data for %s" % ch
            ch_dict['channel_enabled'] = tek.channels[tek.channel_index[ch]].enabled
            if ch_dict['channel_enabled']:
                print "response %s enabled" % ch
                ch_dict['channel_offset'] = tek.channels[tek.channel_index[ch]].offset
                ch_dict['channel_range'] = tek.channels[tek.channel_index[ch]].range
                ch_dict['channel_coupling'] = tek.channels[tek.channel_index[ch]].coupling
                cii = tek.channels[tek.channel_index[ch]].input_impedance
                ch_dict['channel_input_impedance'] = cii
                tek.enabled_list.append(ch)
            else:
                print "response: %s NOT enabled" % ch
            config_excerpt[ch] = ch_dict
        tek.close()
        c += 1

if __name__ == "__main__":
    grl_script()