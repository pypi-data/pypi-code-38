import struct
from binascii import unhexlify
from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from iotile.core.utilities.typedargs.annotate import param, annotated, return_type, context
from iotile.core.utilities.typedargs import type_system
from iotile.core.exceptions import *
from iotile.core.utilities.command_file import CommandFile


@context("ConfigDatabase")
class ConfigDatabasePlugin (TileBusProxyPlugin):
    """A Python interface to the configuration manager in an IOTile controller

    The ConfigDatabase can be used to set configuration variables that are sent
    to all of the tiles in the IOTile device when they power on.
    """

    @return_type("integer")
    def count_variables(self):
        """Count the total number of variables defined in the config manager

        The count returned does not distinguish between old invalid entries and current
        entries, so not all of these entries are necessarily in use but all are stored
        in the controller's memory.

        """
        count, = self.rpc(0x2a, 0x0b, result_format="L")
        return count

    @annotated
    def clear_variables(self):
        """Clear all config variables stored in the controller

        """
        err, = self.rpc(0x2a, 0x0c, result_format="L")
        if err != 0:
            raise HardwareError("Could not get clear config variables", error_code=err)

    @return_type("basic_dict")
    def memory_limits(self):
        """Query information on memory usage and limits in the config database.

        This returns the total number of entries and data as well as the maximum
        limits and now much could be saved by compacting the config database.
        """

        max_data, data_size, invalid_data, entry_count, invalid_count, max_entries = self.rpc(0x2a, 0x10, result_format="LHHHHH2x")
        return {
            'data_usage': data_size,
            'data_compactable': invalid_data,
            'data_limit': max_data,
            'entry_usage': entry_count,
            'entry_compactable': invalid_count,
            'entry_limit': max_entries
        }

    @annotated
    def compact_database(self):
        err, = self.rpc(0x2a, 0x0f, result_format="L", timeout=5.0)
        if err:
            raise HardwareError("Unable to compact config database", error_code=err)

    @param("index", "integer", desc="Index of variable to retrieve information about")
    def invalidate_variable(self, index):
        """Invalidate a currently stored config variable.

        Invalidating a variable causes it to no longer be streamed to any tiles and 
        is equivalent to deleting it.  Since the config database is an append-only
        log, invalidating a variable is the only way to delete a variable without 
        either compacting the database or clearing all variables.
        """

        err, = self.rpc(0x2a, 0x0e, index, result_format="L")
        if err != 0:
            raise HardwareError("Could not invalidate config variable", error_code=err, index=index)

    @return_type("basic_dict")
    @param("index", "integer", desc="Index of variable to retrieve information about")
    def get_variable(self, index):
        """Get a stored configuration variable from the controller."""

        meta = self.get_metadata(index)
        name = self.get_identifier(index)
        value = self.get_data(index)

        var = {
            'metadata': meta,
            'name': name,
            'data': value
        }

        return var

    def get_metadata(self, index):
        """Get the metadata for a stored config variable from the controller by its index
        """

        err, entry = self.rpc(0x2a, 0x0a, index, result_format="L16s")

        if err != 0:
            raise HardwareError("Could not get config variable information", error_code=err)

        return type_system.convert_from_binary(bytearray(entry), 'fw_configvariable')

    def get_identifier(self, index):
        """Get the 16 bit id for the variable by its index
        """

        data = self.get_data(index, include_id=True)

        name, = struct.unpack("<H", data[:2])
        return name

    def get_data(self, index, include_id=False):
        """
        Get the contents of the config variable given its index
        """

        info = self.get_metadata(index)

        var_data = bytearray()

        for i in range(0, info.data_length, 16):
            res = self.rpc(0x2a, 0x0d, index, i, result_type=(0, True))
            err, = struct.unpack_from("<L", res['buffer'])
            if err != 0:
                raise HardwareError("Could not get data for variable", error_code=err, index=index)

            data = res['buffer'][4:]
            var_data += data

        if not include_id:
            var_data = var_data[2:]

        return var_data 

    def _start_entry(self, id, target):
        args = struct.pack("<H8s", id, target.raw_data)
        err, = self.rpc(0x2a, 0x07, args, result_format="L")
        if err != 0:
            raise HardwareError("Could not start a new config variable", error_code=err)

    def _finish_entry(self):
        err, = self.rpc(0x2a, 0x09, result_format="L")
        if err != 0:
            raise HardwareError("Could not start a new config variable", error_code=err)

    def _push_data(self, data):
        for i in range(0, len(data), 20):
            length = 20
            if len(data) - i < length:
                length = len(data) - i

            err, = self.rpc(0x2a, 0x08, data[i:20+i], result_format="L")
            if err != 0:
                raise HardwareError("Could not send config variable data", error_code=err, data_offset=i, data_length=length)

    def _convert_to_bytes(self, type, value):
        """Convert a typed string to a binary array
        """

        int_types = {'uint8_t': 'B', 'int8_t': 'b', 'uint16_t': 'H', 'int16_t': 'h', 'uint32_t': 'L', 'int32_t': 'l'}

        type = type.lower()
        
        is_array = False
        if type[-2:] == '[]':
            if(value[0]!='[' or value[-1]!=']'):
                raise ValidationError("Array value improperly formated, must be a stringified list")
            is_array = True
            type = type[:-2]

        if type not in int_types and type not in ['string', 'binary']:
            raise ValidationError('Type must be a known integer type, integer type array, string', known_integers=int_types.keys(), actual_type=type)

        if type == 'string':
            #value should be passed as a string
            bytevalue = bytearray(value)
        elif type == 'binary':
            if not value.startswith('hex:'):
                raise ValidationError("Binary value type must be hex encoded with the prefix hex:", value=value)

            value = value[4:]
            bytevalue = unhexlify(value)
        elif is_array:
            value = [int(n,0) for n in value[1:-1].split(',')]
            bytevalue = struct.pack("<%s" % (int_types[type]*len(value)), *value)
        else:
            value = int(value, 0)
            bytevalue = struct.pack("<%s" % int_types[type], value)

        return bytevalue

    @param("target", "fw_tileselector", desc="A tile selector describing which tile this variable goes to")
    @param("id", "integer", desc="The 16 bit id of the config variable")
    @param("type", "string", desc="The type of this variable, (u)int8_t, (u)int16_t, (u)int32_t, binary, or string. Add [] at end for array")
    @param("value", "string", desc="The value of the config variable")  
    def set_variable(self, target, id, type, value):
        """Set a config variable on the target tile

        This RPC loads the selected data into the controller tile and tags it to be sent
        to the tile indicated by the tile selector target.
        """

        bindata = self._convert_to_bytes(type, value)

        self._start_entry(id, target)
        self._push_data(bindata)
        self._finish_entry()


    @param("inpath", "path", "readable", desc="The input file to load config variables from")
    def load_from_file(self, inpath):
        """Load config variables into config database from an ascii file.

        This file may be generated using the iotile-sgcompile program that is
        part of the iotile-sensorgraph python distribution.
        """

        cmdfile = CommandFile.FromFile(inpath)

        if cmdfile.filetype != 'Config Variables':
            raise DataError("Unknown file type", found=cmdfile.filetype, expected='Config Variables')

        if cmdfile.version != '1.0':
            raise DataError("Unknown file version", found=cmdfile.version, expected="1.0")

        for cmd in cmdfile.commands:
            if cmd.name == 'set_variable':
                self.set_variable(*cmd.args)
            else:
                raise DataError("Unknown command", name=cmd.name)
