import re
import time
import random
import sys
import socket
import traceback as tback
import threading

from . import parsing
from . import specs


class FreRuntimeError(BaseException):
    pass

class FreMissingError(FreRuntimeError):
    pass

class FreSocketError(FreRuntimeError):
    pass

class FreNameError(FreRuntimeError):
    pass

class FreTypeError(FreRuntimeError):
    pass

class FreValueError(FreRuntimeError):
    pass


class FreVariable(object):
    def __init__(self, env, kind, name, value = None):
        self.env = env # can be either a FreVM or FreEnvironment object

        self.kind = kind
        self.name = name

        if not isinstance(kind, specs.LanguageType):
            raise TypeError("{} is not a fre.specs.LanguageType subclass!".format(type(kind)))

        self.set(value)

        env.variables[name] = self

    def set(self, value):
        if value is None:
            value = self.kind.default_value

        elif not self.kind.check(value):
            raise FreTypeError("{} is not a {}-like value!".format(repr(value), str(self.kind)))

        self.value = self.kind.autocast(value)

    def pointer_level(self):
        return 0

    def get(self):
        return self.value

    def _fre_deref(self):
        if not isinstance(self.kind, specs.PointerType):
            raise FreTypeError("{} can't be dereferenced!".format(self.kind))

        return self.value._fre_deref()

    def pointer(self):
        return FrePointer(self.env, self.kind, self.name, self)

class FreConstant(FreVariable):
    def __init__(self, env, kind, name, value = None):
        self.env = env # can be either a FreVM or FreEnvironment object

        self.kind = kind
        self.name = name

        if not isinstance(kind, specs.LanguageType):
            raise TypeError("{} is not a fre.specs.LanguageType subclass!".format(type(kind)))

        assert self.kind.check(value)
        self.value = value

        env.variables[name] = self

    def set(self, value):
        raise FreRuntimeError("Cannot set a constant variable ({})!".format(self.name))

class FrePointer(object):
    def __init__(self, env, kind, name, var = None):
        self.env = env # can be either a FreVM or FreEnvironment object

        self.kind = kind
        self.name = name

        if not isinstance(kind, specs.LanguageType):
            raise FreTypeError("{} is not a fre.specs.LanguageType subclass".format(type(kind)))

        self.set(var)

        env.variables[name] = self

    def set(self, var):
        if var is None:
            self.value = None

        elif hash(var.kind) != hash(self.kind):
            raise FreTypeError("Pointer assignment mismatch: expected {}*, got {}*".format(str(self.kind), str(var.kind)))

        self.value = var

    def pointer_level(self):
        return self.value.pointer_level() + 1

    def get(self):
        return self

    def _fre_deref(self):
        if self.value is None:
            raise FreValueError("{} is a null pointer".format(self.name))

        else:
            return self.value

class FreFunction(object):
    def __init__(self, env, name, return_kind, arg_typenames, body):
        self.env = env
        self._parser = None

        self.name = name
        self.return_kind = return_kind
        self.arg_typenames = list(arg_typenames)
        self.body = body

        if not isinstance(return_kind, specs.LanguageType):
            raise TypeError("{} is not a fre.specs.LanguageType subclass".format(type(return_kind)))

    def get(self):
        return self

    def call(self, caller, call_env, traceback, args, parser = None):
        call_env.bind(self.env)
        return call_env.execute([self.body], traceback, parser)

    def __mul__(self, num):
        return FreRepeatFunction(self, num)

class FreNativeFunction(FreFunction):
    def __init__(self, env, name, return_kind, arg_typenames):
        self.env = env
        self._parser = None

        self.name = name
        self.return_kind = return_kind
        self.arg_typenames = list(arg_typenames)

        if not isinstance(return_kind, specs.LanguageType):
            raise TypeError("{} is not a fre.specs.LanguageType subclass!".format(type(return_kind)))

    def call(self, caller, call, traceback, args):
        pass

    def __mul__(self, n):
        return FreRepeatFunction(self, n)

class FreRepeatFunction(FreNativeFunction):
    def __init__(self, func, times):
        self.env = func.env

        self.name = func.name + '(*{})'.format(times)
        self.return_kind = func.return_kind
        self.arg_typenames = list(func.arg_typenames)

        self.func = func
        self.times = times

        if not isinstance(func.return_kind, specs.LanguageType):
            raise TypeError("{} is not a fre.specs.LanguageType subclass!".format(type(return_kind)))

    def call(self, caller, call, traceback, args):
        res = None

        for _ in range(self.times):
            res = self.func.call(caller, call, traceback, args)

        return res

    def __mul__(self, n):
        return FreRepeatFunction(self.func, times * n)

#====================
#  NATIVE FUNCTIONS 
#====================

class FreNativeSuite(object):
    operations = []
    constants = {}

    @classmethod
    def register(cls, env):
        for op in cls.operations:
            env.variables[op.fname] = op(env, op.fname, op.rtype, op.atype)

        for cname, (ckind, cval) in cls.constants:
            FreConstant(env, ckind, cname, cval)

# General
class FrePrintFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        sys.stdout.write(str(args[0]))

class FreExitFunction(FreNativeFunction):
    def exit(self, caller, call, traceback, args):
        exit(0)

# Arrays
class FreInsertFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        (array, index, item) = args

        array.insert(index, item)
        return item

class FreAppendFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        i = len(array)

        array.append(args[1])

        return i

class FreConcatFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        return list(args[0]) + list(args[1])

class FrePopFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        return array.pop()

class FreShiftFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        return array.pop(0)

class FreUnshiftFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        return array.insert(0, args[1])

class FreArrayGetFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        return array[args[1]]

class FreArraySetFunction(FreNativeFunction):
    def call(self, caller, call, traceback, args):
        array = args[0]
        array[args[1]] = args[2]
        return args[2]

# Time

class FreTime(FreNativeSuite):
    class Timestamp(FreNativeFunction):
        fname = 'time:stamp'

        atype = []
        rtype = specs.FloatType()

        def call(self, *args):
            return time.time()

    class Sleep(FreNativeFunction):
        fname = 'time:sleep'

        atype = [(specs.FloatType(), 'seconds')]
        rtype = specs.VoidType()

        def call(self, _, _1, _2, args):
            time.sleep(args[0])

    class Format(FreNativeFunction):
        fname = 'time:format'

        atype = [
            (specs.StringType(), 'format') # format
        ]
        rtype = specs.StringType()

        def call(self, _, _1, _2, args):
            return time.strftime(args[0])

    operations = [
        Timestamp, Format, Sleep
    ]

# Random

class FreRandom(FreNativeSuite):
    rng = random.Random()
    rng.seed(time.time())

    class Integer(FreNativeFunction):
        fname = 'random:int'

        atype = [
            (specs.IntType(), 'min'), # smallest value (inclusive)
            (specs.IntType(), 'max'), # largest value (inclusive)
        ]
        rtype = specs.IntType()

        def call(self, caller, call, traceback, args):
            return FreRandom.rng.randint(args[0], args[1])

    class Uniform(FreNativeFunction):
        fname = 'random:uniform'

        atype = [
            (specs.FloatType(), 'min'), # smallest value
            (specs.FloatType(), 'max'), # largest value
        ]
        rtype = specs.FloatType()

        def call(self, caller, call, traceback, args):
            return FreRandom.rng.uniform(args[0], args[1])

    class Gaussian(FreNativeFunction):
        fname = 'random:gaussian'

        atype = [
            (specs.FloatType(), 'min'), # smallest value
            (specs.FloatType(), 'max'), # largest value
        ]
        rtype = specs.FloatType()

        def call(self, caller, call, traceback, args):
            return FreRandom.rng.gauss(args[0], args[1])

    class Seed(FreNativeFunction):
        fname = 'random:seed'

        atype = [
            (specs.IntType(), 'seed') # seed
        ]
        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            FreRandom.rng.seed(args[0])

    operations = [
        Integer, Uniform, Gaussian,
        Seed
    ]

# Strings

class FreStringUtils(FreNativeSuite):
    class Format(FreNativeFunction):
        fname = 'str:format'
        
        atype = [
            (specs.StringType(), 'format'), # to format
            (specs.ArrayType(specs.AnyType()), 'params') # format parameters
        ]

        rtype = specs.StringType() # formatted

        def call(self, caller, call, traceback, args):
            return args[0].format(*args[1])

    class Slice(FreNativeFunction):
        fname = 'str:slice'
        
        atype = [
            (specs.StringType(), 'source'), # to slice
            (specs.IntType(), 'from'), # index 1
            (specs.IntType(), 'to'), # index 2
        ]

        rtype = specs.StringType() # sliced

        def call(self, caller, call, traceback, args):
            return args[0][args[1]:args[2]]

    class SliceFrom(FreNativeFunction):
        fname = 'str:sliceFrom'
        
        atype = [
            (specs.StringType(), 'source'), # to slice
            (specs.IntType(), 'from'), # index 1
        ]

        rtype = specs.StringType() # sliced

        def call(self, caller, call, traceback, args):
            return args[0][args[1]:]

    class SliceTo(FreNativeFunction):
        fname = 'str:sliceTo'
        
        atype = [
            (specs.StringType(), 'source'), # to slice
            (specs.IntType(), 'to'), # index 2
        ]

        rtype = specs.StringType() # sliced

        def call(self, caller, call, traceback, args):
            return args[0][:args[1]]

    class CharAt(FreNativeFunction):
        fname = 'str:charAt'

        atype = [
            (specs.StringType(), 'source'),
            (specs.IntType(), 'index'),
        ]

        rtype = specs.StringType() # char

        def call(self, caller, call, traceback, args):
            return args[0][args[1]]

    class SetChar(FreNativeFunction):
        fname = 'str:setChar'

        atype = [
            (specs.StringType(), 'target'),
            (specs.IntType(), 'index'), # index
            (specs.StringType(), 'char') # new char
        ]

        rtype = specs.StringType() # with set char

        def call(self, caller, call, traceback, args):
            a = args[0]
            a[args[1]] = args[2][0]
            return a

    class Replace(FreNativeFunction):
        fname = 'str:replace'

        atype = [
            (specs.StringType(), 'source'), # source string
            (specs.StringType(), 'from'), # replace this
            (specs.StringType(), 'to') # by this
        ]

        rtype = specs.StringType() # after replacing

        def call(self, caller, call, traceback, args):
            return args[0].replace(args[1], args[2])

    operations = [
        Format,
        SliceFrom, SliceTo, Slice,
        CharAt, SetChar, Replace
    ]

# Threading

class FreThreads(FreNativeSuite):
    threads = {}
    handle_count = 0

    def regthread(th):
        ind = FreThreads.handle_count
        FreThreads.handle_count += 1

        FreThreads.threads[ind] = th

        return ind

    def _target(source, fre_func, call_env, arg):
        fre_func.call(None, call_env, [('thread start', None, None)], [arg], source._parser)

    class Run(FreNativeFunction):
        fname = 'thread:run'
        
        atype = [
            (specs.FunctionType([], specs.VoidType()), 'target'), # function to be threaded
        ]

        rtype = specs.IntType() # thread handle

        def call(self, caller, call, traceback, args):
            th = threading.Thread(target=FreThreads._target, args=(self, args[0], call, None))
            th.start()

            return FreThreads.regthread(th)

    class RunWith(FreNativeFunction):
        fname = 'thread:runWith'
        
        atype = [
            (specs.FunctionType([specs.AnyType()], specs.VoidType()), 'target'), # function to be threaded
            (specs.AnyType(), 'arg'), # sole argument (may be null)
        ]

        rtype = specs.IntType() # thread handle

        def call(self, caller, call, traceback, args):
            th = threading.Thread(target=FreThreads._target, args=(self, args[0], call, args[1]))
            th.start()

            return FreThreads.regthread(th)

    class Join(FreNativeFunction):
        fname = 'thread:join'

        atype = [
            (specs.IntType(), 'handle') # thread handle
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreThreads.threads:
                raise FreMissingError("No such thread with handle {}!".format(ind))

            th = FreThreads.threads[ind]
            th.join()

    operations = [
        Run, RunWith,
        Join,
    ]

# Networking

class FreSocket(FreNativeSuite):
    sockets = {}
    addresses = {}
    handle_count = 0
    modes = [socket.SOCK_STREAM, socket.SOCK_DGRAM]

    class Open(FreNativeFunction):
        fname = 'socket:open'

        atype = [
            (specs.IntType(), "mode"), # SOCK_TCP or SOCK_UDP
        ]

        rtype = specs.IntType() # socket handle

        def call(self, caller, call, traceback, args):
            sock = socket.socket(socket.AF_INET, FreSocket.modes[args[0]])
            return FreSocket.regsock(sock, None)

    class Close(FreNativeFunction):
        fname = 'socket:close'
        
        atype = [
            (specs.IntType(), "socket"), # socket handle
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]
            sock.close()

            del FreSocket.sockets[ind]

            if ind in FreSocket.addresses:
                del FreSocket.addresses[ind]

    class Connect(FreNativeFunction):
        fname = 'socket:connect'

        atype = [
            (specs.IntType(), "socket") , # socket handle
            (specs.StringType(), "host"), # 1st part of AF_INET address
            (specs.IntType(), "port"),    # 2nd part of AF_INET address
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                sock.connect((args[1], args[2]))

            except socket.error as err:
                raise FreSocketError(str(err))

    class Send(FreNativeFunction):
        fname = 'socket:send'

        atype = [
            (specs.IntType(), "socket") , # socket handle
            (specs.StringType(), "data"),
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            msg = args[1]

            if isinstance(msg, str):
                msg = msg.encode('utf-8')

            try:
                sock.sendall(msg)

            except socket.error as err:
                raise FreSocketError(str(err))

    class ReceiveTCP(FreNativeFunction):
        fname = 'socket:receive'

        atype = [
            (specs.IntType(), "socket"),  # socket handle
            (specs.IntType(), "max_size"),
        ]

        rtype = specs.StringType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                return sock.recv(args[1]).decode('utf-8')

            except socket.error as err:
                raise FreSocketError(str(err))

    class ReceiveUDP(FreNativeFunction):
        fname = 'socket:receiveFrom'

        atype = [
            (specs.IntType(), "socket"),  # socket handle
            (specs.IntType(), "max_size"),
        ]

        rtype = specs.ArrayType(specs.StringType()) # [address, data]

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                return sock.recvfrom(args[1]).decode('utf-8')

            except socket.error as err:
                raise FreSocketError(str(err))

    class Bind(FreNativeFunction):
        fname = 'socket:bind'

        atype = [
            (specs.IntType(), "socket"),  # socket handle
            (specs.StringType(), "host"), # 1st part of AF_INET address
            (specs.IntType(), "port"),    # 2nd part of AF_INET address
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                sock.bind((args[1], args[2]))

            except socket.error as err:
                raise FreSocketError(str(err))

    class Listen(FreNativeFunction):
        fname = 'socket:listen'

        atype = [
            (specs.IntType(), "socket"),  # socket handle
            (specs.IntType(), "listenLimit"),
        ]

        rtype = specs.VoidType()

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                sock.listen(args[1])

            except socket.error as err:
                raise FreSocketError(str(err))

    class Accept(FreNativeFunction):
        fname = 'socket:accept'

        atype = [
            (specs.IntType(), "socket")  # socket handle
        ]

        rtype = specs.IntType() # accepted handle

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            sock = FreSocket.sockets[ind]

            try:
                (conn, addr) = sock.accept()
                return FreSocket.regsock(conn, addr)

            except socket.error as err:
                raise FreSocketError(str(err))

    class GetHost(FreNativeFunction):
        fname = 'socket:getHost'

        atype = [
            (specs.IntType(), "socket")  # socket handle
        ]

        rtype = specs.StringType() # address

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}".format(ind))

            if ind not in FreSocket.addresses:
                raise FreMissingError("Can't retrieve the host of this socket")

            return FreSocket.addresses[ind][0]

    class GetPort(FreNativeFunction):
        fname = 'socket:getPort'

        atype = [
            (specs.IntType(), "socket")  # socket handle
        ]

        rtype = specs.IntType() # port

        def call(self, caller, call, traceback, args):
            ind = args[0]

            if ind not in FreSocket.sockets:
                raise FreMissingError("No socket under handle {}!".format(ind))

            if ind not in FreSocket.addresses:
                raise FreMissingError("Can't retrieve the port of this socket")

            return FreSocket.addresses[ind][1]

    @staticmethod
    def regsock(conn, addr):
        ind = FreSocket.handle_count
        FreSocket.handle_count += 1

        FreSocket.sockets[ind] = conn

        if addr:
            FreSocket.addresses[ind] = addr

        return ind

    operations = [
        Open, Close,
        Connect,
        Send, ReceiveTCP, ReceiveUDP,
        Bind, Listen, Accept,
        GetHost, GetPort
    ]

#===================


class FreEnvironment(object):
    def __init__(self, name, spec = None, parent = None):
        # (cetera)
        self.name = name
        self.parent = parent
        self.specs = spec or specs.FreSpecs()

        # Bindings
        self.variables = {}
        self.super_scopes = []

        if parent is None:
            self.init_native_functions()

        # Execution
        self.result = None

        self.return_stop = False
        self.continue_stop = False
        self.break_stop = False

        self._exec_level = 0
        self._parser = None

    def bind(self, super_scope):
        self.super_scopes.append(super_scope)

    def init_native_functions(self):
        self.variables['print'] = FrePrintFunction(self, 'print', specs.VoidType(), [(specs.AnyType(), 'x')])
        self.variables['exit'] = FreExitFunction(self, 'exit', specs.VoidType(), [])

        # Array Functions
        self.variables['array:concat'] = FreConcatFunction(self, 'array:concat', specs.ArrayType(specs.AnyType()), [(specs.ArrayType(specs.AnyType()), 'arr1'), (specs.ArrayType(specs.AnyType()), 'arr2')])

        self.variables['array:insert'] = FreInsertFunction(self, 'array:insert', specs.IntType(), [(specs.ArrayType(specs.AnyType()), 'arr'), (specs.IntType(), 'index'), (specs.AnyType(), 'item')])
        self.variables['array:append'] = FreAppendFunction(self, 'array:append', specs.IntType(), [(specs.ArrayType(specs.AnyType()), 'arr'), (specs.AnyType(), 'item')])
        self.variables['array:unshift'] = FreUnshiftFunction(self, 'array:unshift', specs.AnyType(), [(specs.ArrayType(specs.AnyType()), 'arr'), (specs.AnyType(), 'item')])
        
        self.variables['array:pop'] = FrePopFunction(self, 'array:pop', specs.AnyType(), [(specs.ArrayType(specs.AnyType()), 'arr')])
        self.variables['array:shift'] = FreShiftFunction(self, 'array:shift', specs.AnyType(), [(specs.ArrayType(specs.AnyType()), 'arr')])

        self.variables['array:get'] = FreArrayGetFunction(self, 'array:get', specs.AnyType(), [(specs.ArrayType(specs.AnyType()), 'arr'), (specs.IntType(), 'index')])
        self.variables['array:set'] = FreArraySetFunction(self, 'array:set', specs.AnyType(), [(specs.ArrayType(specs.AnyType()), 'arr'), (specs.IntType(), 'index'), (specs.AnyType(), 'value')])

        # Socket Constants
        self.add_constant('SOCK_TCP', specs.IntType(), 0)
        self.add_constant('SOCK_UDP', specs.IntType(), 1)

        FreSocket.register(self)
        FreThreads.register(self)
        FreStringUtils.register(self)
        FreTime.register(self)
        FreRandom.register(self)

    def add_constant(self, name, kind, value):
        FreConstant(self, kind, name, value)

    def parse_type(self, name):
        if name == '':
            return specs.VoidType()

        elif name[-1] == '*':
            return specs.PointerType(self.parse_type(name[:-1]))

        elif name[-1] == '%':
            return specs.ArrayType(self.parse_type(name[:-1]))

        elif re.match(r'.+?\(.*?\)', name):
            m = re.match(r'(.+?)\((.*?)\)', name)

            return_type = m.group(1)
            arg_types = [x for x in m.group(2).split(',') if x]
            
            return specs.FunctionType([self.parse_type(a) for a in arg_types], self.parse_type(return_type))

        else:
            return self.specs.find_type(name)()

    def find_variable(self, name):
        if name in self.variables:
            return self.variables[name]

        else:
            for s in [self.parent, *self.super_scopes]:
                if not s:
                    continue

                try:
                    return s.find_variable(name)

                except FreNameError:
                    continue

            raise FreNameError("Variable {} not found in the Fre environment!".format(name))

    def evaluate(self, node, traceback = None):
        if not traceback:
            traceback = []

        if not node:
            return None

        if node.node_type == 'expr.funcall':
            func = self.find_variable(node.value)

            if func is None:
                return None

            if isinstance(func, FreVariable):
                if isinstance(func.kind, specs.FunctionType):
                    n = func.name
                    func = func.value

                    if func is None:
                        raise FreTypeError("{} is null".format(n))

                else:
                    raise FreTypeError("{} is not a function variable".format(func.name))

            call = FreEnvironment('call to {}'.format(func.name), self.specs, self)
            args = []

            for c in node.children:
                args.append(self.evaluate(c, traceback))

            for i, ((argt, argn), argv) in enumerate(zip(func.arg_typenames, args)):
                if not argt.check(argv):
                    raise FreTypeError("Function {} argument #{} type mismatch: expected {}-like value, got {}".format(func.name, i, argt, type(argv).__name__))
                FreVariable(call, argt, argn, argv)

            func._parser = self._parser

            res = func.call(self, call, traceback, args)
            return res

        elif node.node_type.startswith('expr.literal.'):
            return node.value

        elif node.node_type == 'expr.identifier':
            vname, vmods = node.value
            var = self.find_variable(vname)

            for m in vmods:
                if m == '*':
                    var = var._fre_deref()

                elif m == '@':
                    var = FrePointer(self, var.kind, var.name + '*', var)

            return var.get()

        elif node.node_type == 'expr.oper':
            operator = node.value
            operands = [self.evaluate(n, traceback) for n in node.children]

            if operator == '+':
                res = operands[0]

                for o in operands[1:]:
                    if isinstance(o, str) or isinstance(res, str):
                        res = str(res) + str(o)

                    else:
                        res += o

                return res

            elif operator == '-':
                res = operands[0]

                for o in operands[1:]:
                    res -= o

                return res

            elif operator == '*':
                res = operands[0]

                for o in operands[1:]:
                    res *= o

                return res

            elif operator == '/':
                res = operands[0]

                for o in operands[1:]:
                    res /= o

                return res

            elif operator == '==':
                res = operands[0]

                for o in operands[1:]:
                    if o != res:
                        return False

                return True

            elif operator == '!=':
                res = operands[0]

                for o in operands[1:]:
                    if o != res:
                        return True

                return False

            elif operator == '&':
                res = operands[0]

                for o in operands[1:]:
                    res &= o

                return res

            elif operator == '|':
                res = operands[0]

                for o in operands[1:]:
                    res |= o

                return res

            elif operator == '^':
                res = operands[0]

                for o in operands[1:]:
                    res ^= o

                return res

            elif operator == '<<':
                res = operands[0]

                for o in operands[1:]:
                    res <<= o

                return res

            elif operator == '>>':
                res = operands[0]

                for o in operands[1:]:
                    res >>= o

                return res

            elif operator == '~':
                return ~operands[0]

            elif operator == '!':
                return not operands[0]

            elif operator == '&&':
                res = True
                
                for o in operands:
                    res = res and o

                return res

            elif operator == '||':
                res = False
                
                for o in operands:
                    res = res or o

                return res

            elif operator == '^^':
                res = False
                
                for o in operands:
                    res = bool(res) != bool(o)

                return res

            elif operator == '<':
                last = operands[0]

                for o in operands[1:]:
                    if o <= last:
                        return False

                    last = o

                return True

            elif operator == '>':
                last = operands[0]

                for o in operands[1:]:
                    if o >= last:
                        return False

                    last = o

                return True

            elif operator == '<=':
                last = operands[0]

                for o in operands[1:]:
                    if o < last:
                        return False

                    last = o

                return True

            elif operator == '>=':
                last = operands[0]

                for o in operands[1:]:
                    if o > last:
                        return False

                    last = o

                return True

            else:
                raise FreRuntimeError("Unknown operator: {}".format(repr(operator)))

        elif node.node_type == 'expr.set':
            name, mods = node.value
            var = self.find_variable(name)

            for m in mods:
                if m == '*':
                    var = var._fre_deref()

            value = self.evaluate(node.body, traceback)
            var.set(value)
            
            return value

        elif node.node_type == 'expr.func':
            func = FreFunction(self, node.value, self.parse_type(node.body.value), [(self.parse_type(adef.body.value), adef.value) for adef in node.children[1:]], node.children[0])
            self.variables[node.value] = func
            return func

    def execute(self, nodes, traceback, parser = None):
        try:
            self._exec_level += 1

            for node in nodes:
                if not node:
                    continue

                traceback.append((self.name, node.line, node.column))

                try:
                    # Stoppers
                    if self.return_stop:
                        if self._exec_level == 1:
                            self.return_stop = False

                            r = self.result
                    
                            self._exec_level = 0
                            self.result = None

                            return self.result

                        else:
                            self._exec_level -= 1
                            return

                    elif self.continue_stop:
                        self.continue_stop = False
                        self._exec_level -= 1
                        return

                    elif self.break_stop:
                        self._exec_level -= 1
                        return

                    if not node:
                        continue

                    # Run the AST using a plain old elif chain
                    nt = node.node_type

                    if nt == 'vardef':
                        name, mods, value = node.value
                        #node.print_tree()
                        vtype = self.parse_type(node.body.value)
                        level = 0

                        for m in mods:
                            if m == '@':
                                level += 1

                        if level > 0:
                            target = self.find_variable(value)

                            if target.pointer_level() != level:
                                raise FreTypeError("Pointer level mismatch: Expected a {} type, got {}".format(vtype, target.kind + '*'))

                        else:
                            value = self.evaluate(value, traceback)
                            FreVariable(self, vtype, name, value)

                    elif nt == 'block':
                        traceback.pop()
                        self.execute(node.children, traceback)
                        traceback.append((self.name, node.line, node.column))

                    elif nt == 'logic.if':
                        (condition, otherwise) = node.children

                        if self.evaluate(condition, traceback):
                            self.execute([node.body], traceback)

                        elif otherwise:
                            self.execute([otherwise.body], traceback)

                    elif nt == 'logic.while':
                        (condition, otherwise) = node.children

                        if self.evaluate(condition, traceback):
                            while True:
                                self.execute([node.body], traceback)

                                if self.break_stop:
                                    self.break_stop = False
                                    break

                                elif not self.evaluate(condition, traceback):
                                    break

                        elif otherwise:
                            self.execute([otherwise.body], traceback)

                    elif nt == 'continue':
                        self.continue_stop = True

                    elif nt == 'break':
                        self.break_stop = True

                    elif nt == 'return':
                        self.return_stop = True

                        if node.body:
                            self.result = self.evaluate(node.body, traceback)

                    elif nt == 'pass':
                        continue

                    else:
                        self.evaluate(node, traceback)

                except BaseException as err:
                    raise

                else:
                    traceback.pop()
                
            r = self.result
            self._exec_level -= 1

            if self._exec_level == 0:
                self.result = None

            return r

        except BaseException as err:
            if parser:
                parser.error("({}) {}".format(type(err).__name__, str(err)))
                self.print_traceback(parser, traceback)

                if not isinstance(err, FreRuntimeError):
                    print('\nDetails:\n')
                    tback.print_exc()

            else:
                raise

    def print_traceback(self, parser, tb):
        for ind, (at, line, col) in list(enumerate(tb))[::-1]:
            if line:
                print('{}. [{}:{}] at {}:'.format(ind + 1, line, col, at))
                print('  ' + parser.lexer.input.get_line(line))
                print(' ' * (1 + col) + '^')

            else:
                print('{}. at {}'.format(ind + 1, at))

    def execute_code(self, s, tb = None):
        (parser, parse_iter) = parsing.FreParser.parse(s)
        self._parser = parser
        tb = tb or []

        return self.execute(parse_iter, tb, parser)