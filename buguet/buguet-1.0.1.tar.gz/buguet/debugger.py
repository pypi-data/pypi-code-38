from web3 import Web3
import readline
import sha3
import re
from buguet.models import *
from buguet.contract_data_loader import *
from os import path
from buguet.tracer import Tracer
from buguet.parser import *
import json
import copy
import os
from buguet.util import *

class EvalFailed(Exception):
    pass

class VarNotYetInitialized(Exception):
    pass

class EvalResultTooLarge(Exception):
    pass

TRACE_REQ_LIMIT = 40

class Debugger:
    def __init__(self, web3, contracts_data, transaction_id, source_roots = []):
        self.web3 = web3;
        self.transaction_id = transaction_id
        self.source_roots = source_roots
        self.position = 0
        self.bp_stack = []
        self.contracts_stack = []
        self.load_transaction_trace()
        self.init_contracts(contracts_data)
        transaction = self.web3.eth.getTransaction(self.transaction_id)

        if transaction.to:
            self.load_contract_by_address(transaction.to.lower().replace('0x', ''), False)
        else:
            tx_receipt = web3.eth.waitForTransactionReceipt(transaction.hash)
            addr = tx_receipt.contractAddress.lower().replace('0x', '')
            self.load_contract_by_address(addr, True)

        self.breakpoints = []
        self.trace_req_counter = 0

    def init_contracts(self, contracts_data):
        self.contracts = []

        for contract_data in contracts_data:
            version = self.parse_version(contract_data['version'])

            contract_ast_by_id = {}
            contract_ast_by_name = {}

            source_list = self.resolve_source_list(contract_data['sourceList'])
            sources = []
            for src_path in source_list:
                f = open(src_path, "rb")
                src = f.read()
                f.close()
                sources.append(src.split(b"\n"))

            for key in contract_data['sources']:
                base_ast = contract_data['sources'][key]['AST']
                for contract_ast in base_ast.get('children', []):
                    if contract_ast['name'] == 'ContractDefinition':
                        contract_ast_by_id[contract_ast['id']] = contract_ast
                        contract_ast_by_name[contract_ast['attributes']['name']] = contract_ast

            for key in contract_data.get('contracts', []):
                name = key.split(":")[1]
                asts = []
                for contract_id in contract_ast_by_name[name]['attributes']['linearizedBaseContracts']:
                    asts.append(contract_ast_by_id[contract_id])
                data = contract_data['contracts'][key]
                if data['bin']:
                    contract = ContractDataLoader(data, list(reversed(asts)), source_list, sources, version).load()
                    self.contracts.append(contract)

    def resolve_source_list(self, source_list):
        result = []
        for src_path in source_list:
            if not os.path.isabs(src_path):
                abs_path = None
                for src_root in self.source_roots:
                    p = os.path.abspath(os.path.join(src_root, src_path))
                    if os.path.exists(p):
                        abs_path = p
                        break
                if not abs_path:
                    raise Exception(f"Can not find file: {src_path}")
                result.append(abs_path)
            else:
                result.append(src_path)
        return result

    def parse_version(self, version_str):
        m = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
        return [int(m.group(1)), int(m.group(2)), int(m.group(3))]

    def load_transaction_trace(self):
        self.tracer = Tracer(self.web3, self.transaction_id)
        self.trace_logs = self.tracer.get_base_logs()

    def load_contract_by_address(self, address, is_init):
        code = self.web3.eth.getCode(Web3.toChecksumAddress(address)).hex()
        code = code.replace("0x", "")
        if len(code) > 0:
            contract = self.find_contract_by_code(code)
            el = ContractCall(address, contract, is_init)
            self.contracts_stack.append(el)
            if is_init:
                self.bp_stack.append(-1)
            else:
                if contract.version < [0, 5, 1]:
                    self.bp_stack.append(-1)

    def find_contract_by_code(self, code):
        code = self.cut_bin_metadata(code)
        for contract in self.contracts:
            if self.cut_bin_metadata(contract.bin_runtime) == code:
                return contract
        raise Exception("No matching contract found in provided solidity data")

    def find_contract_by_init_code(self, code):
        code = self.cut_bin_metadata(code)
        for contract in self.contracts:
            if self.cut_bin_metadata(contract.bin_init) == code:
                return contract
        raise Exception("No matching contract found in provided solidity data")

    def current_contract(self):
        return self.contracts_stack[-1].contract

    def current_contract_address(self):
        return self.contracts_stack[-1].address

    def current_contract_is_init(self):
        return self.contracts_stack[-1].is_init

    def cut_bin_metadata(self, code):
        metadata_start = code.find("a165627a7a72305820")
        if metadata_start == -1:
            return code
        return code[:metadata_start]

    def current_op(self):
        return self.trace_logs[self.position]

    def is_ended(self):
        return self.position >= len(self.trace_logs)

    def current_instruction_num(self):
        if self.current_contract_is_init():
            pc_to_op_idx = self.current_contract().pc_to_op_idx_init
        else:
            pc_to_op_idx = self.current_contract().pc_to_op_idx_runtime
        return pc_to_op_idx.get(self.current_op()["pc"], -1)

    def current_src_fragment(self):
        if self.current_contract_is_init():
            srcmap = self.current_contract().srcmap_init
        else:
            srcmap = self.current_contract().srcmap_runtime
        instruction_num = self.current_instruction_num()
        if instruction_num == -1:
            return SrcMap(-1, -1, -1, -1)
        return srcmap[instruction_num]

    def current_source(self):
        return self.current_contract().sources[self.current_src_fragment().file_idx]

    def current_source_path(self):
        return self.current_contract().source_list[self.current_src_fragment().file_idx]

    def current_line_number(self):
        frag = self.current_src_fragment()
        if frag.file_idx == -1:
            return -1
        offset_by_line = self.current_contract().source_offsets[frag.file_idx]
        offset = frag.start
        start = 0
        end = len(offset_by_line)
        while True:
            idx = (start + end) // 2
            s = offset_by_line[idx]
            s1 = offset_by_line[idx + 1]
            if offset >= s and offset < s1:
                return idx
            elif offset < s:
                end = idx - 1
            elif offset >= s1:
                start = idx + 1

    def current_func(self):
        contract = self.current_contract()
        start = self.current_src_fragment().start
        for f in contract.functions:
            if start >= f.src.start and start < f.src.start + f.src.length:
                return f

    def get_storage_at_address(self, address):
        self.trace_req_counter += 1
        if self.trace_req_counter >= TRACE_REQ_LIMIT:
            raise EvalResultTooLarge()
        return self.tracer.get_storage(self.position, address.hex())

    def advance(self):
        self.check_function_switch()
        self.check_contract_switch()
        self.position += 1

    def check_function_switch(self):
        if self.current_src_fragment().jump == 'i':
            self.bp_stack.append(self.current_op()['stack_length'] - 1)
        if self.current_src_fragment().jump == 'o' and len(self.bp_stack) > 0:
            self.bp_stack.pop()

    def check_contract_switch(self):
        op = self.current_op()
        if op['op'] in ['CALL', 'STATICCALL']:
            address = op['new_address']
            self.load_contract_by_address(address, False)
        elif op['op'] in ['DELEGATECALL', 'CALLCODE']:
            address = op['new_address']
            address = int(address).to_bytes(20, byteorder='big').hex()
            self.load_contract_by_address(address, False)
        elif op['op'] == 'CREATE':
            address = op['new_address']
            self.load_contract_by_address(address, True)
        elif op['op'] in ['STOP', 'RETURN', 'REVERT']:
            if self.current_contract_is_init() or op['op'] == 'REVERT':
                self.bp_stack.pop()
            self.contracts_stack.pop()

    def step(self):
        start_line_number = self.current_line_number()
        while True:
            self.advance()
            if self.is_ended():
                return
            line_number = self.current_line_number()
            if line_number != -1 and line_number != start_line_number:
                return

    def next(self):
        start_stack_height = len(self.bp_stack)
        while True:
            self.step()
            if self.is_ended():
                return
            if len(self.bp_stack) <= start_stack_height:
                if self.current_src_fragment().jump == 'o':
                    self.step()
                break

    def stepout(self):
        start_stack_height = len(self.bp_stack)
        while True:
            self.step()
            if self.is_ended():
                return
            if len(self.bp_stack) == start_stack_height - 1:
                break

    def continu(self):
        self.step()
        if self.is_ended():
            return
        while True:
            self.advance()
            if self.is_ended():
                return
            for bp in self.breakpoints:
                if (bp.src == self.current_source_path()
                        and bp.line == self.current_line_number() + 1):
                    return

    def eval(self, line):
        try:
            expr = Parser(line).parse()
            res = self.eval_expr(expr)
            if type(res) is Variable:
                return self.expand_var(res)
            return res
        except ParsingFailed:
            return "Can not parse expression"
        except EvalFailed:
            return "Can not evaluate expression"
        except VarNotYetInitialized:
            return "Variable is not yet initialized"
        except EvalResultTooLarge:
            return "Evaluation result is too large"
        finally:
            self.trace_req_counter = 0

    def eval_expr(self, expr):
        if type(expr) is Literal:
            return expr.value
        elif type(expr) is Name:
            if expr.value == "this":
                return self.tracer.get_address(self.position)
            return self.eval_var(expr.value)
        elif type(expr) is ApplyBrackets:
            return self.eval_apply_brackets(expr)
        elif type(expr) is ApplyDot:
            return self.eval_apply_dot(expr)
        elif type(expr) is Not:
            value = self.eval_expr(expr.value)
            if type(value) != bool:
                raise EvalFailed()
            return not value
        elif type(expr) in [Mult, Div, Mod, Plus, Minus, Lt, Gt, Le, Ge, Eq, NotEq, And, Or]:
            return self.eval_binary_operator(expr)
        else:
            raise EvalFailed()

    def eval_binary_operator(self, expr):
        left = self.eval_expr(expr.left)
        right = self.eval_expr(expr.right)

        if type(left) != type(right):
            raise EvalFailed()

        if (type(expr) is Plus and not type(left) in [int, str]) or \
           (type(expr) in [And, Or] and type(left) != bool) or \
           (type(expr) in [Mult, Div, Mod, Minus, Gt, Ge, Lt, Le] and type(left) != int):
            raise EvalFailed()

        elif type(expr) is Mult:
            return left * right
        elif type(expr) is Div:
            if right == 0:
                raise EvalFailed()
            return left // right
        elif type(expr) is Mod:
            if right == 0:
                raise EvalFailed()
            return left % right
        if type(expr) is Plus:
            return left + right
        elif type(expr) is Minus:
            return left - right
        elif type(expr) is Gt:
            return left > right
        elif type(expr) is Ge:
            return left >= right
        elif type(expr) is Lt:
            return left < right
        elif type(expr) is Le:
            return left <= right
        elif type(expr) is Eq:
            return left == right
        elif type(expr) is NotEq:
            return left != right
        elif type(expr) is And:
            return left and right
        elif type(expr) is Or:
            return left or right
        else:
            raise EvalFailed()

    def eval_var(self, var_name):
        function = self.current_func()
        if not function:
            raise EvalFailed()

        if len(self.bp_stack) == 0:
            raise EvalFailed()

        bp = self.bp_stack[-1]
        if bp == -1:
            if self.current_contract_is_init():
                bp = len(function.params) + 0
            else:
                bp = len(function.params) + 2

        var = None
        location = None

        if var_name in function.params_by_name:
            var = function.params_by_name[var_name]
            location = bp - len(function.params) + var.location
        elif var_name in function.local_vars_by_name:
            var = function.local_vars_by_name[var_name]
            location = bp + var.location + len(function.return_vars)
        elif var_name in function.return_vars_by_name:
            var = function.return_vars_by_name[var_name]
            location = bp + var.location

        if var:
            if location >= self.current_op()['stack_length']:
                raise VarNotYetInitialized()
            data = self.tracer.get_stack(self.position, location)
            if type(var.var_type) in [Int, Uint, FixedBytes, Bool, Address]:
                return self.elementary_type_as_obj(var.var_type, data)
            else:
                new_location = (int).from_bytes(data, 'big')
                new_var = Variable(var.var_type, location = new_location, offset = 0, location_type = var.location_type)
                if var.location_type == 'memory':
                    return self.eval_memory(new_var)
                elif var.location_type == 'storage':
                    return self.eval_storage(new_var)
                else:
                    raise EvalFailed()

        if var_name in self.current_contract().variables_by_name:
            var = self.current_contract().variables_by_name[var_name]
            return self.eval_storage(var)
        else:
            raise EvalFailed()

    def eval_apply_brackets(self, expr):
        var = self.eval_expr(expr.left)
        key = self.eval_expr(expr.right)
        if not type(var) is Variable:
            raise EvalFailed()
        if var.location_type == 'memory':
            if type(var.var_type) in [Array, FixedArray]:
                return self.eval_memory_array_at_idx(var, key)
            else:
                raise EvalFailed()
        elif var.location_type == 'storage':
            if type(var.var_type) is Map:
                return self.eval_storage_map_at_key(var, key)
            elif type(var.var_type) is FixedArray:
                return self.eval_storage_fixed_array_at_idx(var, key)
            elif type(var.var_type) is Array:
                return self.eval_storage_array_at_idx(var, key)
            else:
                raise EvalFailed()
        else:
            raise EvalFailed()

    def eval_apply_dot(self, expr):
        if expr.left == Name("msg"):
            if expr.right.value == "sender":
                return self.tracer.get_sender(self.position)
            if expr.right.value == "value":
                return self.tracer.get_value(self.position)

        var = self.eval_expr(expr.left)
        if not type(var) is Variable or not type(var.var_type) is Struct:
            raise EvalFailed()
        key = expr.right.value
        if var.location_type == 'memory':
            return self.eval_memory_struct_at_key(var, key)
        elif var.location_type == 'storage':
            return self.eval_storage_struct_at_key(var, key)
        else:
            raise EvalFailed()

    def get_memory(self, idx):
        self.trace_req_counter += 1
        if self.trace_req_counter >= TRACE_REQ_LIMIT:
            raise EvalResultTooLarge()
        return self.tracer.get_memory(self.position, idx)

    def eval_memory(self, var):
        if type(var.var_type) in [Int, Uint, FixedBytes, Bool, Address]:
            return self.eval_memory_elementary_type(var)
        elif type(var.var_type) in [String, Bytes]:
            return self.eval_memory_string_or_bytes(var)
        else:
            return var

    def eval_memory_elementary_type(self, var):
        data = self.get_memory(var.location)
        return self.elementary_type_as_obj(var.var_type, data)

    def eval_memory_array_at_idx(self, var, idx):
        if type(var.var_type) is FixedArray:
            off = idx
        elif type(var.var_type) is Array:
            off = idx + 1
        addr = var.location + off * 32
        if type(var.var_type.element_type) in [String, Bytes, Struct, Array, FixedArray]:
            addr = int.from_bytes(self.get_memory(addr), byteorder='big')
        new_var = Variable(var.var_type.element_type, location = addr, location_type = 'memory')
        return self.eval_memory(new_var)

    def eval_memory_struct_at_key(self, var, key):
        for i, field in enumerate(var.var_type.variables):
            if field.name == key:
                addr = var.location + i * 32
                if type(field.var_type) in [String, Bytes, Struct, Array, FixedArray]:
                    addr = int.from_bytes(self.get_memory(addr), byteorder='big')
                new_var = Variable(field.var_type, location = addr, location_type = 'memory')
                return self.eval_memory(new_var)
        raise EvalFailed()

    def eval_memory_string_or_bytes(self, var):
        result = bytes()
        length = (int).from_bytes(self.get_memory(var.location), 'big')
        num_memory_words = (length + 31) // 32
        for i in range(num_memory_words):
            data = self.get_memory(var.location + (i + 1) * 32)[:length - i*32]
            result += data
        return self.elementary_type_as_obj(var.var_type, result)

    def eval_storage(self, var):
        if type(var.var_type) in [Int, Uint, FixedBytes, Bool, Address]:
            return self.eval_storage_elementary_type(var)
        elif type(var.var_type) in [String, Bytes]:
            return self.eval_storage_string_or_bytes(var)
        else:
            return var

    def eval_storage_elementary_type(self, var):
        address = var.location.to_bytes(32, byteorder='big')
        result = self.get_storage_at_address(address)
        result_int = int.from_bytes(result, byteorder='big')
        result_int = (result_int >> var.offset) & ((2 << var.var_type.size - 1) - 1)
        result = result_int.to_bytes(var.var_type.size // 8, byteorder='big')
        return self.elementary_type_as_obj(var.var_type, result)

    def eval_storage_string_or_bytes(self, var):
        address = var.location.to_bytes(32, 'big')
        data = self.get_storage_at_address(address)
        data_int = (int).from_bytes(data, 'big')
        large_string = data_int & 0x1
        if large_string:
            bytes_length = (data_int - 1) // 2
            s = sha3.keccak_256()
            s.update(address)
            large_str_address = s.digest()
            result = bytes()
            for i in range(0, bytes_length // 32 + 1):
                address = (int.from_bytes(large_str_address, byteorder='big') + i).to_bytes(32, byteorder='big')
                value = self.get_storage_at_address(address)
                value = value[:bytes_length - i*32]
                result += value
        else:
            bytes_length = (data_int & 0xFF) // 2
            result = data[:bytes_length]

        return self.elementary_type_as_obj(var.var_type, result)

    def location_and_offset_for_array_idx(self, arr, idx):
        if arr.element_type.size < 256:
            elems_per_slot = (256 // arr.element_type.size)
            location = idx // elems_per_slot
            offset = (idx % elems_per_slot) * arr.element_type.size
        else:
            slot_per_elems = arr.element_type.size // 256
            location = idx * slot_per_elems
            offset = 0
        return [location, offset]

    def eval_storage_fixed_array_at_idx(self, var, idx):
        element_type = var.var_type.element_type
        rel_location, offset = self.location_and_offset_for_array_idx(var.var_type, idx)
        location = var.location + rel_location
        new_var = Variable(element_type, location = location, offset = offset, location_type = 'storage')
        return self.eval_storage(new_var)

    def eval_storage_array_at_idx(self, var, idx):
        s = sha3.keccak_256()
        s.update(var.location.to_bytes(32, 'big'))
        elem_address = int.from_bytes(s.digest(), byteorder='big')
        location, offset = self.location_and_offset_for_array_idx(var.var_type, idx)
        new_var = Variable(var.var_type.element_type, location = elem_address + location, offset = offset, location_type = 'storage')
        return self.eval_storage(new_var)

    def eval_storage_map_at_key(self, var, key):
        key_bytes = None

        key_type = var.var_type.key_type

        if type(key_type) == String:
            key_bytes = bytes(key, 'utf-8')
        elif type(key_type) in [Int, Uint]:
            try:
                key_bytes = int(key).to_bytes(32, "big")
            except ValueError:
               raise EvalFailed()
        elif type(key_type) is Address:
            key_bytes = bytes(12) + bytes.fromhex(key.replace("0x", ""))
        elif type(key_type) is Bytes:
            key_bytes = bytes.fromhex(key.replace("0x", ""))
        elif type(key_type) is FixedBytes:
            key_bytes = bytes.fromhex(key.replace("0x", ""))
            key_bytes =  key_bytes + bytes(32 - len(key_bytes))
        elif type(key_type) is Bool:
            if key:
                key_bytes = (1).to_bytes(32, "big")
            else:
                key_bytes = (0).to_bytes(32, "big")
        else:
            raise EvalFailed()

        s = sha3.keccak_256()
        s.update(key_bytes)
        s.update(var.location.to_bytes(32, 'big'))
        value_address = s.digest()
        value_type = var.var_type.value_type
        location = int.from_bytes(value_address, 'big')
        var = Variable(value_type, location = location, offset = 0, location_type = 'storage')
        return self.eval_storage(var)

    def eval_storage_struct_at_key(self, var, key):
        for field in var.var_type.variables:
            if field.name == key:
                location = var.location + field.location
                new_var = Variable(field.var_type, location = location, offset = field.offset, location_type = 'storage')
                return self.eval_storage(new_var)

    def elementary_type_as_obj(self, var_type, data):
        if type(var_type) is Int:
            return (int).from_bytes(data, byteorder = 'big', signed = True)
        if type(var_type) is Uint:
            return (int).from_bytes(data, byteorder = 'big', signed = False)
        if type(var_type) is Bool:
            if (int).from_bytes(data, 'big') == 1:
                return True
            else:
                return False
        if type(var_type) is String:
            return str(data, 'utf8')
        if type(var_type) is Address:
            return data[-20:].hex()

        return data.hex()

    def expand_fixed_array(self, var):
        length = var.var_type.length
        res = []
        for i in range(length):
            if var.location_type == 'storage':
                el = self.eval_storage_fixed_array_at_idx(var, i)
            elif var.location_type == 'memory':
                el = self.eval_memory_array_at_idx(var, i)

            if type(el) is Variable:
                el = self.expand_var(el)
            res.append(el)
        return res

    def expand_array(self, var):
        res = []

        if var.location_type == 'storage':
            length = self.get_storage_at_address(var.location.to_bytes(32, 'big'))
        elif var.location_type == 'memory':
            length = self.get_memory(var.location)

        length = (int).from_bytes(length, byteorder = 'big')

        for i in range(length):
            if var.location_type == 'storage':
                el = self.eval_storage_array_at_idx(var, i)
            elif var.location_type == 'memory':
                el = self.eval_memory_array_at_idx(var, i)

            if type(el) is Variable:
                el = self.expand_var(el)
            res.append(el)
        return res

    def expand_struct(self, var):
        res = {}
        for field in var.var_type.variables:
            key = field.name
            if var.location_type == 'storage':
                el = self.eval_storage_struct_at_key(var, key)
            elif var.location_type == 'memory':
                el = self.eval_memory_struct_at_key(var, key)

            if type(el) is Variable:
                el = self.expand_var(el)
            res[key] = el
        return res

    def expand_var(self, var):
        if type(var.var_type) is Map:
            return "Map"
        elif type(var.var_type) is FixedArray:
            return self.expand_fixed_array(var)
        elif type(var.var_type) is Array:
            return self.expand_array(var)
        elif type(var.var_type) is Struct:
            return self.expand_struct(var)
        else:
            raise EvalFailed()

    def add_breakpoint(self, breakpoint):
        abs_path = None
        for contract in self.contracts:
            for src_path in contract.source_list:
                if breakpoint.src in src_path:
                    abs_path = src_path
                    break
        if abs_path:
            bp = Breakpoint(abs_path, breakpoint.line)
            self.breakpoints.append(bp)
            return bp
