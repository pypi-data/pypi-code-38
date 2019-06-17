from collections import defaultdict
from re import sub, match

from copy import deepcopy
from numpy import int8, int16, int32, uint8, uint16, uint32, uint64
from can_headers import drive_hardware_type, parameter_dictionary, trace_variables


def hex_string_to_bytes(input_string):
    """
    Take an input string of arbitrary length (assuming the first two characters
     are a full byte, i,e,, 22222 and 222202 produce the same result, to a
     reversed list of bytes, i.e., "221c0" -> [1, 28, 34]
    :param input_string:
    :return: list
    """
    out_bytes = []
    for i in range(0, len(input_string), 2):
        out_bytes.append(int(input_string[i:i+2], 16))
    return out_bytes


def bytes_to_string(input_bytes):
    if isinstance(input_bytes, int):
        raise ValueError("input_bytes not list or array: ", input_bytes)
    return "".join([chr(i) for i in input_bytes if i != 0])


def int_to_bit_list(input_int):
    if input_int is None:
        return [0 for i in range(16)]
    input_int = uint16(input_int)
    status_formatted = [int(i) for i in "{0:016b}".format(input_int)]
    status_formatted.reverse()
    return status_formatted


def int_to_hexes(input_int, width=None):
    if width == 4:
        input_int = uint32(input_int)
    _hex = hex(input_int)[2:].replace("L", "")
    if len(_hex) % 2 != 0:
        _hex = "0"+_hex
    out_hex = []
    for i in range(0, len(_hex), 2):
        out_hex.insert(0, int(_hex[i:i+2], 16))
    if width is not None:
        for i in range(len(out_hex), width, 1):
            out_hex.append(0)
    return out_hex


def test_int_to_hexes():
    data1 = int_to_hexes(30000, width=4)
    assert 0x75 == data1[1]
    assert 0x30 == data1[0]
    data2 = int_to_hexes(40863, width=4)
    assert 0x9F == data2[0]
    assert 0x9F == data2[1]
    data3 = int_to_hexes(257, width=4)
    assert 0x01 == data3[0]
    assert 0x01 == data3[1]


def int48(input_int):
    return input_int


def lookup_trace_variable_address(input_name):
    return int(trace_variables[input_name]["address"])



def lookup_trace_variable_units(input_name):
    try:
        return float(trace_variables[input_name]["units"].split(" ")[0])
    except Exception as e:
        return 1.0


def lookup_trace_variable_unit_name(input_name):
    try:
        return unit_getter(trace_variables[input_name]["units"].split(" "))
    except Exception as e:
        return "Unknown"


def unit_getter(parts):
    return parts[0] if len(parts) == 1 else " ".join(parts[1:])


def get_trace_variables():
    return trace_variables.keys()


def lookup_hardware_type(input_int):
    address = "%0.4X" % input_int
    if address in drive_hardware_type:
        return str(drive_hardware_type[address]["name"])
    else:
        return "unknown_hardware"


def read_in_data(_data):
    if not isinstance(_data, list):
        return _data
    _out_data = []
    for i in range(0, len(_data)-1, 4):
        _data_point = 0
        for byte_i in range(4):
            _data_point += _data[i+byte_i] << 8*byte_i
        _out_data.append(_data_point)
    return _out_data


def properties_from_cfg():
    maps = {"INT8": int8, "INT16": int16, "INT32": int32, "INT32*": int32,
            "String": bytes_to_string,
            "STRING": bytes_to_string, "U8": uint8, "U16": uint16,
            "U32": uint32, "U64": uint64, "HARDWARE_TYPE": lookup_hardware_type,
            "OCTET": read_in_data}

    width_dict = {"INT8": 1, "INT16": 2, "INT32": 4, "INT32*": 4, "String": 40,
                  "STRING": 40, "HARDWARE_TYPE": 4, "OCTET": 40,
                  "U8": 1, "U16": 2, "U32": 4, "U64": 8}

    out_dictionary = {}
    for section in parameter_dictionary.keys():
        _parameter_name = parameter_dictionary[section]["parametername"]
        _type = parameter_dictionary[section]["datatype"]
        out_dictionary[_parameter_name] = {}
        _add_bytes = hex_string_to_bytes(section)
        if len(_add_bytes) == 2:
            _add_bytes.append(0)

        out_dictionary[_parameter_name]["index"] = _add_bytes
        out_dictionary[_parameter_name]["width"] = width_dict[_type]
        out_dictionary[_parameter_name]["type"] = maps[_type]
        try:
            _units = parameter_dictionary[section]["units"].split(" ")
            out_dictionary[_parameter_name]["units"] = unit_getter(_units)
            try:
                out_dictionary[_parameter_name]["scale"] = float(_units[0])
            except:
                out_dictionary[_parameter_name]["scale"] = 1.0
        except:
            out_dictionary[_parameter_name]["units"] = "Unknown"
        try:
            _map_pdo = parameter_dictionary[section]["map_pdo"]
            out_dictionary[_parameter_name]["pdo"] = _map_pdo
        except:
            out_dictionary[_parameter_name]["pdo"] = True
        try:
            _plotable = parameter_dictionary[section]["plotable"]
            out_dictionary[_parameter_name]["plot"] = _plotable
        except:
            out_dictionary[_parameter_name]["plot"] = False
    return out_dictionary


PROPERTIES = properties_from_cfg()


def address_list_to_string(address_list):
    return "".join(['{:02d}'.format(address_list[i]) if i < len(address_list) - 1
                    else '{:01d}'.format(address_list[i])
                    for i in range(len(address_list))])


def generate_index_map(properties):
    """
    Generate a dict mapping addresses to property names. This is used to map
     incoming data back to properties from SDO's.
    :param properties: dict of dicts
    :return: dict mapping addresses to property names
    """
    out_dict = {}
    for _property in properties.keys():
        address = properties[_property]['index']
        out_dict[address_list_to_string(address)] = _property
    return out_dict


def convert_numpy_points(data_points):
    out_dict = defaultdict(list)
    # removes numpy datatypes from data
    for i in range(len(data_points)):
        for key in data_points[i].keys():
            # purely for typing reduction
            dp = data_points[i][key]
            out_dict[key].append(dp if type(dp) == str or type(
                dp) == bool else float(dp))
    return out_dict


HEXRE = "[0-9A-Fa-fxX\s\,\[\]]+"
NODE_ID = "[0-9A-Fa-f]+"
FRAME_MAP = {"SYNC": {"id": 0x80},
             "DOWNLOAD": {"expression": "DOWNLOAD"},
             "WAIT FOR TRACE": {"expression": "WAIT FOR TRACE"}}


def string_to_address_list(in_string):
    if in_string.find(",") > 0:
        return [int(i) for i in in_string.split(",")]
    return [int(in_string[i:i + 2]) for i in range(0, len(in_string), 2)]


def parse_hex(input):
    """
    Parse an input string into an array of bytes.
    :param input: a string of the form 0xFFFFFF or 255,255,255, or a list
    :return: a list of ints between 0 and 255
    """

    output_parts = []
    if not input and input != 0:
        return output_parts
    if type(input) == list:
        parts = input
    else:
        input = str(input).replace("[", "").replace("]", "")
        parts = input.split(",")

    for part in parts:
        part = str(part)
        if part == '':
            continue
        part = part.strip()
        try:
            hex_match = match("0(x|X)([A-Fa-f0-9])+", part)
            parts = ["0"+i if len(i) == 1 else i for i in part.split(" 0x")]
            part = "".join(parts)
        except TypeError:
            raise ValueError(str(part) + " part is of type: " + str(type(part)))
        if hex_match > 0:
            hex_part = part[2:]
            # chop the string into pairs
            current_pos = len(output_parts)
            if len(hex_part) % 2 != 0:
                hex_part = "0" + hex_part
            hex_index = len(hex_part)
            while hex_index - 2 >= -1:
                lower_index = hex_index - 2 if hex_index - 2 >= 0 else 0
                output_parts.insert(current_pos,
                                    int(hex_part[lower_index:hex_index], 16))
                hex_index -= 2
        else:
            if part:
                part = int(part)
            else:
                continue
            if not 0 <= part < 256:
                hex_part = hex(part)[2:]
                current_pos = len(output_parts)
                if len(hex_part) % 2 != 0:
                    hex_part = "0"+hex_part
                hex_index = len(hex_part)
                while hex_index - 2 >= -1:
                    lower_index = hex_index - 2 if hex_index - 2 >= 0 else 0
                    output_parts.insert(current_pos,
                                        int(hex_part[lower_index:hex_index], 16))
                    hex_index -= 2
                continue
            output_parts.append(part)
    return output_parts


INDEX_MAP = generate_index_map(PROPERTIES)


def lookup_address(address):
    # reverse look up the address
    i_map = INDEX_MAP.items()
    keys = [key for key, value in i_map if value == address]
    if len(keys) > 0:
        return string_to_address_list(keys[0])


def gen_command_code(data_length):
    hex1 = 0x33 - 4 * data_length
    return 0x21 if hex1 < 0 else hex1


def gen_sdo_write(id, data, index):
    data_length = len(data)
    frame_data = index
    frames = []

    if data_length <= 4:
        command_code = gen_command_code(data_length)
        frame_data += data
        frame = {"id": id, "data": [command_code]+frame_data}
        frames.append(frame)
    else:
        # initiate a download
        command_code = 0b00100001
        frame_data += [data_length]
        frame_data = [frame_data[j] if j < len(frame_data) else 0
                      for j in range(7)]
        frame = {"id": id, "data": [command_code]+frame_data}

        frames.append(frame)
        bytes_left = data_length
        seqno = 0
        while bytes_left > 0:
            if seqno == 1:
                command_code = 0b00010000
            else:
                command_code = 0b00000000
            if bytes_left < 7:
                n = 7 - bytes_left
                command_code += (n << 1) + 1
            frame_data = data[data_length - bytes_left:min(
                data_length + 7 - bytes_left,
                len(data))]
            frame = {"id": id,"data": [command_code]+frame_data}
            # self.write(str(frame))
            frames.append(frame)
            seqno = (seqno + 1) % 2

            bytes_left -= 7
    return frames


def check_address(address):
    if not isinstance(address, list):
        raise Exception("address " + str(address) + " is not a list!")
    elif len(address) < 3:
        while len(address) < 3:
            address.append(0)
    return address


def interpret_expression(_frame):
    if "expression" in _frame:
        _frame["expression"] = sub(" can [\d]+", "", _frame["expression"])
    write_match = match(
        r"^WRITE (" + HEXRE + ") to (" + HEXRE + "|[\w]+) on node (" + NODE_ID + ")$",
        _frame["expression"])
    query_match = match(r"QUERY (" + HEXRE + "|[\w]+) on node (" + NODE_ID + ")$",
                        _frame["expression"])
    nmt_match = match(r"(SET [CDEMNOPRST ]+) on node (" + NODE_ID + ")$",
                      _frame["expression"])
    comment_match = match("^\#", _frame["expression"])
    hex_match = match("^" + HEXRE + "$", _frame["expression"])

    if _frame["expression"] in FRAME_MAP:
        return deepcopy(FRAME_MAP[_frame["expression"]])
    elif comment_match:
        return None
    elif write_match:
        data = parse_hex(write_match.group(1).strip())
        address = write_match.group(2).strip()
        if match(r"^" + HEXRE + "$", address):
            address = parse_hex(address)
        else:
            address = lookup_address(address)
        address = check_address(address)
        node = int(write_match.group(3))
        return gen_sdo_write(0x600 + node, data, [address[1], address[0], address[2]])
    elif query_match:
        address = query_match.group(1).strip()
        if match(r"^" + HEXRE + "$", address):
            address = parse_hex(address)
        else:
            address = lookup_address(address)
        address = check_address(address)
        node = int(query_match.group(2).strip())
        frame_data = [0x40, address[1], address[0], address[2]]
        return {"id": 0x600 + node, "data": frame_data}
    elif hex_match:
        parts = parse_hex(_frame["expression"])
        return {"id": parts[0:2], "data": parts[2:]}
    elif nmt_match:
        _frame = deepcopy(FRAME_MAP[nmt_match.group(1)])
        _frame["data"] += [int(nmt_match.group(2))]
        return _frame