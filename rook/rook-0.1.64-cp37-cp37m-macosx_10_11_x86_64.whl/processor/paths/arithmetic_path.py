import six
from ...logger import logger

from rook.processor.paths.arithmetic_path_internal import parse, ParseError
from rook.exceptions import RookInvalidArithmeticPath, RookNonPrimitiveObjectType, RookAttributeNotFound, RookOperationReadOnly, RookExceptionEvaluationFailed
from ..namespaces.python_object_namespace import PythonObjectNamespace
from ..namespaces.container_namespace import ContainerNamespace


'''
Canopy is used to build and evaluate a tree of operations.
a .peg file (Rookout/canopy/ArithmeticPath.peg) is compiled into the various rooks languages.
Canopy is a PEG parser compiler - and i extend its goal to actually evaluate our arithmetic paths.
'''


ops = {"NE": "!=",
       "=": "==",
       "EQ": "==",
       "LT": "<",
       "GT": ">",
       "GE": ">=",
       "LE": "<=",
       "AND": " and ",
       "OR": " or ",
       "&&": " and ",
       "||": " or "}


level1 = ["*", "/"]
level2 = ["+", "-"]
level3 = ["<=", ">=", "!=", "=", "==", ">", "<", "LT", "GT", "LE", "GE", "EQ", "NE", "lt", "gt", "le", "ge", "eq", "ne"]
level4 = ["in", "IN"]
level5 = ["or", "OR", "||", "and", "AND", "&&"]

allLevels = [level1, level2, level3, level4, level5]

try:
    PRIMITIVE_VALUES = (str, unicode, int, long, float, list)
except NameError:
    PRIMITIVE_VALUES = (str, int, float, list)


class Marker(object):
    pass


class FunctionOperation(Marker):
    def __init__(self, function_name, function_arguments):
        self.function_name = function_name
        self.function_arguments = function_arguments

    def read(self, namespace, create):
        return namespace.call_method(self.function_name, self.function_arguments)

    def write(self, namespace, value):
        raise RookOperationReadOnly(type(self))


class AttributeOperation(Marker):
    def __init__(self, name):
        self.name = name

    def read(self, namespace, create):
        try:
            return namespace.read_attribute(self.name)
        except RookAttributeNotFound as exc:
            if create:
                namespace.write_attribute(self.name, ContainerNamespace({}))
                return namespace.read_attribute(self.name)
            else:
                raise

    def write(self, namespace, value):
        return namespace.write_attribute(self.name, value)


class LookupOperation(Marker):
    def __init__(self, name):
        if name.startswith("'"):
            self.name = name.strip("'")
        elif name.startswith('"'):
            self.name = name.strip('"')
        else:
            self.name = int(name)

    def read(self, namespace, create):
        return namespace.read_key(self.name)

    def write(self, namespace, value):
        raise RookOperationReadOnly(type(self))


class ToolException(Marker):
    def __init__(self, exc):
        self.obj = exc

    def to_string(self):
        return str(self.obj)


class NamespaceResult(Marker):
    def __init__(self, namespace):
        self.obj = namespace
        if isinstance(namespace, PythonObjectNamespace):
            if isinstance(namespace.obj, six.string_types):
                self.text = '\'' + namespace.obj + '\''
            else:
                if namespace.obj is not None:
                    self.text = str(namespace.obj)
                else:
                    self.text = 'None'
        else:
            self.text = 'None'

    def to_string(self):
        return self.text


class NonPrimitiveNamespaceResult(NamespaceResult):
    def __init__(self, namespace, path):
        super(NonPrimitiveNamespaceResult, self).__init__(namespace)
        self.path = path

    def to_string(self):
        return 'NonPrimitiveNamespaceResult'


class Text(Marker):
    def __init__(self, string):
        self.obj = "'" + string + "'"
        self.text = string

    def to_string(self):
        return self.obj


class TextResult(Marker):
    def __init__(self, string):
        self.obj = string
        self.text = string

    def to_string(self):
        return str(self.text)


class Array(Marker):
    def __init__(self, l, string):
        self.obj = l
        self.text = string

    def to_string(self):
        return self.text


class FloatNumber(Marker):
    def __init__(self, num):
        self.obj = float(num)
        self.text = num

    def to_string(self):
        return self.text


class Number(Marker):
    def __init__(self, num):
        self.obj = int(num)
        self.text = num

    def to_string(self):
        return str(self.obj)


class Char(Marker):
    def __init__(self, char):
        self.obj = char
        self.text = "'" + char + "'"

    def to_string(self):
        return self.obj


class Bool(Marker):
    def __init__(self, boolean):
        self.obj = (boolean == 'true') or (boolean == 'True')
        self.text = boolean

    def to_string(self):
        return str(self.obj)


class Undefined(Marker):
    def __init__(self):
        self.obj = None
        self.text = None

    @staticmethod
    def to_string():
        return 'None'


class Opt(Marker):
    def __init__(self, opt):
        self.opt = opt
        self.level = None

        opt_upper_case = opt.upper()

        for key, value in six.iteritems(ops):
            if key == opt_upper_case:
                self.opt = value
                break

        level = 0
        found = False

        for value in allLevels:
            for innerValue in value:
                if opt == innerValue:
                    self.level = level
                    found = True
                    break
            if found:
                break
            level += 1

        if not found:
            #TODO:: throw exception
            pass

    def execute_operation(self, a, b):
        if self.level == 3:
            if not isinstance(b, Array):
                return Bool('False')

            for e in b.obj:
                if e.text == a.text and e.obj == a.obj:
                    return Bool('True')

            return Bool('False')
        else:
            operation = a.to_string() + self.opt + b.to_string()
            try:
                result = eval(operation)
            except TypeError as e:
                raise RookExceptionEvaluationFailed(str(e))

            if isinstance(result, bool):
                if not result:
                    if isinstance(a, NonPrimitiveNamespaceResult):
                        if not isinstance(b, Undefined):
                            raise RookNonPrimitiveObjectType(a.path)
                    if isinstance(b, NonPrimitiveNamespaceResult):
                        if not isinstance(a, Undefined):
                            raise RookNonPrimitiveObjectType(b.path)
                return Bool(str(result))

            if isinstance(result, six.integer_types):
                return Number(str(result))

            return TextResult(result)


class Actions(object):
    def __init__(self, namespace):
        self.namespace = None
        self.operations = []
        self.namespace = namespace

    @staticmethod
    def make_lookup_operation(input, start, end, elements):
        return LookupOperation(input[start + 1:end - 1])

    @staticmethod
    def make_function_operation(input, start, end, elements):
        # To build the function name, we will merge the unicode_set and all the unicode_set_with_numbers
        # To build the args we will simply read the atom at index 3
        #   which can be result of another operation; thus checking for exception
        # For further explanation, check ArithmeticPath.peg

        function_name = elements[0].text + elements[1].text

        if isinstance(elements[3], ToolException):
            return elements[3]

        args = elements[3].text
        return FunctionOperation(function_name, args)

    @staticmethod
    def make_function_operation_access(input, start, end, elements):
        # To build the function name, we will merge the unicode_set and all the unicode_set_with_numbers
        # To build the args we will simply read the atom at index 4
        #   which can be result of another operation; thus checking for exception
        # For further explanation, check ArithmeticPath.peg

        function_name = elements[1].text + elements[2].text

        if isinstance(elements[4], ToolException):
            return elements[4]

        args = elements[4].text
        return FunctionOperation(function_name, args)

    @staticmethod
    def make_attribute_operation(input, start, end, elements):
        return AttributeOperation(input[start + 1:end])

    @staticmethod
    def make_attribute(input, start, end, elements):
        return AttributeOperation(input[start:end])

    def make_and_execute_namespace_operation(self, input, start, end, elements):
        # Element 1 will not be null
        # Element 2 is a list of another elements (can be empty)
        # element1.(element2.element3.element4)
        # For further explanation, check ArithmeticPath.peg

        try:
            self.operations = []
            self.operations.append(elements[1])

            for e in elements[2].elements:
                self.operations.append(e)

            # Check if we have some exceptions in the operations chain - might happen if function parsing failed.
            for op in self.operations:
                if isinstance(op, ToolException):
                    return op

            result = elements[1].read(self.namespace, False)
            for e in elements[2].elements:
                result = e.read(result, False)

            if isinstance(result, PythonObjectNamespace) and result.obj and not isinstance(result.obj, PRIMITIVE_VALUES):
                # returning this class that mark its non primitive for additional information
                # this will help us in case of non True result when comparing this object
                return NonPrimitiveNamespaceResult(result, input[start:end])

            return NamespaceResult(result)
        except Exception as e:
            return ToolException(e)

    @staticmethod
    def make_comp_exp_ex(input, start, end, elements):
        # Element 2 is the actual expression
        # For further explanation, check ArithmeticPath.peg
        return elements[2]

    @staticmethod
    def make_comp_exp(input, start, end, elements):
        # We can assume the following: atom ( opt_ atom )*
        # the first (which must be) will be simple atom
        # the second and so forth will always be pair <Opt, Atom>
        # Its important to remember that this execution will handle the inner brackets if exist
        # In order to handle priority (which i could not figure out if available with canopy library):
        # 1. lets make the tree flat
        # 2. handle priority ourselves - (atom opt1 atom) will be handled before (atom opt2 atom)
        #   and will return TreeNode with result
        # For further explanation, check ArithmeticPath.peg

        # handle case the size is 1
        if len(elements[1].elements) == 0:
            return elements[0]

        if isinstance(elements[0], ToolException):
            return elements[0]

        flat_elements = [elements[0]]
        for n in elements[1].elements:
            flat_elements.append(n.elements[0])

            if isinstance(n.elements[1], ToolException):
                return n.elements[1]
            flat_elements.append(n.elements[1])

        while len(flat_elements) > 1:
            stop = False
            for level in range(len(allLevels)):
                for i in range(1, len(flat_elements), 2):
                    current_opt = flat_elements[i]
                    if current_opt.level == level:
                        result = current_opt.execute_operation(flat_elements[i - 1], flat_elements[i + 1])
                        flat_elements = flat_elements[:i - 1] + [result] + flat_elements[i + 2:]
                        stop = True
                        break
                if stop:
                    break

        return flat_elements[0]

    @staticmethod
    def make_opt(input, start, end, elements):
        return Opt(elements[1].text)

    @staticmethod
    def make_apostrophe_string(input, start, end, elements):
        return Text(elements[2].text)

    @staticmethod
    def make_string(input, start, end, elements):
        return Text(elements[2].text)

    @staticmethod
    def make_list(input, start, end, elements):
        tree_flatter = TreeFlatter()
        result = tree_flatter.flat_tree(elements[3])
        return Array(result, input[start:end])

    @staticmethod
    def make_float(input, start, end, elements):
        return FloatNumber(input[start:end].replace(' ', ''))

    @staticmethod
    def make_number(input, start, end, elements):
        return Number(input[start:end].replace(' ', ''))

    @staticmethod
    def make_char(input, start, end, elements):
        return Char(input[start:end].replace(' ', ''))

    @staticmethod
    def make_bool(input, start, end, elements):
        return Bool(input[start:end].replace(' ', ''))

    @staticmethod
    def make_null(input, start, end, elements):
        return Undefined()

    @staticmethod
    def make_undefined(input, start, end, elements):
        return Undefined()


class TreeFlatter(object):
    def __init__(self):
        self.flatted_tree = []

    def flat_tree(self, element):
        if isinstance(element, Marker):
            self.flatted_tree.append(element)

        for e in element.elements:
            if isinstance(e, Marker):
                self.flatted_tree.append(e)
            else:
                self.flat_tree(e)

        return self.flatted_tree


class ArithmeticPath(object):
    NAME = 'calc'

    def __init__(self, configuration, factory=None):
        if isinstance(configuration, six.string_types):
            string = configuration
        else:
            string = configuration['path']

        self.expression = string
        if self.expression == "":
            raise RookInvalidArithmeticPath(self.expression)

    def read_from(self, root_namespace):
        context = Actions(root_namespace)

        try:
            result = parse(self.expression, actions=context)
        except ParseError as e:
            raise RookInvalidArithmeticPath(self.expression, e)
        return self.normalize_result(result)

    def write_to(self, root_namespace, value):
        context = Actions(root_namespace)

        try:
            # initialize operations chain - by parsing the expression - ignore return value
            parse(self.expression, actions=context)
        except ParseError as e:
            raise RookInvalidArithmeticPath(self.expression, e)

        # execute the operation chain.
        size = len(context.operations)
        if size == 0:
            raise RookInvalidArithmeticPath(self.expression)

        i = 0
        namespace = root_namespace
        for _ in range(i, size - 1):
            namespace = context.operations[i].read(namespace, True)
            i += 1

        context.operations[i].write(namespace, value)

    @staticmethod
    def normalize_result(result):
        if isinstance(result, Array):
            new_arr = []
            for e in result.obj:
                new_arr.append(e.obj)
            return PythonObjectNamespace(new_arr)

        if isinstance(result, NamespaceResult):
            return result.obj

        if isinstance(result, ToolException):
            raise result.obj

        if isinstance(result, NonPrimitiveNamespaceResult):
            raise result.obj

        return PythonObjectNamespace(result.obj)
