class Contract:
    def __init__(self, name, src, functions, variables,
            bin_runtime, pc_to_op_idx_runtime, srcmap_runtime,
            bin_init, pc_to_op_idx_init, srcmap_init,
            source_list, sources, source_offsets, version):
        self.name = name
        self.src = src
        self.functions = functions
        self.variables = variables
        self.bin_runtime = bin_runtime
        self.pc_to_op_idx_runtime = pc_to_op_idx_runtime
        self.srcmap_runtime = srcmap_runtime
        self.bin_init = bin_init
        self.pc_to_op_idx_init = pc_to_op_idx_init
        self.srcmap_init = srcmap_init
        self.source_list = source_list
        self.sources = sources
        self.source_offsets = source_offsets
        self._variables_by_name = {}
        self.version = version

    @property
    def variables_by_name(self):
        if not self._variables_by_name:
            for var in self.variables:
                self._variables_by_name[var.name] = var
        return self._variables_by_name

class SrcMap:
    def __init__(self, start, length, file_idx, jump):
        self.start = start
        self.length = length
        self.file_idx = file_idx
        self.jump = jump

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Breakpoint:
    def __init__(self, src, line):
        self.src = src
        self.line = line

class Function:
    def __init__(self, name, src, params, local_vars, return_vars):
        self.name = name
        self.src = src
        self.params = params
        self.local_vars = local_vars
        self.return_vars = return_vars
        self._params_by_name = {}
        self._local_vars_by_name = {}
        self._return_vars_by_name = {}

    @property
    def params_by_name(self):
        if not self._params_by_name:
            for var in self.params:
                self._params_by_name[var.name] = var
        return self._params_by_name

    @property
    def local_vars_by_name(self):
        if not self._local_vars_by_name:
            for var in self.local_vars:
                self._local_vars_by_name[var.name] = var
        return self._local_vars_by_name

    @property
    def return_vars_by_name(self):
        if not self._return_vars_by_name:
            for var in self.return_vars:
                self._return_vars_by_name[var.name] = var
        return self._return_vars_by_name

class Block:
    def __init__(self):
        self.local_vars = []

class Variable:
    def __init__(self, var_type, name=None, location=None, offset=None, location_type=None):
        self.name = name
        self.var_type = var_type
        self.location = location
        self.offset = offset
        self.location_type = location_type

class Int:
    def __init__(self, size):
        self.size = size

class Uint:
    def __init__(self, size):
        self.size = size

class FixedBytes:
    def __init__(self, size):
        self.size = size

class Bool:
    @property
    def size(self):
        return 8

class Address:
    @property
    def size(self):
        return 160

class Bytes:
    @property
    def size(self):
        return 256

class String:
    @property
    def size(self):
        return 256

class FixedArray:
    def __init__(self, element_type, length, size = None):
        self.element_type = element_type
        self.length = length
        self.size = size

class Struct:
    def __init__(self, name, variables, size = None):
        self.name = name
        self.variables = variables
        self.size = size

class Array:
    def __init__(self, element_type):
        self.element_type = element_type

    @property
    def size(self):
        return 256

class Map:
    def __init__(self, key_type, value_type):
        self.key_type = key_type
        self.value_type = value_type

    @property
    def size(self):
        return 256

class ContractCall:
    def __init__(self, address, contract, is_init):
        self.address = address
        self.contract = contract
        self.is_init = is_init
