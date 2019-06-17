import sys
from time import time, sleep
from configparser import ConfigParser
from CANcard import CanCard, CanFrame
from can_helpers import address_list_to_string, generate_index_map, \
    int_to_bit_list, int_to_hexes, lookup_trace_variable_address, \
    lookup_trace_variable_units, PROPERTIES, convert_numpy_points, lookup_trace_variable_unit_name
from can_headers import registers
from collections import defaultdict

from copy import deepcopy
from numpy import reshape, average
from ctypes import c_int
from gradientone import gateway_helpers
from device_drivers.can.can_helpers import bytes_to_string

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')


INDEX_MAP = generate_index_map(PROPERTIES)
TRACE_SCALE = 10

ERROR_REGISTER = ["Generic error", "Current error", "Voltage error",
                  "Temperature error", "Communication error",
                  "Device specific error", "Reserved for future use",
                  "Manufacturer error"]
CANOPEN_ERRORS = {0: 'error Reset or No Error', 4096: 'Generic Error',
                  12832: 'Internal voltage too low',
                  36864: 'External Error', 9008: 'Load dump at outputs',
                  8192: 'Current', 13088: 'Output voltage too low',
                  33280: 'Protocol Error', 33024: 'Communication',
                  8448: 'Current, device input side', 33088: 'recovered from bus off',
                  12544: 'Mains Voltage', 8704: 'Current inside the device',
                  25088: 'User Software', 16640: 'Ambient Temperature',
                  33344: 'Unexpected SYNC data length',
                  8960: 'Current, device output side', 25344: 'Data Set',
                  24832: 'Internal Software', 33056: 'CAN in Error Passive Mode',
                  33296: 'PDO not processed due to length error',
                  13056: 'Output Voltage', 8992: 'Short circuit at outputs',
                  33312: 'PDO length exceeded', 12800: 'Voltage inside the device',
                  12288: 'Voltage', 12560: 'Input voltage too high',
                  16384: 'Temperature', 33072: 'Life Guard Error or Heartbeat Error',
                  20480: 'Device Hardware',
                  33328: 'DAM MPDO not processed, destination object not available',
                  12816: 'Internal voltage too high', 24576: 'Device Software',
                  33360: 'RPDO timeout', 12576: 'Input voltage too low',
                  28672: 'Additional Modules', 16896: 'Device Temperature',
                  13072: 'Output voltage too high', 32768: 'Monitoring'}
COPLEY_ERRORS = ["Output short circuit", "Amplifier over temperature",
                 "Amplifier over voltage", "Amplifier under voltage",
                 "Motor over temperature input active",
                 "Encoder power error (indicates the 5V encoder supply over current)",
                 "Motor phasing error", "Output current limited",
                 "Output voltage limited", "Positive limit switch",
                 "Negative limit switch", "Tracking error",
                 "Position input wrapped around +/- 2^31 bits",
                 "Amplifier internal hardware error (contact Copley Controls customer "
                 "support)", "Node guarding error"]


class MotorException(Exception):
    pass


class Motor(CanCard):
    def __init__(self, fname=None):
        super(Motor, self).__init__(fname=fname)
        # Copley has 8 PDOs. More pieces of data could be delivered if
        # multiple values are assigned to a PDO, but only 8 are used for now.
        self._properties = [None, None, None, None, None, None, None, None]
        self._trace_properties = []
        self._last_assigned = -1
        self._last_values = {}
        self.unplugged = False
        self.trace_reference_period = None
        self.logs = []
        self.emcy_msgs = []
        self.verbose = True
        self.address_map = INDEX_MAP
        self.node = 1
        self.current_flags = defaultdict(list)
        self.current_flag_timestamp = None
        self.flag_timestamps = []
        self.monitor_registers = []
        self.start_time = time()
        self.nmt_states = {}
        self.trace_target_reached = False
        self.trace_timeout = 10.0

    @property
    def operation(self):
        return True

    @operation.setter
    def operation(self, state):
        data = [0x01 if state else 0x80] + [self.node]
        # ID of master node
        preop = CanFrame(id=0x000, data=data)
        self.xmit(preop)

    @property
    def moving(self):
        return int_to_bit_list(self.property_getter('status_word'))[14]

    @property
    def velocity_units(self):
        if self.property_getter("motor_back_emf_constant_deprecated") == 0.0:
            return "counts/sec"
        else:
            return "RPM"

    def read_all_flags(self):
        flags = defaultdict(dict)
        for key in self.nmt_states:
            self.node = key
            for register in registers:
                self.status(register=register)
                flags[key][register] = deepcopy(self.current_flags[register])
        return flags

    def status(self, register="status_word", skip_format=False, use_sdo=True, setup_pdo=False):
        status_formatted = int_to_bit_list(self.property_getter(register, use_sdo=use_sdo, setup_pdo=setup_pdo))
        timestamp = self.current_flag_timestamp - self.start_time
        for i in range(len(status_formatted)):
            if i >= len(registers[register]):
                continue
            status_flag = registers[register][i]

            if status_formatted[i]:
                if status_flag not in self.current_flags[register]:
                    self.current_flags[register].append(status_flag)
                    self.flag_timestamps.append([timestamp, status_flag, True])
            else:
                if status_flag in self.current_flags[register]:
                    del self.current_flags[register][self.current_flags[register].index(status_flag)]
                    self.flag_timestamps.append([timestamp, status_flag, False])
        if skip_format:
            return ""
        return ", ".join(self.current_flags[register])

    def read_registers(self):
        for monitor_register in self.monitor_registers:
            self.status(monitor_register, skip_format=True)

    def log(self, msg):
        if self.verbose:
            gateway_helpers.logger.info(msg)
        self.logs.append(msg)

    def route_incoming_frame(self, in_frame):
        # if you got an incoming PDO, try again
        if 0x80 <= in_frame.id < 0x100:
            self.handle_emcy(in_frame)
        elif 0x100 <= in_frame.id < 0x500:
            self.handle_pdo(in_frame)
        elif 0x580 <= in_frame.id < 0x600:
            if in_frame.data[0] < 0x81:
                self.handle_sdo(in_frame)
        elif in_frame.id > 0x700:
            self.num_heartbeats[in_frame.id - 0x700] += 1
            self.handle_heartbeat(in_frame)
        else:
            print("got unknown frame: ", str(in_frame))

    def acknowledge(self):
        if self.unplugged:
            return
        #self.sync()
        self.num_heartbeats = defaultdict(int)
        _ack = self.recv(timeout=self.timeout)
        while _ack is not None:
            if len(_ack.data) == 0:
                _ack = self.recv(timeout=self.timeout)
                continue
            self.route_incoming_frame(_ack)
            # if we have received at least two heartbeats from any one node, exit
            if len([n for n in self.num_heartbeats if self.num_heartbeats[n] > 3]) > 0:
                return
            _ack = self.recv(timeout=self.timeout)

    def get_nmt_states(self):
        # run through all the possible node states and get the responses
        # to find what node to use
        current_nodes = deepcopy(self.node)
        for i in range(0, 16):
            self.node = i
            self.send_sdo(address='canopen_heartbeat_time', data=[0x01, 0x0],
                      acknowledge=True)
            self.acknowledge()
            self.send_sdo(address='canopen_heartbeat_time', data=[0x00, 0x0],
                          acknowledge=True)
        # change the current node based on the new values
        if len(self.nmt_states.keys()) > 0:
            self.node = self.nmt_states.keys()[0]

    def clear_pdos(self):
        for i in range(8):
            if self.unplugged:
                return
            self.send_sdo(address=[0x1a, i, 0x00], data=[0x00])
            if self.unplugged:
                return
            self.send_sdo(address=[0x18, i, 0x01],
                          data=[0x81, i + 1, 0x00, 0x80])
        self._properties = [None, None, None, None, None, None, None, None]

    def handle_heartbeat(self, in_frame):
        NMT_STATES = {0x00: "Boot up (Initialising)", 0x04: "Stopped",
                      0x05: "Operational",
                      0x7f: "Pre-operational"}
        self.nmt_states[int(in_frame.id-0x700)] = NMT_STATES[in_frame.data[0]]

    def handle_pdo(self, in_frame):
        id_index = in_frame.id - 0x181

        if id_index >= len(self._properties):
            return

        property_name = self._properties[id_index]
        if property_name is None:
            return
        in_data = in_frame.data
        if property_name in registers:
            self.current_flag_timestamp = in_frame.time
        self.set_value(in_data, property_name)
        if property_name in self.monitor_registers:
            self.status(property_name, use_sdo=False, setup_pdo=False)

    def set_value(self, in_data, property_name):
        if 'scale' in PROPERTIES[property_name].keys():
            _scale = PROPERTIES[property_name]['scale']
        else:
            _scale = 1

        _data_type = PROPERTIES[property_name]['type']
        if _data_type == bytes_to_string:
            output = in_data
        elif len(in_data) < 5:
            output = 0
            for byte_num in range(len(in_data)):
                output += in_data[byte_num] << 8 * byte_num
        else:
            output = in_data
        try:
            value = _data_type(output) * _scale
        except OverflowError:
            # certain versions of numpy can't interpreted unsigned ints
            # correctly. If that happens, default to using ctypes
            value = c_int(output).value * _scale
        self._last_values["_" + property_name] = value

    def handle_sdo(self, in_frame):
        """
        Get data from an incoming SDO, and store it in .
        :param data: the data part of the incoming CAN frame
        :return: nothing
        """
        # chop and invert bits 4:1
        # width (bytes) of the frame calculated in the next line
        width = float(0x4F - in_frame.data[0]) / 4 + 1
        if len(in_frame.data) < 4:
            return
        if in_frame.data[0] == 0x20 or in_frame.data[0] == 0x30:
            return
        elif in_frame.data[0] > 0x10:
            _addr = [in_frame.data[2], in_frame.data[1], in_frame.data[3]]
            index = address_list_to_string(_addr)
            property_name = INDEX_MAP[index]
        else:
            property_name = "trace_data"

        def send_toggle(in_frame, width, out_data):
            toggle_byte = 0x70 if in_frame.data[0] == 0x00 else 0x60
            self.send_sdo(command_code=toggle_byte, address=[0, 0, 0],
                          data=[], acknowledge=False)
            in_frame = self.recv(timeout=self.timeout)

            # To get the next frame to see what to send out
            # frames will be coming in from different processes
            # keep waiting/checking if you don't get the frames you expect
            while not (0x580 <= in_frame.id < 0x600 and in_frame.data[0] < 0x40):
                if in_frame.data[0] == 0x80:
                    return in_frame, 0, False, out_data
                self.route_incoming_frame(in_frame)
                in_frame = self.recv(timeout=self.timeout)
                if in_frame is None:
                    raise ValueError("Response frame not received within timeout. Check your CAN device.")
                    return None, None, False, None
            num_bytes = (((in_frame.data[0] & 0x0e) >> 1) ^ 0xFF) & 0x07

            out_data += in_frame.data[1:num_bytes+1]
            width -= num_bytes
            if num_bytes < 7:
                collecting = False
            else:
                collecting = True
            return in_frame, width, collecting, out_data

        if width > 4:
            # get the length of the data from the SDO
            width = in_frame.data[4]
            out_data = []
            in_frame, width, collecting, out_data = send_toggle(in_frame, width, out_data)
            while collecting:
                in_frame, width, collecting, out_data = send_toggle(in_frame, width, out_data)

        else:
            out_data = in_frame.data[4:]

        if property_name in registers:
            self.current_flag_timestamp = in_frame.time

        self.set_value(out_data, property_name)

    def handle_emcy(self, in_frame):
        """Handle emergency messages

        Can have multiple messages from one frame
        """
        canopen_addr = in_frame.data[0] * 256 + in_frame.data[1]
        msg = "Emergency code, "
        if canopen_addr in CANOPEN_ERRORS:
            msg += "canopen error is: " + CANOPEN_ERRORS[canopen_addr] + ", "
        error_register = []
        for i in range(8):
            if ((in_frame.data[2] >> i) % 2) == 1:
                error_register.append(ERROR_REGISTER[i])
        if len(error_register) > 0:
            msg += "error register values: " + ", ".join(error_register) + ", "
        copley_errors = []
        copley_addr = in_frame.data[4] * 256 + in_frame.data[5]
        for i in range(16):
            if ((copley_addr >> i) % 2) == 1:
                copley_errors.append(COPLEY_ERRORS[i])
        if len(copley_errors) > 0:
            msg += "copley register values: " + ", ".join(copley_errors) + ", "
        self.emcy_msgs.append((in_frame.time, msg))

    def move(self, steps=0, relative=False):
        # Set to profile position mode.  (Move to a target position).
        self.send_sdo(address='mode_of_operation', data=[0x01])
        # Set target position to steps
        self.send_sdo(address='trajectory_generator_position_command',
                      data=int_to_hexes(steps, width=4))
        # Set control word bit 4 to 1 (move)
        start = 0x2f + relative*0x40
        end = 0x3f + relative*0x40
        self.send_sdo(address='control_word', data=[start, 0x00])
        # Set control word bit 4 to 0 (done with move commands)
        self.send_sdo(address='control_word', data=[end, 0x00])

    def send_sdo(self, address, data, acknowledge=True, command_code=None, append=True):
        # check for human readable string to lookup address
        if isinstance(address, str):
            # look up the address in the Properties
            address = PROPERTIES[address]['index']
        if command_code is None:
            hex1 = 0x33-4*len(data)
            command_code = 0x21 if hex1 < 0 else hex1
        while len(data) < 4:
            data.append(0)
        data = [command_code]+[address[1]]+[address[0]]+[address[2]]+data
        self.frame = CanFrame(id=0x600+self.node, data=data)
        self.xmit(self.frame, append=append)
        if acknowledge:
            self.acknowledge()

    def property_getter(self, property_name='current', use_sdo=True, setup_pdo=True):
        if property_name not in PROPERTIES:
            raise KeyError(str(property_name)+" not in PROPERTIES: "+str(
                PROPERTIES.keys()))
        if PROPERTIES[property_name]['pdo'] and not use_sdo:
            # Setup a pdo if it doesn't exist
            if property_name not in self._properties and setup_pdo:
                self.operation = False
                async = True if property_name == 'status_word' else False
                self.setup_pdo(property_name, async=async)
                self.operation = True
                self.acknowledge()
        else:
            # else send sdo querying the device directly
            self.send_sdo(command_code=0x40, data=[],
                          address=PROPERTIES[property_name]['index'],
                          acknowledge=True)

        try:
            return self._last_values["_" + property_name]
        except Exception as e:
            # occasionally timeouts can occur here
            gateway_helpers.logger.warning(property_name+ " not in last_values: "+ str(self._last_values.keys()))
            return None

    def setup_pdo(self, property_name='current', async=False):
        if property_name in self._properties:
            index = self._properties.index(property_name)
        else:
            self._last_assigned += 1
            if self._last_assigned == len(self._properties):
                self._last_assigned = 0
            index = self._last_assigned
        value = PROPERTIES[property_name]['index']
        bit_width = PROPERTIES[property_name]['width'] * 8

        # Set Number of Mapped objects to zero
        self.send_sdo(address=[0x1A, index, 0x00], data=[0x00])

        # Turn off the TPD last_assigned
        self.send_sdo(address=[0x18, index, 0x01], data=[0x81 + index, 0x01, 0x00, 0x80])
        # set transmission to every sync (if async is false, else set to async)
        self.send_sdo(address=[0x18, index, 0x02], data=[0xff if async else 0x01])
        # map PDO
        self.send_sdo(address=[0x1A, index, 0x01],
                      data=[bit_width] + [value[2], value[1], value[0]])
        # Turn on the TPDO
        self.send_sdo(address=[0x18, index, 0x01], data=[0x81 + index, 1, 0, 0])
        # Set Number of total Mapped objects to one
        self._properties[index] = property_name
        self.send_sdo(address=[0x1A, index, 0x00], data=[0x01])

    def setup_trace(self, trace_delay=0.0, trace_period=110, trigger_config=0):
        """
        Setup the CAN Bus to read data in as a trace (instead of as a pdo)
        """
        # first, clear all trace channels
        for chan in range(6):
            chan_name = "trace_channel_"+str(chan+1)
            self.send_sdo(address=PROPERTIES[chan_name]['index'],
                          data=[0, 0])

        for property_index in range(len(self._trace_properties)):
            chan_name = "trace_channel_"+str(property_index+1)
            address_hexes = int_to_hexes(lookup_trace_variable_address(
                                         self._trace_properties[property_index]),
                                         width=2)
            self.send_sdo(address=PROPERTIES[chan_name]['index'],
                          data=address_hexes)
        if self.trace_reference_period is None:
            self.trace_reference_period = self.property_getter("trace_reference_period")
        # set the trace_delay
        delay_units = int(trace_delay/self.trace_reference_period)
        self.send_sdo(address=PROPERTIES["trace_delay"]["index"],
                      data=int_to_hexes(delay_units, width=2))
        # set the trace time
        self.send_sdo(address=PROPERTIES["trace_period"]["index"],
                      data=int_to_hexes(trace_period, width=2)[0:2])
        # set the trigger type
        # TODO: break this into components
        trigger_config = int_to_hexes(trigger_config, width=6)
        self.send_sdo(address=PROPERTIES["trace_trigger_configuration"]["index"],
                      data=trigger_config)
        self.start_trace(software_trace=True)

    def sync(self):
        sf = CanFrame(id=0x80, data=[])
        self.xmit(sf)

    def do_trace(self, destination, trace_period=110,
                 properties=['actual_load_position', 'actual_motor_velocity'],
                 relative=False, trace_timeout=10.0):
        self.trace_timeout = trace_timeout
        if self.property_getter("motor_encoder_type_deprecated", use_sdo=True) == 1 and \
                        self.property_getter("motor_back_emf_constant_deprecated", use_sdo=True) == 0.0:
            self.send_sdo(address=PROPERTIES["motor_back_emf_constant_deprecated"]["index"],
                          data = int_to_hexes(8.3, width=4)[0:2])
        elif self.property_getter("motor_encoder_type_deprecated", use_sdo=True) != 1 and \
                        self.property_getter("motor_back_emf_constant_deprecated", use_sdo=True) != 0.0:
            self.send_sdo(
                address=PROPERTIES["motor_back_emf_constant_deprecated"]["index"],
                data=int_to_hexes(0, width=4)[0:2])
        # set up registers
        if "status_word" not in self.monitor_registers:
            self.monitor_registers.append("status_word")
        for register in self.monitor_registers:
            # map the status word
            self.setup_pdo(property_name=register, async=True)

        self.operation = True
        self.flag_timestamps = []

        self._trace_properties = properties
        self.setup_trace(trace_period=trace_period)
        self.move(destination, relative=relative)
        # wait for the motor to start moving
        while self.moving and destination > 500:
            sleep(0.001)
        _ = self.wait_for_trace()
        trace_period = self.property_getter("trace_period", use_sdo=True)
        data_array = None
        while time()-self.start_time < self.trace_timeout:
            try:
                data_array = self.property_getter("trace_data", use_sdo=True)
                samples = self.property_getter("trace_sample_count", use_sdo=True)
                data_array = reshape(data_array, (samples, len(self._trace_properties)))

                break
            except Exception as e:
                samples = self.property_getter("trace_sample_count", use_sdo=True)
                #gateway_helpers.logger.info("trace data not available, trying again")
                sleep(0.01)
        #print("samples are: ", samples)
        if data_array is None:
            gateway_helpers.logger.error("Trace data was not available within timeout.")
            return
        data = []
        for row_index in range(len(data_array)):
            _point = {'measure_time': TRACE_SCALE*row_index*trace_period*self.trace_reference_period}
            for col_index in range(len(self._trace_properties)):
                to_int = c_int(data_array[row_index][col_index]).value
                input_name = self._trace_properties[col_index]
                units = lookup_trace_variable_units(input_name)
                _point[self._trace_properties[col_index]] = to_int*units
            data.append(_point)
        # format the data in the channel list format
        sample_rate = self.trace_reference_period*TRACE_SCALE/trace_period
        data = self.make_units(data, sample_rate)
        return data

    def start_trace(self, software_trace=True):
        samples = self.property_getter("trace_sample_count", use_sdo=True)
        if samples:
            return
        if software_trace:
            self.send_sdo(address=PROPERTIES["trace_trigger"]["index"],
                          data=[0, 1])
            self.start_time = self.frames_list[-1].time
            self.current_flag_timestamp = self.frames_list[-1].time

    def wait_for_trace(self, max_counts=-1, software_trace=True):
        #self.start_trace(software_trace=software_trace)
        # the trace won't complete before the maximum time has elapsed, so wait in order
        # to minimize the sdos required to query the samples.
        if max_counts == -1:
            max_counts = sys.maxint
        self.acknowledge()

        samples = self.property_getter("trace_sample_count", use_sdo=True)

        while self.status("status_word").find("Target Reached") == -1 and time()-self.start_time < self.trace_timeout:
            pass
            #sleep(0.1)
            #samples = self.property_getter("trace_sample_count", use_sdo=True)
        if software_trace:
            self.send_sdo(address=PROPERTIES["trace_trigger"]["index"],
                          data=[0, 0])

        self.trace_target_reached = self.status("status_word").find("Target Reached") != -1
        return samples

    def make_units(self, data_points, sample_rate):
        channels = []
        data_dict = convert_numpy_points(data_points)
        assert isinstance(data_dict, dict)
        if "measure_time" in data_dict:
            time_step = average(
                [data_dict["measure_time"][i + 1] - data_dict["measure_time"][i] for i in
                 range(len(data_dict["measure_time"]) - 1)])
        else:
            time_step = 1.0 / sample_rate
        for key in data_dict:
            if key == "measure_time":
                continue
            channel = {"y_values": data_dict[key], "name": key, "time_step": time_step}

            if key == "actual_motor_velocity" or key == "actual_motor_loop_velocity":
                channel["units"] = self.velocity_units
                if channel["units"] == "RPM":
                    channel["y_values"] = [x*0.01 for x in channel["y_values"]]
                else:
                    channel["y_values"] = [x * 0.1 for x in channel["y_values"]]
            elif key in PROPERTIES:
                channel["units"] = PROPERTIES[key]["units"]
            else:
                channel["units"] = lookup_trace_variable_unit_name(key)
            channels.append(channel)
        return channels

    def send_lss(self):
        self.frame = CanFrame(id=0x7e5, data=[0x04, 0x01])
        self.xmit(self.frame)
        self.acknowledge()
        self.frame = CanFrame(id=0x7e5, data=[0x5e])
        self.xmit(self.frame)
        self.acknowledge()


def get_hardware_info(card):
    card.clear_pdos()
    output = {}
    parts =['motor_manufacturer', 'motor_model', 'model_number',
            'model_number', 'drive_name', 'firmware_version_number',
            'drive_hardware_type']
    for part in parts:
        _result = card.property_getter(part)
        if _result is not None:
            output[part] = int(_result) if type(_result) is not str and type(_result) is not bool else _result
    return output


if __name__ == "__main__":

    # instantiate the motor controller
    card = Motor()
    card.open()
    #card.node = 4
    card.get_nmt_states()

    card.monitor_registers = ['status_word', 'control_word']

    destination = 100
    num_moves = 100
    print("This script will attempt up to 100 relative moves of increasing destination distance. Timeout is set to 1 minute.")
    for i in range(num_moves):
        print("test move %s of %s to %d" % (i, num_moves, destination))
        #card.send_sdo(address='latching_fault_status_register',
        #              data=[0xFF, 0xFF, 0xFF, 0xFF])
        start = time()
        data = card.do_trace(destination, relative=True)
        end = time()
        '''
        chan = [d for d in data if d['name'] == 'actual_load_position'][0]['y_values']
        velocities = [d for d in data if d['name'] == 'actual_motor_velocity'][0]['y_values']

        distance = max(chan)-min(chan)
        #print(card.flag_timestamps)
        moving_flags = [d[0] for d in card.flag_timestamps if d[1] == "Moving"]
        target_reached = [d[0] for d in card.flag_timestamps if d[1] == "Target Reached"]
        if len(target_reached) == 0:
            target_reached = [0]
        '''
        #print(card.read_all_flags())
        destination *= 1.1