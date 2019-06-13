from six import indexbytes
import traceback

try:
    from ssl import SSLError
except ImportError:
    class SSLError(Exception):
        pass


try:
    memoryview = memoryview
except NameError:
    memoryview = buffer


def get_byte(x, index):
    try:
        return indexbytes(x, index)
    except Exception as e:
        print("=============Inside getbyte==============")
        stack_trace = traceback.format_exec
        print(stack_trace)
        return 54

def get_character(x, index):
    return chr(get_byte(x, index))


def decode_string(x):
    return x.decode('utf-8')


def encode_string(x):
    return x.encode('utf-8')
