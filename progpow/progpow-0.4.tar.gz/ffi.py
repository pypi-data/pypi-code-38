from cffi import FFI
from build_helper import absolute, ensure_system
ensure_system()

#0.9.2
ffi0_9_2 = FFI()
with open("include/progpow.h", 'rt') as h:
    ffi0_9_2.cdef(h.read())
include_path = absolute("include/")
ffi0_9_2.set_source("_libprogpow0_9_2", r'#include "progpow.h"', include_dirs = [include_path], libraries = ['progpow0_9_2'])

ffi0_9_2.compile()


#0.9.3
ffi0_9_3 = FFI()
with open("include/progpow.h", 'rt') as h:
    ffi0_9_3.cdef(h.read())
include_path = absolute("include/")
ffi0_9_3.set_source("_libprogpow0_9_3", r'#include "progpow.h"', include_dirs = [include_path], libraries = ['progpow0_9_3'])

ffi0_9_3.compile()
