from ctypes import cdll
from epics.ca import find_libca
dllname = find_libca()

print(dllname)

libca = cdll.LoadLibrary(dllname)

print(hasattr(libca, 'ca_context_create'),
      hasattr(cdll.LoadLibrary(None), 'ca_context_create'))
