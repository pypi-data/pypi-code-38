from ctypes import cdll, c_char, c_size_t
from os import path

PATH = path.join(path.dirname(__file__),"./lnumber.so")
print PATH
lib = cdll.LoadLibrary(PATH)

def lnumber(graph, verts):
  global lib
  return lib.laman_number(str(graph).encode("utf-8"), c_size_t(verts))

#print lnumber(252590061719913632,12)
