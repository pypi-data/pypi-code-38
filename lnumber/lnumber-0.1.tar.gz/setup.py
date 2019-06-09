from setuptools import setup, Extension #Extension costum gcc compiles library
from setuptools.command.build_ext import build_ext
#from setuptools.command.install import install
import subprocess
import os

def rem_opt(l,keys):
  return [y for y in l if y not in keys]

class BuildExt(build_ext):
  def build_extensions(self):
    keys = ["-Wstrict-prototypes","-fwrapv","-g","-O1","-O2","-fstack-protector-strong","-fno-strict-aliasing"]
    self.compiler.compiler_so = rem_opt(self.compiler.compiler_so,keys)
    build_ext.build_extensions(self)

os.environ["CC"] = "gcc"
os.environ["CXX"] = "gcc"

module = Extension('lnumber.lnumber',
  sources = ['lnumber/src/laman_number.cpp','lnumber/src/lib.cpp'],
  include_dirs = ['lnumber/inc','lnumber'],
  extra_compile_args=['-std=c++11','-O3','-s','-DNDEBUG','-flto','-fopenmp','-m64','-Wall','-Wextra','-Wno-unknown-pragmas','-Wno-sign-compare','-fpic'],
  extra_link_args=['-shared','-lstdc++','-lm','-lgmp','-lgmpxx','-lgomp'])

setup(
  name='lnumber',
  version='0.1',
  packages=['lnumber'],
  #cmdclass={'install': CustomInstall},
  cmdclass={'build_ext': BuildExt},
  include_package_data=True,
  ext_modules=[module],
  author = 'Jose Capco, Christoph Koutchan',
  url='http://www.koutschan.de/data/laman/',
  data_files = [("", ["license.txt"])]
)
