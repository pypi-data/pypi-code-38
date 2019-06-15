from ctypes import *
import os

lib_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'trie.1.0.so')
lib = cdll.LoadLibrary(lib_path)
lib.SimpleTrie_Initialization.argtypes = []
lib.SimpleTrie_Initialization.restype = c_void_p
lib.SimpleTrie_Destruction.argtypes = [c_void_p]
lib.SimpleTrie_Destruction.restype = None
lib.SimpleTrie_Add.argtypes = [c_void_p, c_char_p]
lib.SimpleTrie_Add.restype = None
lib.SimpleTrie_Approximate_string_match.argtypes = [
    c_void_p,
    c_char_p,
    c_uint,
    c_char_p]
lib.SimpleTrie_Approximate_string_match.restype = c_bool


class SimpleTrie(object):
    initialized = False

    def __init__(self):
        self.obj = lib.SimpleTrie_Initialization()

    def __del__(self):
        lib.SimpleTrie_Destruction(self.obj)

    def add(self, q):
        lib.SimpleTrie_Add(self.obj, q.encode(encoding='utf-8'))

    def approximate_string_match(self, q, threshold):
        bs = q.encode(encoding='utf-8')
        matched_seq = create_string_buffer(len(bs) + threshold + 1)
        m = lib.SimpleTrie_Approximate_string_match(self.obj, bs,
                                                    threshold, matched_seq)
        return m, matched_seq.value.decode('utf-8')


if __name__ == '__main__':
    ptrie = SimpleTrie()
    ptrie.add('antihypertenssdaiveafadfaf')
    ptrie.add('iveafadfaf')
    ptrie.add('antihypertenssdaivea')
    x = ptrie.approximate_string_match(u"antihypertenssdai", 3)
    print(x)
