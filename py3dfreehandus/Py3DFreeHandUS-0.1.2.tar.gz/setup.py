# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import check_call, Popen
import tempfile
import os
import shutil



def _post_install(packagedir, setupdir):
    print("copying doc files ...")
    if os.path.isdir(os.path.join(packagedir, 'doc')):
        shutil.rmtree(os.path.join(packagedir, 'doc'))
    shutil.copytree(
        os.path.join(packagedir, 'sphinx/_build/html'),
        os.path.join(packagedir, 'doc'),
    )
    if os.path.isdir(os.path.join(packagedir, 'sphinx')):
        shutil.rmtree(os.path.join(packagedir, 'sphinx'))
    print("compiling Cython code ...")
    p = Popen("python cython_setup.py build_ext --inplace --compiler=mingw32".split(), cwd=packagedir)
    stdout, stderr = p.communicate()
    if stdout is not None:
        print(stdout)
    if stderr is not None:
        print(stderr)
    if os.path.isdir(os.path.join(packagedir, 'build')):
        shutil.rmtree(os.path.join(packagedir, 'build'))


class _install(install):
    """Installation for installation mode."""
    def run(self):
        print("installing wget ...")
        check_call("pip install wget".split())
        print('installing Microsoft Visual C++ for Python 2.7 ...')
        tempdir = tempfile.gettempdir()
        if not os.path.isfile(os.path.join(tempdir, 'VCForPython27.msi')):
            check_call(("python -m wget -o %s/VCForPython27.msi https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi" % (tempdir,)).split())
        try:
            check_call(("msiexec.exe /i %s\\VCForPython27.msi /QN" % (tempdir,)).split())
        except:
            print("already installed")
        print('installing btk ...')
        check_call("easy_install btk".split())
        setupdir = os.path.dirname(os.path.realpath(__file__))
        installVTK = False
        if installVTK:
            print('installing vtk ...')
            if not os.path.isfile(os.path.join(tempdir, 'VTK-6.3.0-cp27-cp27m-win_amd64.whl')):
                check_call(("python -m wget -o %s/VTK-6.3.0-cp27-cp27m-win_amd64.whl https://media.githubusercontent.com/media/u0078867/Py3DFreeHandUS/master/libs/VTK-6.3.0-cp27-cp27m-win_amd64.whl" % (tempdir,)).split())
            check_call(("pip install %s/VTK-6.3.0-cp27-cp27m-win_amd64.whl" % (tempdir,)).split())
        install.run(self)
#        self.do_egg_install() # needed to install dependencies
        packagedir = "%s/Py3DFreeHandUS" % (self.install_lib,)
        self.execute(_post_install, (packagedir, setupdir)) # needed to copy package files

setup(
    name='Py3DFreeHandUS',
    version='0.1.2',
    description='Library for 3D free-hand ultrasonography',
    long_description=open('README.md').read(),
    packages=find_packages('src'),
    package_dir={'':'src'},
    package_data={
        '': ['src/Py3DFreeHandUS/*.pyx', 'src/Py3DFreeHandUS/*.pyd'],
    },
    install_requires=[
        'numpy==1.14.2',
        'scipy==1.1.0',
        'sympy==0.7.6',
        'cython==0.21',
        'matplotlib==2.1.1',
        'SimpleITK==0.9.1',
        'opencv-python==3.4.3.18',
        'moviepy==0.2.2.11',
        'pydicom==0.9.9',
        'guidata==1.7.6',
        'scikit-image==0.14.1'
    ],
    cmdclass={
        'install': _install,
    },
    include_package_data=True,
    license='MIT',
    author='u0078867',
    author_email='davide.monari@kuleuven.be',
    url='https://github.com/u0078867/Py3DFreeHandUS',
)
