# we use this setup.py to build wheels of info-clustering package
# this kind of installation is more flexible and maintainable than `cmake install`
# you can only choose one of the two installation methods.
# before running this file, make sure psp dynamic lib exists in build directory
import os,sys
import pathlib
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig
from shutil import copy

with open('README.md') as fh:
    long_description = fh.read()
    
class CMakeExtension(Extension):

    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])
        
class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = pathlib.Path().absolute()

        # these dirs will be created in build_py, so if you don't have
        # any python sources to bundle, the dirs will be missing
        build_temp = pathlib.Path('build')
        build_temp.mkdir(parents=True, exist_ok=True)

        # example of cmake args
        config = 'Debug' if self.debug else 'Release'
        cmake_args = []
        if not(os.path.exists('CMakeCache.txt')):
            if sys.platform == 'win32':
                VCPKG_ROOT = os.environ.get('VCPKG_ROOT',None)
                if(VCPKG_ROOT == None):
                    raise NameError("VCPKG_ROOT environment variable not set")
                VCPKG_DEFAULT_TRIPLET = os.environ.get('VCPKG_DEFAULT_TRIPLET', 'x64-windows')
                cmake_args += [
                    '-DCMAKE_TOOLCHAIN_FILE=' + os.path.join(VCPKG_ROOT, 'scripts', 'buildsystems', 'vcpkg.cmake'),
                    '-DVCPKG_TARGET_TRIPLET=' + VCPKG_DEFAULT_TRIPLET
                ]
            else:
                cmake_args += [
                    '-DCMAKE_BUILD_TYPE=' + config
                ]
        # example of build args
        build_args = [
            '--config', config
        ]

        os.chdir(str(build_temp))
        if(os.environ.get('CMAKE')):
            cmake_exe = os.environ['CMAKE']
        else:
            cmake_exe = 'cmake'
        self.spawn([cmake_exe, str(cwd)] + cmake_args)
        if not self.dry_run:
            self.spawn([cmake_exe, '--build', '.'] + build_args)
        os.chdir(str(cwd))            
        # after building, rename and copy the file to the lib directory 
        if sys.platform == 'win32':
            psp_path = os.path.join(str(build_temp), config, 'psp.dll')
            copy(psp_path, self.get_ext_fullpath(ext.name))            
        else:
            if(sys.platform == 'darwin'):
                psp_name = 'libpsp.dylib'
            else:
                psp_name = 'libpsp.so'
            copy(os.path.join(str(build_temp), psp_name), self.get_ext_fullpath(ext.name))

        
setup(
    name='info_cluster',
    version='0.4', # python binding version, not the C++ lib version
    packages=['info_cluster'],
    ext_modules=[CMakeExtension('info_cluster/psp')],
    install_requires=['numpy'],
    author="zhaofeng-shu33",
    author_email="616545598@qq.com",
    description="a hierachical clustering algorithm based on information theory",
    url="https://github.com/zhaofeng-shu33/principal_sequence_of_partition",
    long_description = long_description,
    long_description_content_type="text/markdown",        
    classifiers=[
        "Programming Language :: Python :: 3",
    ], 
    license="Apache License Version 2.0",
    cmdclass={'build_ext': build_ext,}    
)
