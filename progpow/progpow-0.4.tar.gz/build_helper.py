from cffi import FFI
import os
from os import path
import errno
import subprocess
import glob

versions = ['0_9_2', '0_9_3']

def absolute(*paths):
    op = os.path
    return op.realpath(op.abspath(op.join(op.dirname(__file__), *paths)))

base_dir = absolute(path.dirname(__file__))
build_temp = path.join(base_dir, 'build')

try:
  os.makedirs(build_temp)
except OSError as e:
  if e.errno != errno.EEXIST:
    raise

def ensure_dir(path):
  if not os.path.exists(path): 
        os.makedirs(self.path)

def has_system_lib():
    ffi = FFI()
    try:
        for v in versions:
          ffi.dlopen("progpow%s"%v)
        return True
    except OSError:
        if 'LIB_DIR' in os.environ:
            for path in glob.glob(path.join(os.environ['LIB_DIR'], "*progpow*")):
                try:
                    FFI().dlopen(path)
                    return True
                except OSError:
                    pass
        return False

def has_local_lib():
  for v in versions:
    if not path.exists(path.join(base_dir, 'libprogpow%s.so'%v)):
      return False
  return True

def build_clib():  
    for v in versions:  
      c_lib_dir = path.join(base_dir, "c_lib"+v)
      c_files, cpp_files = glob.glob(path.join(c_lib_dir, '*.c')), glob.glob(path.join(c_lib_dir, '*.cpp'))
      subprocess.check_call(["gcc", '-fPIC', '-c',] + c_files, cwd=build_temp)
      subprocess.check_call(["g++", '-fPIC', '-c', '-std=c++11'] + cpp_files, cwd=build_temp)
      subprocess.check_call(["g++", '-fPIC', '-shared', '-std=c++11'] + glob.glob(path.join(build_temp, '*.o')) + [ '-o', 'libprogpow%s.so'%v], cwd=build_temp)
      subprocess.check_call(["cp", 'libprogpow%s.so'%v, base_dir], cwd=build_temp)
      subprocess.check_call(["rm"]+glob.glob(path.join(build_temp, '*.o')), cwd=build_temp)


def install():
    place = None
    if 'LIB_DIR' in os.environ:
      lib_dir =os.environ['LIB_DIR'] 
      if len(lib_dir):
        place = lib_dir.split(";")[0]
    if not place:
      place = '/usr/local/lib/' #TODO win and mac
    ensure_dir(place)
    for v in versions:
      try:
        subprocess.check_call(["cp", 'libprogpow%s.so'%v, place], cwd=base_dir)
      except: #CalledProcessError TODO
        subprocess.check_call(['sudo', "cp", 'libprogpow%s.so'%v, place], cwd=base_dir)
      

def ensure_local():
  if not has_local_lib():
    build_clib()

def ensure_system():
  if not has_system_lib():
    ensure_local()
    install()



