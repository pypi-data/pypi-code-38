
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages 
import glob, os.path, sys

# Read long description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Path check
def which(command):
    percorso = os.getenv("PATH")
    directories = percorso.split(os.pathsep)
    for path_dir in directories:
        real_dir = os.path.expanduser(path_dir)
        try:
            lista_dir = os.listdir(real_dir)
        except OSError:
            lista_dir = []
        if os.path.exists(real_dir) and command in lista_dir:
            return os.path.join(real_dir, command)
    return None


# Look for script files
lscr = glob.glob(os.path.join('Scripts', 'SRP*'))
lscrex = []
for i in lscr:
    if os.path.splitext(i)[1] == '':
        lscrex.append(i)


# Look for data files
lsdt = glob.glob(os.path.join('SRP/SRPData', '*'))
lsdtex = []
for i in lsdt:
    if os.path.splitext(i)[1] == '':
        lsdtex.append(i)


# python
print("Python version %s" % (sys.version))
pvl = sys.version.split()[0].split('.')
if int(pvl[0]) != 3 :
    print("Python version should be 3.x.")


import SRP

setup(
    name='SRPAstro', 
    version=SRP.__version__, 
    description='Data Analysis Packages', 
    packages = find_packages('.'),
    include_package_data = True,
    long_description='Set of tools for carrying out simple tasks related to astronomers daily life',
    author='Stefano Covino', 
    author_email='stefano.covino@brera.inaf.it', 
    url='https://pypi.python.org/pypi/SRPAstro',
    install_requires=['mysql-connector-python', 'py-postgresql', 'requests', 'astroquery', 'astropy>=0.4',
        'scipy', 'astlib>=0.4', 'matplotlib', 'atpy', 'asciitable', 'ephem', 'numpy>=1.1'],
    scripts=lscrex,
    zip_safe = False,
    package_data={'SRP':lsdtex},
    classifiers=[ 
        'Development Status :: 5 - Production/Stable', 
        'Environment :: Console', 
        'Intended Audience :: Science/Research', 
        'License :: Freely Distributable', 
        'Operating System :: MacOS :: MacOS X', 
        'Operating System :: POSIX', 
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Astronomy', 
        ], 
    ) 


# nose
