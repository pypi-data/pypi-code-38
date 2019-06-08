from ctypes import cdll
from epics.ca import find_libca
dllname = find_libca()

print(dllname)

libca = cdll.LoadLibrary(dllname)
print("{:20s} {:s} {:s}".format('function name', 'in libca' , 'in None'))

for fname in ('ca_context_create', 'ca_pend_io',
                  'ca_create_channel'):

    print("{:20s}  {:s}     {:s}".format(fname,
                                         repr(hasattr(libca, fname)),
                                         repr(hasattr(cdll.LoadLibrary(None), fname))))

#
# False
# >>> libca.ca_context_create
# <_FuncPtr object at 0x109536c00>
# >>> hasattr(cdll.LoadLibrary(None), 'sqrt')
# True
# >>> libc = cdll.LoadLibrary('libc')
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/Users/Newville/anaconda3/lib/python3.7/ctypes/__init__.py", line 434, in LoadLibrary
#     return self._dlltype(name)
#   File "/Users/Newville/anaconda3/lib/python3.7/ctypes/__init__.py", line 356, in __init__
#     self._handle = _dlopen(self._name, mode)
# OSError: dlopen(libc, 6): image not found
# >>> libc = cdll.LoadLibrary('libc.dylib')
# >>> hasattr(cdll.LoadLibrary(None), 'sqrt')
# True
# >>> libca.ca_context_create
# <_FuncPtr object at 0x109536c00>
# >>> hasattr(cdll.LoadLibrary(None), 'ca_context_create')
# False
# >>> hasattr(cdll.LoadLibrary(None), 'ca_pend_io')
# False
# >>> hasattr(cdll.LoadLibrary(None), 'ca_pend_event')
# False
# >>> libca.ca_pend_event
# <_FuncPtr object at 0x109536e58>
# >>>
