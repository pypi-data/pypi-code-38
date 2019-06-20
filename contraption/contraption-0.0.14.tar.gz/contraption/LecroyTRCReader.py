import struct
from array import array
import sys

OFF_SET = 21
LECROY_WAVEFORM_TEMPLATE ={
"DESCRIPTOR_NAME":["2s", 0, 16],
"TEMPLATE_NAME":["2s", 16, 32],
"COMM_TYPE":["H", 32, 34],
"COMM_ORDER":["H", 34, 36],
"WAVE_DESCRIPTOR":["l", 36, 40],
"USER_TEXT":["l", 40, 44],
"RES_DESC1":["l", 44, 48],
"TRIGTIME_ARRAY":["l", 48, 52],
"RIS_TIME_ARRAY":["l", 52, 56],
"RES_ARRAY1":["l", 56, 60],
"WAVE_ARRAY_1":["l", 60 ,64],
"WAVE_ARRAY_2":["l", 64, 68],
"RES_ARRAY2":["l", 68, 72],
"RES_ARRAY3":["l", 72, 76],
"INSTRUMENT_NAME":["16s", 76, 92],
"INSTRUMENT_NUMBER":["l", 92, 96],
"TRACE_LABEL":["16s", 96, 112],
"RESERVED1":["h", 112, 114],
"RESERVED2":["h", 114, 116],
"WAVE_ARRAY_COUNT":["l", 116, 120],
"PNTS_PER_SCREEN":["l", 120, 124],
"FIRST_VALID_PNT":["l", 124, 128],
"LAST_VALID_PNT":["l", 128, 132],
"FIRST_POINT":["l",132,136],
"SPARSING_FACTOR":["l", 136, 140],
"SEGMENT_INDEX":["l", 140, 144],
"SUBARRAY_COUNT":["l", 144, 148],
"SWEEP_PER_ACQ":["l", 148, 152],
"POINTS_PER_PAIR":["h", 152, 154],
"PAIR_OFFSET":["h", 154, 156],
"VERTICAL_GAIN":["f", 156, 160],
"VERTICAL_OFFSET":["f", 160, 164],
"MAX_VALUE":["f", 164, 168],
"MIN_VALUE":["f", 168, 172],
"NOMINAL_BITS":["H", 172, 174],
"NOM_SUBARRAY_COUNT":["H", 174, 176],
"HORIZ_INTERVAL":["f", 176, 180],
"HORIZ_OFFSET":["d", 180, 188],
"PIXEL_OFFSET":["d", 188, 196],
"VERTUNIT":["48s", 196, 244],
"HORUNIT":["48s", 244, 292],
"HORIZ_UNCERTAINTY":["f", 292, 296],
"TRIGGER_TIME_SEC":["d", 296, 304],
"TRIGGER_TIME_MIN":["B", 304, 305],
"TRIGGER_TIME_HOU":["B", 305, 306],
"TRIGGER_TIME_DAY":["B", 306, 307],
"TRIGGER_TIME_MON":["B", 307, 308],
"TRIGGER_TIME_YEA":["H", 308, 310],
"TRIGGER_TIME_UNUSED":["H", 310, 312],
"ACQ_DURATION":["f", 312, 316],
"RECORD_TYPE":["H", 316, 318],
"PROCESSING_DONE":["H", 318, 320],
"RESERVED5":["H", 320, 322],
"RIS_SWEEPS":["H", 322, 324],
"TIMEBASE":["H", 324, 326],
"VERT_COUPLING":["H", 326, 328],
"PROBE_ATT":["f", 328, 332],
"FIXED_VERT_GAIN":["H", 332, 334],
"BANDWIDTH_LIMIT":["H", 334, 336],
"VERTICAL_VERNIER":["f",336, 340],
"ACQ_VERT_OFFSET":["f", 340, 344],
"WAVE_SOURCE":["H", 344, 346]
}


VERBOSE = False

def Print(content, verbose=False):
    if not verbose:
        return 0
    elif verbose == True:
        print(content)
    else:
        print("Debug... "),
        print(content)


def LoadTRCFile(fileName):
    with open(fileName, mode="rb") as f:
        return f.read()

def Endianess( check_endianess, default="<" ):
    if check_endianess == 0:
        return ">"
    elif check_endianess == 1:
        return "<"
    else:
        if default != "":
            return default
        else:
            sys.exit("Cannot find bit order!")

def Decode_Bytes(data_bytes, format, TRCfile_mode=False):
    unpacked_data = ""
    try:
        unpacked_data = struct.unpack( format, data_bytes)
    except:
        if TRCfile_mode:
            unpacked_data = data_bytes
        else:
            unpacked_data = struct.unpack( format, str(data_bytes))
    if type(unpacked_data) == tuple:
        unpacked_data = unpacked_data[0]
        try:
            if "\x00" in unpacked_data:
                unpacked_data = unpacked_data.split("\x00")[0]
        except:
            pass
    else:
        pass
    return unpacked_data

def trcReader( binary_waveform, sub_data, CH=2, sequence=None, TRCfile_mode=False):#, bytes_fmt ):
    #print(binary_waveform)
    OFF_SET = ""
    if OFF_SET == "":
        offset_bytes = binary_waveform[:50]
        offset_ss = struct.unpack( "50s", offset_bytes)
        if type(offset_ss) == tuple:
            offset_ss = offset_ss[0]
        OFF_SET = offset_ss.find("WAVEDESC")
        CH_prefix_index = offset_ss.find("C{}:WF ALL,".format(CH))
        Print(CH_prefix_index)
        if CH_prefix_index != 0:
            OFF_SET += CH_prefix_index
        Print(OFF_SET)

    endianess = ""
    endi_bytes = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["COMM_ORDER"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["COMM_ORDER"][2]]
    Print(endi_bytes)
    #fmt = endi+LECROY_WAVEFORM_TEMPLATE[sub_data][0]
    endi_ss = struct.unpack( "H", endi_bytes)
    if type(endi_ss) == tuple:
        endianess = endi_ss[0]
    Print(endianess)
    endianess = Endianess(endianess)

    if sub_data == "WAV_DATA":
        if sequence == None:
            #WAVEDESC_INDEX = trcReader(binary_waveform, "WAVE_DESCRIPTOR", CH, sequence, TRCfile_mode )
            #USER_TEXT_INDEX = trcReader(binary_waveform, "USER_TEXT", CH, sequence, TRCfile_mode )
            wave_count_bytes = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_ARRAY_COUNT"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_ARRAY_COUNT"][2]]
            wave_count = struct.unpack(endianess+"l", wave_count_bytes)
            wave_count = wave_count[0]
            Print("voltage_bit:{}".format(wave_count))

            vertical_offset_bytes =  binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][2]]
            vertical_offset = struct.unpack( endianess+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][0], vertical_offset_bytes)
            vertical_offset = vertical_offset[0]
            Print("vertical_offset:{}".format(vertical_offset))
            vertical_gain_bytes =  binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][2]]
            vertical_gain = struct.unpack( endianess+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][0], vertical_gain_bytes)
            vertical_gain = float(vertical_gain[0])
            Print("vertical_gain:{}".format(vertical_gain))
            wave_data_stream = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]:]
            wave_data  = []
            for i in range(wave_count):
                voltage_bit = wave_data_stream[i*2:i*2+2]
                voltage_bit = struct.unpack(endianess+"h", voltage_bit)
                voltage_bit = voltage_bit[0]
                Print("voltage_bit:{}".format(voltage_bit))
                wave_data.append( (voltage_bit)*1.0*vertical_gain-vertical_offset )
            return wave_data
        else:
            wave_count_bytes = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_ARRAY_COUNT"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_ARRAY_COUNT"][2]]
            wave_count = struct.unpack(endianess+"l", wave_count_bytes)
            wave_count = wave_count[0]

            segment_count_bytes = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["NOM_SUBARRAY_COUNT"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["NOM_SUBARRAY_COUNT"][2]]
            segment_count = struct.unpack(endianess+"H", segment_count_bytes)
            segment_count = segment_count[0]
            Print("wave_cout:{}".format(wave_count))
            Print("wave_cout:{}".format(int(wave_count/segment_count)))
            wave_count = int(wave_count/segment_count)

            vertical_offset_bytes =  binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][2]]
            vertical_offset = struct.unpack( endianess+LECROY_WAVEFORM_TEMPLATE["VERTICAL_OFFSET"][0], vertical_offset_bytes)
            vertical_offset = vertical_offset[0]
            #print("vertical_offset:{}".format(vertical_offset))
            vertical_gain_bytes =  binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][2]]
            vertical_gain = struct.unpack( endianess+LECROY_WAVEFORM_TEMPLATE["VERTICAL_GAIN"][0], vertical_gain_bytes)
            vertical_gain = float(vertical_gain[0])
            #print("vertical_gain:{}".format(vertical_gain))
            USER_TEXT_bytes = int(trcReader( binary_waveform, "USER_TEXT", CH))
            TRIGTIME_ARRAY_bytes = int(trcReader( binary_waveform, "TRIGTIME_ARRAY", CH))
            trigger_time_array = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes:OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes+TRIGTIME_ARRAY_bytes]
            Print(len(trigger_time_array))
            Print(len(trigger_time_array)/struct.calcsize("d"))
            #raw_input()
            for i in range(len(trigger_time_array)/struct.calcsize("d")):
                d = struct.unpack(endianess+"d", trigger_time_array[0+i*8:8*i+8])
                if i%2==0:print(d)
            raw_input()

            RIS_TIME_ARRAY_bytes = int(trcReader( binary_waveform, "RIS_TIME_ARRAY", CH))
            print(RIS_TIME_ARRAY_bytes)
            raw_input()
            #wave_low_bytes = OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes+TRIGTIME_ARRAY_bytes
            wave_low_bytes = OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes+TRIGTIME_ARRAY_bytes+RIS_TIME_ARRAY_bytes
            wave_data_stream = binary_waveform[wave_low_bytes:]
            wave_data  = []
            COMM_TYPE =trcReader( binary_waveform, "COMM_TYPE", CH)
            wave_data_type = ""
            wave_data_byte_size = ""
            if COMM_TYPE == 0:
                wave_data_type = "b"
                wave_data_byte_size = 1
            else:
                wave_data_type = "h"
                wave_data_byte_size = 2
            print(COMM_TYPE)
            raw_input()
            for k in range(segment_count*2):
                if (k+1)%2!=0:
                    for i in range(wave_count):
                        voltage_bit = wave_data_stream[i*wave_data_byte_size+k*wave_count:i*wave_data_byte_size+wave_data_byte_size+k*wave_count]
                        voltage_bit = struct.unpack(endianess+wave_data_type, voltage_bit)
                        voltage_bit = voltage_bit[0]
                        #print(voltage_bit)
                        #print("voltage_bit:{}".format(voltage_bit))
                        wave_data.append( (voltage_bit)*1.0*vertical_gain- vertical_offset )

                #print("here good")
                #print(wave_data)
            return wave_data


    if sub_data == "Trig_Time":
        trigger_timestamp = []
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_SEC", CH, sequence, TRCfile_mode) )
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_MIN", CH, sequence, TRCfile_mode) )
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_HOU", CH, sequence, TRCfile_mode) )
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_DAY", CH, sequence, TRCfile_mode) )
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_MON", CH, sequence, TRCfile_mode) )
        trigger_timestamp.append( trcReader( binary_waveform, "TRIGGER_TIME_YEA", CH, sequence, TRCfile_mode) )
        return trigger_timestamp

    if sub_data == "Trigger_Tdiff" and sequence!=None:
        WAVEDESC_INDEX = int(trcReader( binary_waveform, "WAVE_DESCRIPTOR", CH, sequence, TRCfile_mode))
        USER_TEXT_bytes = int(trcReader( binary_waveform, "USER_TEXT", CH))
        TRIGTIME_ARRAY_bytes = int(trcReader( binary_waveform, "TRIGTIME_ARRAY", CH))

        trigger_Tdiff_data = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes:OFF_SET+LECROY_WAVEFORM_TEMPLATE["WAVE_SOURCE"][2]+USER_TEXT_bytes+TRIGTIME_ARRAY_bytes]
        d_byteSize = struct.calcsize("d")
        numEvent = len(trigger_Tdiff_data)/d_byteSize
        Print(numEvent)
        trigger_Tdiff = []
        for i in range(numEvent):
            d = struct.unpack(endianess+"d", trigger_Tdiff_data[0+i*d_byteSize:8+i*d_byteSize])
            if i%2==0:
                trigger_Tdiff.append(d)
        return trigger_Tdiff


    #base case
    data_bytes = binary_waveform[OFF_SET+LECROY_WAVEFORM_TEMPLATE[sub_data][1]:OFF_SET+LECROY_WAVEFORM_TEMPLATE[sub_data][2]]
    data_fmt = endianess+LECROY_WAVEFORM_TEMPLATE[sub_data][0]
    return Decode_Bytes(data_bytes, data_fmt, TRCfile_mode)
