# This file was generated from canopy\ArithmeticPath.peg
# See http://canopy.jcoglan.com/ for documentation.

from collections import defaultdict
import re


class TreeNode(object):
    def __init__(self, text, offset, elements=None):
        self.text = text
        self.offset = offset
        self.elements = elements or []

    def __iter__(self):
        for el in self.elements:
            yield el


class TreeNode1(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode1, self).__init__(text, offset, elements)
        self.atom = elements[0]


class TreeNode2(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode2, self).__init__(text, offset, elements)
        self.opt_ = elements[0]
        self.atom = elements[1]


class TreeNode3(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode3, self).__init__(text, offset, elements)
        self.unicode_set = elements[0]


class TreeNode4(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode4, self).__init__(text, offset, elements)
        self.variable = elements[1]


class TreeNode5(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode5, self).__init__(text, offset, elements)
        self.unicode_set = elements[0]


class TreeNode6(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode6, self).__init__(text, offset, elements)
        self.unicode_set = elements[1]


class TreeNode7(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode7, self).__init__(text, offset, elements)
        self.__ = elements[3]


class TreeNode8(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode8, self).__init__(text, offset, elements)
        self.__ = elements[4]
        self.comp_expression = elements[2]


class TreeNode9(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode9, self).__init__(text, offset, elements)
        self.__ = elements[4]


class TreeNode10(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode10, self).__init__(text, offset, elements)
        self.__ = elements[4]


class TreeNode11(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode11, self).__init__(text, offset, elements)
        self.__ = elements[6]


class TreeNode12(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode12, self).__init__(text, offset, elements)
        self.atom = elements[0]
        self.__ = elements[1]


class TreeNode13(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode13, self).__init__(text, offset, elements)
        self.__ = elements[3]
        self.atom = elements[2]


class TreeNode14(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode14, self).__init__(text, offset, elements)
        self.__ = elements[4]


class TreeNode15(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode15, self).__init__(text, offset, elements)
        self.__ = elements[3]


class TreeNode16(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode16, self).__init__(text, offset, elements)
        self.__ = elements[5]


class TreeNode17(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode17, self).__init__(text, offset, elements)
        self.__ = elements[2]
        self.data = elements[1]


class TreeNode18(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode18, self).__init__(text, offset, elements)
        self.__ = elements[2]
        self.data = elements[1]


class TreeNode19(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode19, self).__init__(text, offset, elements)
        self.__ = elements[2]
        self.data = elements[1]


class TreeNode20(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode20, self).__init__(text, offset, elements)
        self.__ = elements[2]
        self.data = elements[1]


class ParseError(SyntaxError):
    pass


FAILURE = object()


class Grammar(object):
    REGEX_1 = re.compile('^[a-zA-Z_$]')
    REGEX_2 = re.compile('^[a-zA-Z0-9_$]')
    REGEX_3 = re.compile('^[\\"]')
    REGEX_4 = re.compile('^[ !#-~]')
    REGEX_5 = re.compile('^[\\"]')
    REGEX_6 = re.compile('^[^\']')
    REGEX_7 = re.compile('^[\']')
    REGEX_8 = re.compile('^[ !#-~]')
    REGEX_9 = re.compile('^[\']')
    REGEX_10 = re.compile('^[0-9]')
    REGEX_11 = re.compile('^[0-9]')
    REGEX_12 = re.compile('^[0-9]')
    REGEX_13 = re.compile('^[\\s]')

    def _read_comp_expression(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['comp_expression'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read_atom()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            remaining0, index2, elements1, address3 = 0, self._offset, [], True
            while address3 is not FAILURE:
                index3, elements2 = self._offset, []
                address4 = FAILURE
                address4 = self._read_opt_()
                if address4 is not FAILURE:
                    elements2.append(address4)
                    address5 = FAILURE
                    address5 = self._read_atom()
                    if address5 is not FAILURE:
                        elements2.append(address5)
                    else:
                        elements2 = None
                        self._offset = index3
                else:
                    elements2 = None
                    self._offset = index3
                if elements2 is None:
                    address3 = FAILURE
                else:
                    address3 = TreeNode2(self._input[index3:self._offset], index3, elements2)
                    self._offset = self._offset
                if address3 is not FAILURE:
                    elements1.append(address3)
                    remaining0 -= 1
            if remaining0 <= 0:
                address2 = TreeNode(self._input[index2:self._offset], index2, elements1)
                self._offset = self._offset
            else:
                address2 = FAILURE
            if address2 is not FAILURE:
                elements0.append(address2)
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_comp_exp(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['comp_expression'][index0] = (address0, self._offset)
        return address0

    def _read_atom(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['atom'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1 = self._offset
        address0 = self._read_float_()
        if address0 is FAILURE:
            self._offset = index1
            address0 = self._read_number()
            if address0 is FAILURE:
                self._offset = index1
                address0 = self._read_string()
                if address0 is FAILURE:
                    self._offset = index1
                    address0 = self._read_apostrophe_string()
                    if address0 is FAILURE:
                        self._offset = index1
                        address0 = self._read_list()
                        if address0 is FAILURE:
                            self._offset = index1
                            address0 = self._read_chr()
                            if address0 is FAILURE:
                                self._offset = index1
                                address0 = self._read_boolean_()
                                if address0 is FAILURE:
                                    self._offset = index1
                                    address0 = self._read_null_()
                                    if address0 is FAILURE:
                                        self._offset = index1
                                        address0 = self._read_undefined_()
                                        if address0 is FAILURE:
                                            self._offset = index1
                                            address0 = self._read_comp_expression_ex()
                                            if address0 is FAILURE:
                                                self._offset = index1
                                                address0 = self._read_namespace()
                                                if address0 is FAILURE:
                                                    self._offset = index1
        self._cache['atom'][index0] = (address0, self._offset)
        return address0

    def _read_unicode_set(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['unicode_set'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        chunk0 = None
        if self._offset < self._input_size:
            chunk0 = self._input[self._offset:self._offset + 1]
        if chunk0 is not None and Grammar.REGEX_1.search(chunk0):
            address0 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
            self._offset = self._offset + 1
        else:
            address0 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append('[a-zA-Z_$]')
        self._cache['unicode_set'][index0] = (address0, self._offset)
        return address0

    def _read_unicode_set_with_numbers(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['unicode_set_with_numbers'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        chunk0 = None
        if self._offset < self._input_size:
            chunk0 = self._input[self._offset:self._offset + 1]
        if chunk0 is not None and Grammar.REGEX_2.search(chunk0):
            address0 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
            self._offset = self._offset + 1
        else:
            address0 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append('[a-zA-Z0-9_$]')
        self._cache['unicode_set_with_numbers'][index0] = (address0, self._offset)
        return address0

    def _read_variable(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['variable'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read_unicode_set()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            remaining0, index2, elements1, address3 = 0, self._offset, [], True
            while address3 is not FAILURE:
                address3 = self._read_unicode_set_with_numbers()
                if address3 is not FAILURE:
                    elements1.append(address3)
                    remaining0 -= 1
            if remaining0 <= 0:
                address2 = TreeNode(self._input[index2:self._offset], index2, elements1)
                self._offset = self._offset
            else:
                address2 = FAILURE
            if address2 is not FAILURE:
                elements0.append(address2)
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_attribute(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['variable'][index0] = (address0, self._offset)
        return address0

    def _read_variable_access(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['variable_access'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        chunk0 = None
        if self._offset < self._input_size:
            chunk0 = self._input[self._offset:self._offset + 1]
        if chunk0 == '.':
            address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
            self._offset = self._offset + 1
        else:
            address1 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append('"."')
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            address2 = self._read_variable()
            if address2 is not FAILURE:
                elements0.append(address2)
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_attribute_operation(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['variable_access'][index0] = (address0, self._offset)
        return address0

    def _read_map_access(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['map_access'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        chunk0 = None
        if self._offset < self._input_size:
            chunk0 = self._input[self._offset:self._offset + 1]
        if chunk0 == '[':
            address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
            self._offset = self._offset + 1
        else:
            address1 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append('"["')
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            address2 = self._read_chr()
            if address2 is FAILURE:
                self._offset = index2
                address2 = self._read_string()
                if address2 is FAILURE:
                    self._offset = index2
                    address2 = self._read_apostrophe_string()
                    if address2 is FAILURE:
                        self._offset = index2
                        address2 = self._read_number()
                        if address2 is FAILURE:
                            self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                chunk1 = None
                if self._offset < self._input_size:
                    chunk1 = self._input[self._offset:self._offset + 1]
                if chunk1 == ']':
                    address3 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                    self._offset = self._offset + 1
                else:
                    address3 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('"]"')
                if address3 is not FAILURE:
                    elements0.append(address3)
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_lookup_operation(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['map_access'][index0] = (address0, self._offset)
        return address0

    def _read_func_call(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['func_call'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read_unicode_set()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            remaining0, index2, elements1, address3 = 0, self._offset, [], True
            while address3 is not FAILURE:
                address3 = self._read_unicode_set_with_numbers()
                if address3 is not FAILURE:
                    elements1.append(address3)
                    remaining0 -= 1
            if remaining0 <= 0:
                address2 = TreeNode(self._input[index2:self._offset], index2, elements1)
                self._offset = self._offset
            else:
                address2 = FAILURE
            if address2 is not FAILURE:
                elements0.append(address2)
                address4 = FAILURE
                chunk0 = None
                if self._offset < self._input_size:
                    chunk0 = self._input[self._offset:self._offset + 1]
                if chunk0 == '(':
                    address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                    self._offset = self._offset + 1
                else:
                    address4 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('"("')
                if address4 is not FAILURE:
                    elements0.append(address4)
                    address5 = FAILURE
                    index3 = self._offset
                    address5 = self._read_atom()
                    if address5 is FAILURE:
                        address5 = TreeNode(self._input[index3:index3], index3)
                        self._offset = index3
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        chunk1 = None
                        if self._offset < self._input_size:
                            chunk1 = self._input[self._offset:self._offset + 1]
                        if chunk1 == ')':
                            address6 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                            self._offset = self._offset + 1
                        else:
                            address6 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append('")"')
                        if address6 is not FAILURE:
                            elements0.append(address6)
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_function_operation(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['func_call'][index0] = (address0, self._offset)
        return address0

    def _read_func_call_access(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['func_call_access'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        chunk0 = None
        if self._offset < self._input_size:
            chunk0 = self._input[self._offset:self._offset + 1]
        if chunk0 == '.':
            address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
            self._offset = self._offset + 1
        else:
            address1 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append('"."')
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            address2 = self._read_unicode_set()
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index2, elements1, address4 = 0, self._offset, [], True
                while address4 is not FAILURE:
                    address4 = self._read_unicode_set_with_numbers()
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index2:self._offset], index2, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 == '(':
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"("')
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        index3 = self._offset
                        address6 = self._read_atom()
                        if address6 is FAILURE:
                            address6 = TreeNode(self._input[index3:index3], index3)
                            self._offset = index3
                        if address6 is not FAILURE:
                            elements0.append(address6)
                            address7 = FAILURE
                            chunk2 = None
                            if self._offset < self._input_size:
                                chunk2 = self._input[self._offset:self._offset + 1]
                            if chunk2 == ')':
                                address7 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                self._offset = self._offset + 1
                            else:
                                address7 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append('")"')
                            if address7 is not FAILURE:
                                elements0.append(address7)
                            else:
                                elements0 = None
                                self._offset = index1
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_function_operation_access(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['func_call_access'][index0] = (address0, self._offset)
        return address0

    def _read_namespace(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['namespace'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            address2 = self._read_func_call()
            if address2 is FAILURE:
                self._offset = index2
                address2 = self._read_variable()
                if address2 is FAILURE:
                    self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index3, elements1, address4 = 0, self._offset, [], True
                while address4 is not FAILURE:
                    index4 = self._offset
                    address4 = self._read_func_call_access()
                    if address4 is FAILURE:
                        self._offset = index4
                        address4 = self._read_map_access()
                        if address4 is FAILURE:
                            self._offset = index4
                            address4 = self._read_variable_access()
                            if address4 is FAILURE:
                                self._offset = index4
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index3:self._offset], index3, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    address5 = self._read___()
                    if address5 is not FAILURE:
                        elements0.append(address5)
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_and_execute_namespace_operation(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['namespace'][index0] = (address0, self._offset)
        return address0

    def _read_comp_expression_ex(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['comp_expression_ex'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '(':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"("')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read_comp_expression()
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address4 = FAILURE
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 == ')':
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('")"')
                    if address4 is not FAILURE:
                        elements0.append(address4)
                        address5 = FAILURE
                        address5 = self._read___()
                        if address5 is not FAILURE:
                            elements0.append(address5)
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_comp_exp_ex(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['comp_expression_ex'][index0] = (address0, self._offset)
        return address0

    def _read_string(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['string'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 is not None and Grammar.REGEX_3.search(chunk0):
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('[\\"]')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index2, elements1, address4 = 0, self._offset, [], True
                while address4 is not FAILURE:
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 is not None and Grammar.REGEX_4.search(chunk1):
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[ !#-~]')
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index2:self._offset], index2, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 1]
                    if chunk2 is not None and Grammar.REGEX_5.search(chunk2):
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[\\"]')
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        address6 = self._read___()
                        if address6 is not FAILURE:
                            elements0.append(address6)
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_string(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['string'][index0] = (address0, self._offset)
        return address0

    def _read_apostrophe_string(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['apostrophe_string'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '\'':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"\'"')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index2, elements1, address4 = 0, self._offset, [], True
                while address4 is not FAILURE:
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 is not None and Grammar.REGEX_6.search(chunk1):
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[^\']')
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index2:self._offset], index2, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 1]
                    if chunk2 == '\'':
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"\'"')
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        address6 = self._read___()
                        if address6 is not FAILURE:
                            elements0.append(address6)
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_apostrophe_string(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['apostrophe_string'][index0] = (address0, self._offset)
        return address0

    def _read_list(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['list'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '[':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"["')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read___()
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address4 = FAILURE
                    index2 = self._offset
                    index3, elements1 = self._offset, []
                    address5 = FAILURE
                    address5 = self._read_atom()
                    if address5 is not FAILURE:
                        elements1.append(address5)
                        address6 = FAILURE
                        address6 = self._read___()
                        if address6 is not FAILURE:
                            elements1.append(address6)
                            address7 = FAILURE
                            remaining0, index4, elements2, address8 = 0, self._offset, [], True
                            while address8 is not FAILURE:
                                index5, elements3 = self._offset, []
                                address9 = FAILURE
                                chunk1 = None
                                if self._offset < self._input_size:
                                    chunk1 = self._input[self._offset:self._offset + 1]
                                if chunk1 == ',':
                                    address9 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                    self._offset = self._offset + 1
                                else:
                                    address9 = FAILURE
                                    if self._offset > self._failure:
                                        self._failure = self._offset
                                        self._expected = []
                                    if self._offset == self._failure:
                                        self._expected.append('","')
                                if address9 is not FAILURE:
                                    elements3.append(address9)
                                    address10 = FAILURE
                                    address10 = self._read___()
                                    if address10 is not FAILURE:
                                        elements3.append(address10)
                                        address11 = FAILURE
                                        address11 = self._read_atom()
                                        if address11 is not FAILURE:
                                            elements3.append(address11)
                                            address12 = FAILURE
                                            address12 = self._read___()
                                            if address12 is not FAILURE:
                                                elements3.append(address12)
                                            else:
                                                elements3 = None
                                                self._offset = index5
                                        else:
                                            elements3 = None
                                            self._offset = index5
                                    else:
                                        elements3 = None
                                        self._offset = index5
                                else:
                                    elements3 = None
                                    self._offset = index5
                                if elements3 is None:
                                    address8 = FAILURE
                                else:
                                    address8 = TreeNode13(self._input[index5:self._offset], index5, elements3)
                                    self._offset = self._offset
                                if address8 is not FAILURE:
                                    elements2.append(address8)
                                    remaining0 -= 1
                            if remaining0 <= 0:
                                address7 = TreeNode(self._input[index4:self._offset], index4, elements2)
                                self._offset = self._offset
                            else:
                                address7 = FAILURE
                            if address7 is not FAILURE:
                                elements1.append(address7)
                            else:
                                elements1 = None
                                self._offset = index3
                        else:
                            elements1 = None
                            self._offset = index3
                    else:
                        elements1 = None
                        self._offset = index3
                    if elements1 is None:
                        address4 = FAILURE
                    else:
                        address4 = TreeNode12(self._input[index3:self._offset], index3, elements1)
                        self._offset = self._offset
                    if address4 is FAILURE:
                        address4 = TreeNode(self._input[index2:index2], index2)
                        self._offset = index2
                    if address4 is not FAILURE:
                        elements0.append(address4)
                        address13 = FAILURE
                        address13 = self._read___()
                        if address13 is not FAILURE:
                            elements0.append(address13)
                            address14 = FAILURE
                            chunk2 = None
                            if self._offset < self._input_size:
                                chunk2 = self._input[self._offset:self._offset + 1]
                            if chunk2 == ']':
                                address14 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                self._offset = self._offset + 1
                            else:
                                address14 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append('"]"')
                            if address14 is not FAILURE:
                                elements0.append(address14)
                                address15 = FAILURE
                                address15 = self._read___()
                                if address15 is not FAILURE:
                                    elements0.append(address15)
                                else:
                                    elements0 = None
                                    self._offset = index1
                            else:
                                elements0 = None
                                self._offset = index1
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_list(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['list'][index0] = (address0, self._offset)
        return address0

    def _read_chr(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['chr'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 is not None and Grammar.REGEX_7.search(chunk0):
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('[\']')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                chunk1 = None
                if self._offset < self._input_size:
                    chunk1 = self._input[self._offset:self._offset + 1]
                if chunk1 is not None and Grammar.REGEX_8.search(chunk1):
                    address3 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                    self._offset = self._offset + 1
                else:
                    address3 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('[ !#-~]')
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address4 = FAILURE
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 1]
                    if chunk2 is not None and Grammar.REGEX_9.search(chunk2):
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[\']')
                    if address4 is not FAILURE:
                        elements0.append(address4)
                        address5 = FAILURE
                        address5 = self._read___()
                        if address5 is not FAILURE:
                            elements0.append(address5)
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_char(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['chr'][index0] = (address0, self._offset)
        return address0

    def _read_number(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['number'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '-':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"-"')
            if address2 is FAILURE:
                address2 = TreeNode(self._input[index2:index2], index2)
                self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index3, elements1, address4 = 1, self._offset, [], True
                while address4 is not FAILURE:
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 is not None and Grammar.REGEX_10.search(chunk1):
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[0-9]')
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index3:self._offset], index3, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    address5 = self._read___()
                    if address5 is not FAILURE:
                        elements0.append(address5)
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_number(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['number'][index0] = (address0, self._offset)
        return address0

    def _read_float_(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['float_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '-':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"-"')
            if address2 is FAILURE:
                address2 = TreeNode(self._input[index2:index2], index2)
                self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                remaining0, index3, elements1, address4 = 1, self._offset, [], True
                while address4 is not FAILURE:
                    chunk1 = None
                    if self._offset < self._input_size:
                        chunk1 = self._input[self._offset:self._offset + 1]
                    if chunk1 is not None and Grammar.REGEX_11.search(chunk1):
                        address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address4 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('[0-9]')
                    if address4 is not FAILURE:
                        elements1.append(address4)
                        remaining0 -= 1
                if remaining0 <= 0:
                    address3 = TreeNode(self._input[index3:self._offset], index3, elements1)
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address5 = FAILURE
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 1]
                    if chunk2 == '.':
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"."')
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        remaining1, index4, elements2, address7 = 1, self._offset, [], True
                        while address7 is not FAILURE:
                            chunk3 = None
                            if self._offset < self._input_size:
                                chunk3 = self._input[self._offset:self._offset + 1]
                            if chunk3 is not None and Grammar.REGEX_12.search(chunk3):
                                address7 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                self._offset = self._offset + 1
                            else:
                                address7 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append('[0-9]')
                            if address7 is not FAILURE:
                                elements2.append(address7)
                                remaining1 -= 1
                        if remaining1 <= 0:
                            address6 = TreeNode(self._input[index4:self._offset], index4, elements2)
                            self._offset = self._offset
                        else:
                            address6 = FAILURE
                        if address6 is not FAILURE:
                            elements0.append(address6)
                            address8 = FAILURE
                            address8 = self._read___()
                            if address8 is not FAILURE:
                                elements0.append(address8)
                            else:
                                elements0 = None
                                self._offset = index1
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_float(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['float_'][index0] = (address0, self._offset)
        return address0

    def _read_boolean_(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['boolean_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 4]
            if chunk0 == 'True':
                address2 = TreeNode(self._input[self._offset:self._offset + 4], self._offset)
                self._offset = self._offset + 4
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"True"')
            if address2 is FAILURE:
                self._offset = index2
                chunk1 = None
                if self._offset < self._input_size:
                    chunk1 = self._input[self._offset:self._offset + 4]
                if chunk1 == 'true':
                    address2 = TreeNode(self._input[self._offset:self._offset + 4], self._offset)
                    self._offset = self._offset + 4
                else:
                    address2 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('"true"')
                if address2 is FAILURE:
                    self._offset = index2
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 5]
                    if chunk2 == 'False':
                        address2 = TreeNode(self._input[self._offset:self._offset + 5], self._offset)
                        self._offset = self._offset + 5
                    else:
                        address2 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"False"')
                    if address2 is FAILURE:
                        self._offset = index2
                        chunk3 = None
                        if self._offset < self._input_size:
                            chunk3 = self._input[self._offset:self._offset + 5]
                        if chunk3 == 'false':
                            address2 = TreeNode(self._input[self._offset:self._offset + 5], self._offset)
                            self._offset = self._offset + 5
                        else:
                            address2 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append('"false"')
                        if address2 is FAILURE:
                            self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read___()
                if address3 is not FAILURE:
                    elements0.append(address3)
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_bool(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['boolean_'][index0] = (address0, self._offset)
        return address0

    def _read_null_(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['null_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 4]
            if chunk0 == 'None':
                address2 = TreeNode(self._input[self._offset:self._offset + 4], self._offset)
                self._offset = self._offset + 4
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"None"')
            if address2 is FAILURE:
                self._offset = index2
                chunk1 = None
                if self._offset < self._input_size:
                    chunk1 = self._input[self._offset:self._offset + 3]
                if chunk1 == 'nil':
                    address2 = TreeNode(self._input[self._offset:self._offset + 3], self._offset)
                    self._offset = self._offset + 3
                else:
                    address2 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('"nil"')
                if address2 is FAILURE:
                    self._offset = index2
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 4]
                    if chunk2 == 'null':
                        address2 = TreeNode(self._input[self._offset:self._offset + 4], self._offset)
                        self._offset = self._offset + 4
                    else:
                        address2 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"null"')
                    if address2 is FAILURE:
                        self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read___()
                if address3 is not FAILURE:
                    elements0.append(address3)
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_null(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['null_'][index0] = (address0, self._offset)
        return address0

    def _read_undefined_(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['undefined_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 9]
            if chunk0 == 'undefined':
                address2 = TreeNode(self._input[self._offset:self._offset + 9], self._offset)
                self._offset = self._offset + 9
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"undefined"')
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read___()
                if address3 is not FAILURE:
                    elements0.append(address3)
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_undefined(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['undefined_'][index0] = (address0, self._offset)
        return address0

    def _read_opt_(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['opt_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        address1 = self._read___()
        if address1 is not FAILURE:
            elements0.append(address1)
            address2 = FAILURE
            index2 = self._offset
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 == '+':
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('"+"')
            if address2 is FAILURE:
                self._offset = index2
                chunk1 = None
                if self._offset < self._input_size:
                    chunk1 = self._input[self._offset:self._offset + 1]
                if chunk1 == '-':
                    address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                    self._offset = self._offset + 1
                else:
                    address2 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append('"-"')
                if address2 is FAILURE:
                    self._offset = index2
                    chunk2 = None
                    if self._offset < self._input_size:
                        chunk2 = self._input[self._offset:self._offset + 1]
                    if chunk2 == '*':
                        address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                        self._offset = self._offset + 1
                    else:
                        address2 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append('"*"')
                    if address2 is FAILURE:
                        self._offset = index2
                        chunk3 = None
                        if self._offset < self._input_size:
                            chunk3 = self._input[self._offset:self._offset + 1]
                        if chunk3 == '/':
                            address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                            self._offset = self._offset + 1
                        else:
                            address2 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append('"/"')
                        if address2 is FAILURE:
                            self._offset = index2
                            chunk4 = None
                            if self._offset < self._input_size:
                                chunk4 = self._input[self._offset:self._offset + 2]
                            if chunk4 == '<=':
                                address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                self._offset = self._offset + 2
                            else:
                                address2 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append('"<="')
                            if address2 is FAILURE:
                                self._offset = index2
                                chunk5 = None
                                if self._offset < self._input_size:
                                    chunk5 = self._input[self._offset:self._offset + 2]
                                if chunk5 == '>=':
                                    address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                    self._offset = self._offset + 2
                                else:
                                    address2 = FAILURE
                                    if self._offset > self._failure:
                                        self._failure = self._offset
                                        self._expected = []
                                    if self._offset == self._failure:
                                        self._expected.append('">="')
                                if address2 is FAILURE:
                                    self._offset = index2
                                    chunk6 = None
                                    if self._offset < self._input_size:
                                        chunk6 = self._input[self._offset:self._offset + 2]
                                    if chunk6 == '!=':
                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                        self._offset = self._offset + 2
                                    else:
                                        address2 = FAILURE
                                        if self._offset > self._failure:
                                            self._failure = self._offset
                                            self._expected = []
                                        if self._offset == self._failure:
                                            self._expected.append('"!="')
                                    if address2 is FAILURE:
                                        self._offset = index2
                                        chunk7 = None
                                        if self._offset < self._input_size:
                                            chunk7 = self._input[self._offset:self._offset + 2]
                                        if chunk7 == '==':
                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                            self._offset = self._offset + 2
                                        else:
                                            address2 = FAILURE
                                            if self._offset > self._failure:
                                                self._failure = self._offset
                                                self._expected = []
                                            if self._offset == self._failure:
                                                self._expected.append('"=="')
                                        if address2 is FAILURE:
                                            self._offset = index2
                                            chunk8 = None
                                            if self._offset < self._input_size:
                                                chunk8 = self._input[self._offset:self._offset + 1]
                                            if chunk8 == '=':
                                                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                                self._offset = self._offset + 1
                                            else:
                                                address2 = FAILURE
                                                if self._offset > self._failure:
                                                    self._failure = self._offset
                                                    self._expected = []
                                                if self._offset == self._failure:
                                                    self._expected.append('"="')
                                            if address2 is FAILURE:
                                                self._offset = index2
                                                chunk9 = None
                                                if self._offset < self._input_size:
                                                    chunk9 = self._input[self._offset:self._offset + 1]
                                                if chunk9 == '>':
                                                    address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                                    self._offset = self._offset + 1
                                                else:
                                                    address2 = FAILURE
                                                    if self._offset > self._failure:
                                                        self._failure = self._offset
                                                        self._expected = []
                                                    if self._offset == self._failure:
                                                        self._expected.append('">"')
                                                if address2 is FAILURE:
                                                    self._offset = index2
                                                    chunk10 = None
                                                    if self._offset < self._input_size:
                                                        chunk10 = self._input[self._offset:self._offset + 1]
                                                    if chunk10 == '<':
                                                        address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                                                        self._offset = self._offset + 1
                                                    else:
                                                        address2 = FAILURE
                                                        if self._offset > self._failure:
                                                            self._failure = self._offset
                                                            self._expected = []
                                                        if self._offset == self._failure:
                                                            self._expected.append('"<"')
                                                    if address2 is FAILURE:
                                                        self._offset = index2
                                                        chunk11 = None
                                                        if self._offset < self._input_size:
                                                            chunk11 = self._input[self._offset:self._offset + 2]
                                                        if chunk11 == 'LT':
                                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                            self._offset = self._offset + 2
                                                        else:
                                                            address2 = FAILURE
                                                            if self._offset > self._failure:
                                                                self._failure = self._offset
                                                                self._expected = []
                                                            if self._offset == self._failure:
                                                                self._expected.append('"LT"')
                                                        if address2 is FAILURE:
                                                            self._offset = index2
                                                            chunk12 = None
                                                            if self._offset < self._input_size:
                                                                chunk12 = self._input[self._offset:self._offset + 2]
                                                            if chunk12 == 'GT':
                                                                address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                self._offset = self._offset + 2
                                                            else:
                                                                address2 = FAILURE
                                                                if self._offset > self._failure:
                                                                    self._failure = self._offset
                                                                    self._expected = []
                                                                if self._offset == self._failure:
                                                                    self._expected.append('"GT"')
                                                            if address2 is FAILURE:
                                                                self._offset = index2
                                                                chunk13 = None
                                                                if self._offset < self._input_size:
                                                                    chunk13 = self._input[self._offset:self._offset + 2]
                                                                if chunk13 == 'LE':
                                                                    address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                    self._offset = self._offset + 2
                                                                else:
                                                                    address2 = FAILURE
                                                                    if self._offset > self._failure:
                                                                        self._failure = self._offset
                                                                        self._expected = []
                                                                    if self._offset == self._failure:
                                                                        self._expected.append('"LE"')
                                                                if address2 is FAILURE:
                                                                    self._offset = index2
                                                                    chunk14 = None
                                                                    if self._offset < self._input_size:
                                                                        chunk14 = self._input[self._offset:self._offset + 2]
                                                                    if chunk14 == 'GE':
                                                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                        self._offset = self._offset + 2
                                                                    else:
                                                                        address2 = FAILURE
                                                                        if self._offset > self._failure:
                                                                            self._failure = self._offset
                                                                            self._expected = []
                                                                        if self._offset == self._failure:
                                                                            self._expected.append('"GE"')
                                                                    if address2 is FAILURE:
                                                                        self._offset = index2
                                                                        chunk15 = None
                                                                        if self._offset < self._input_size:
                                                                            chunk15 = self._input[self._offset:self._offset + 2]
                                                                        if chunk15 == 'EQ':
                                                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                            self._offset = self._offset + 2
                                                                        else:
                                                                            address2 = FAILURE
                                                                            if self._offset > self._failure:
                                                                                self._failure = self._offset
                                                                                self._expected = []
                                                                            if self._offset == self._failure:
                                                                                self._expected.append('"EQ"')
                                                                        if address2 is FAILURE:
                                                                            self._offset = index2
                                                                            chunk16 = None
                                                                            if self._offset < self._input_size:
                                                                                chunk16 = self._input[self._offset:self._offset + 2]
                                                                            if chunk16 == 'NE':
                                                                                address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                self._offset = self._offset + 2
                                                                            else:
                                                                                address2 = FAILURE
                                                                                if self._offset > self._failure:
                                                                                    self._failure = self._offset
                                                                                    self._expected = []
                                                                                if self._offset == self._failure:
                                                                                    self._expected.append('"NE"')
                                                                            if address2 is FAILURE:
                                                                                self._offset = index2
                                                                                chunk17 = None
                                                                                if self._offset < self._input_size:
                                                                                    chunk17 = self._input[self._offset:self._offset + 2]
                                                                                if chunk17 == 'lt':
                                                                                    address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                    self._offset = self._offset + 2
                                                                                else:
                                                                                    address2 = FAILURE
                                                                                    if self._offset > self._failure:
                                                                                        self._failure = self._offset
                                                                                        self._expected = []
                                                                                    if self._offset == self._failure:
                                                                                        self._expected.append('"lt"')
                                                                                if address2 is FAILURE:
                                                                                    self._offset = index2
                                                                                    chunk18 = None
                                                                                    if self._offset < self._input_size:
                                                                                        chunk18 = self._input[self._offset:self._offset + 2]
                                                                                    if chunk18 == 'gt':
                                                                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                        self._offset = self._offset + 2
                                                                                    else:
                                                                                        address2 = FAILURE
                                                                                        if self._offset > self._failure:
                                                                                            self._failure = self._offset
                                                                                            self._expected = []
                                                                                        if self._offset == self._failure:
                                                                                            self._expected.append('"gt"')
                                                                                    if address2 is FAILURE:
                                                                                        self._offset = index2
                                                                                        chunk19 = None
                                                                                        if self._offset < self._input_size:
                                                                                            chunk19 = self._input[self._offset:self._offset + 2]
                                                                                        if chunk19 == 'le':
                                                                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                            self._offset = self._offset + 2
                                                                                        else:
                                                                                            address2 = FAILURE
                                                                                            if self._offset > self._failure:
                                                                                                self._failure = self._offset
                                                                                                self._expected = []
                                                                                            if self._offset == self._failure:
                                                                                                self._expected.append('"le"')
                                                                                        if address2 is FAILURE:
                                                                                            self._offset = index2
                                                                                            chunk20 = None
                                                                                            if self._offset < self._input_size:
                                                                                                chunk20 = self._input[self._offset:self._offset + 2]
                                                                                            if chunk20 == 'ge':
                                                                                                address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                self._offset = self._offset + 2
                                                                                            else:
                                                                                                address2 = FAILURE
                                                                                                if self._offset > self._failure:
                                                                                                    self._failure = self._offset
                                                                                                    self._expected = []
                                                                                                if self._offset == self._failure:
                                                                                                    self._expected.append('"ge"')
                                                                                            if address2 is FAILURE:
                                                                                                self._offset = index2
                                                                                                chunk21 = None
                                                                                                if self._offset < self._input_size:
                                                                                                    chunk21 = self._input[self._offset:self._offset + 2]
                                                                                                if chunk21 == 'eq':
                                                                                                    address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                    self._offset = self._offset + 2
                                                                                                else:
                                                                                                    address2 = FAILURE
                                                                                                    if self._offset > self._failure:
                                                                                                        self._failure = self._offset
                                                                                                        self._expected = []
                                                                                                    if self._offset == self._failure:
                                                                                                        self._expected.append('"eq"')
                                                                                                if address2 is FAILURE:
                                                                                                    self._offset = index2
                                                                                                    chunk22 = None
                                                                                                    if self._offset < self._input_size:
                                                                                                        chunk22 = self._input[self._offset:self._offset + 2]
                                                                                                    if chunk22 == 'ne':
                                                                                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                        self._offset = self._offset + 2
                                                                                                    else:
                                                                                                        address2 = FAILURE
                                                                                                        if self._offset > self._failure:
                                                                                                            self._failure = self._offset
                                                                                                            self._expected = []
                                                                                                        if self._offset == self._failure:
                                                                                                            self._expected.append('"ne"')
                                                                                                    if address2 is FAILURE:
                                                                                                        self._offset = index2
                                                                                                        chunk23 = None
                                                                                                        if self._offset < self._input_size:
                                                                                                            chunk23 = self._input[self._offset:self._offset + 2]
                                                                                                        if chunk23 == 'in':
                                                                                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                            self._offset = self._offset + 2
                                                                                                        else:
                                                                                                            address2 = FAILURE
                                                                                                            if self._offset > self._failure:
                                                                                                                self._failure = self._offset
                                                                                                                self._expected = []
                                                                                                            if self._offset == self._failure:
                                                                                                                self._expected.append('"in"')
                                                                                                        if address2 is FAILURE:
                                                                                                            self._offset = index2
                                                                                                            chunk24 = None
                                                                                                            if self._offset < self._input_size:
                                                                                                                chunk24 = self._input[self._offset:self._offset + 2]
                                                                                                            if chunk24 == 'IN':
                                                                                                                address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                                self._offset = self._offset + 2
                                                                                                            else:
                                                                                                                address2 = FAILURE
                                                                                                                if self._offset > self._failure:
                                                                                                                    self._failure = self._offset
                                                                                                                    self._expected = []
                                                                                                                if self._offset == self._failure:
                                                                                                                    self._expected.append('"IN"')
                                                                                                            if address2 is FAILURE:
                                                                                                                self._offset = index2
                                                                                                                chunk25 = None
                                                                                                                if self._offset < self._input_size:
                                                                                                                    chunk25 = self._input[self._offset:self._offset + 2]
                                                                                                                if chunk25 == 'or':
                                                                                                                    address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                                    self._offset = self._offset + 2
                                                                                                                else:
                                                                                                                    address2 = FAILURE
                                                                                                                    if self._offset > self._failure:
                                                                                                                        self._failure = self._offset
                                                                                                                        self._expected = []
                                                                                                                    if self._offset == self._failure:
                                                                                                                        self._expected.append('"or"')
                                                                                                                if address2 is FAILURE:
                                                                                                                    self._offset = index2
                                                                                                                    chunk26 = None
                                                                                                                    if self._offset < self._input_size:
                                                                                                                        chunk26 = self._input[self._offset:self._offset + 2]
                                                                                                                    if chunk26 == 'OR':
                                                                                                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                                        self._offset = self._offset + 2
                                                                                                                    else:
                                                                                                                        address2 = FAILURE
                                                                                                                        if self._offset > self._failure:
                                                                                                                            self._failure = self._offset
                                                                                                                            self._expected = []
                                                                                                                        if self._offset == self._failure:
                                                                                                                            self._expected.append('"OR"')
                                                                                                                    if address2 is FAILURE:
                                                                                                                        self._offset = index2
                                                                                                                        chunk27 = None
                                                                                                                        if self._offset < self._input_size:
                                                                                                                            chunk27 = self._input[self._offset:self._offset + 2]
                                                                                                                        if chunk27 == '||':
                                                                                                                            address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                                            self._offset = self._offset + 2
                                                                                                                        else:
                                                                                                                            address2 = FAILURE
                                                                                                                            if self._offset > self._failure:
                                                                                                                                self._failure = self._offset
                                                                                                                                self._expected = []
                                                                                                                            if self._offset == self._failure:
                                                                                                                                self._expected.append('"||"')
                                                                                                                        if address2 is FAILURE:
                                                                                                                            self._offset = index2
                                                                                                                            chunk28 = None
                                                                                                                            if self._offset < self._input_size:
                                                                                                                                chunk28 = self._input[self._offset:self._offset + 3]
                                                                                                                            if chunk28 == 'and':
                                                                                                                                address2 = TreeNode(self._input[self._offset:self._offset + 3], self._offset)
                                                                                                                                self._offset = self._offset + 3
                                                                                                                            else:
                                                                                                                                address2 = FAILURE
                                                                                                                                if self._offset > self._failure:
                                                                                                                                    self._failure = self._offset
                                                                                                                                    self._expected = []
                                                                                                                                if self._offset == self._failure:
                                                                                                                                    self._expected.append('"and"')
                                                                                                                            if address2 is FAILURE:
                                                                                                                                self._offset = index2
                                                                                                                                chunk29 = None
                                                                                                                                if self._offset < self._input_size:
                                                                                                                                    chunk29 = self._input[self._offset:self._offset + 3]
                                                                                                                                if chunk29 == 'AND':
                                                                                                                                    address2 = TreeNode(self._input[self._offset:self._offset + 3], self._offset)
                                                                                                                                    self._offset = self._offset + 3
                                                                                                                                else:
                                                                                                                                    address2 = FAILURE
                                                                                                                                    if self._offset > self._failure:
                                                                                                                                        self._failure = self._offset
                                                                                                                                        self._expected = []
                                                                                                                                    if self._offset == self._failure:
                                                                                                                                        self._expected.append('"AND"')
                                                                                                                                if address2 is FAILURE:
                                                                                                                                    self._offset = index2
                                                                                                                                    chunk30 = None
                                                                                                                                    if self._offset < self._input_size:
                                                                                                                                        chunk30 = self._input[self._offset:self._offset + 2]
                                                                                                                                    if chunk30 == '&&':
                                                                                                                                        address2 = TreeNode(self._input[self._offset:self._offset + 2], self._offset)
                                                                                                                                        self._offset = self._offset + 2
                                                                                                                                    else:
                                                                                                                                        address2 = FAILURE
                                                                                                                                        if self._offset > self._failure:
                                                                                                                                            self._failure = self._offset
                                                                                                                                            self._expected = []
                                                                                                                                        if self._offset == self._failure:
                                                                                                                                            self._expected.append('"&&"')
                                                                                                                                    if address2 is FAILURE:
                                                                                                                                        self._offset = index2
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                address3 = self._read___()
                if address3 is not FAILURE:
                    elements0.append(address3)
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = self._actions.make_opt(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        self._cache['opt_'][index0] = (address0, self._offset)
        return address0

    def _read___(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['__'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        remaining0, index1, elements0, address1 = 0, self._offset, [], True
        while address1 is not FAILURE:
            chunk0 = None
            if self._offset < self._input_size:
                chunk0 = self._input[self._offset:self._offset + 1]
            if chunk0 is not None and Grammar.REGEX_13.search(chunk0):
                address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset)
                self._offset = self._offset + 1
            else:
                address1 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append('[\\s]')
            if address1 is not FAILURE:
                elements0.append(address1)
                remaining0 -= 1
        if remaining0 <= 0:
            address0 = TreeNode(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        self._cache['__'][index0] = (address0, self._offset)
        return address0


class Parser(Grammar):
    def __init__(self, input, actions, types):
        self._input = input
        self._input_size = len(input)
        self._actions = actions
        self._types = types
        self._offset = 0
        self._cache = defaultdict(dict)
        self._failure = 0
        self._expected = []

    def parse(self):
        tree = self._read_comp_expression()
        if tree is not FAILURE and self._offset == self._input_size:
            return tree
        if not self._expected:
            self._failure = self._offset
            self._expected.append('<EOF>')
        raise ParseError(format_error(self._input, self._failure, self._expected))


def format_error(input, offset, expected):
    lines, line_no, position = input.split('\n'), 0, 0
    while position <= offset:
        position += len(lines[line_no]) + 1
        line_no += 1
    message, line = 'Line ' + str(line_no) + ': expected ' + ', '.join(expected) + '\n', lines[line_no - 1]
    message += line + '\n'
    position -= len(line) + 1
    message += ' ' * (offset - position)
    return message + '^'

def parse(input, actions=None, types=None):
    parser = Parser(input, actions, types)
    return parser.parse()
