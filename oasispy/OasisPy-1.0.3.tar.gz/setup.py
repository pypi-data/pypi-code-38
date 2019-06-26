#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools.command.install import install
import os
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        setup_check = input("\n-> Setup OASIS environment now? (recommended) [y]/n: ")
        if setup_check == '':
            setup_check = 'y'
        if setup_check == 'y':
            loc = input("\n-> Location to build OASIS file tree? (default=cwd) ")
            if loc == '':
                loc = os.getcwd()
            if os.path.exists(loc) == True:
                if os.path.exists(loc + "/OASIS") == False:
                    os.system("mkdir %s/OASIS" % (loc))
                    os.system("mkdir %s/OASIS/targets" % (loc))
                    os.system("mkdir %s/OASIS/temp" % (loc))
                    os.system("mkdir %s/OASIS/archive" % (loc))
                    os.system("mkdir %s/OASIS/config" % (loc))
                    os.system("mkdir %s/OASIS/simulations" % (loc))
                    os.system("mkdir %s/OASIS/archive/data" % (loc))
                    os.system("mkdir %s/OASIS/archive/templates" % (loc))
                    os.system("mkdir %s/OASIS/archive/residuals" % (loc))
                    print("-> OASIS file system created in %s\n" % (loc))
                else:
                    print("-> OASIS architecure already exists on this computer")
                ais_run = os.path.dirname(os.path.realpath(__file__)) + '/OasisPy/AIS/package/./install.csh'
                os.system(ais_run)
                with open(os.path.dirname(os.path.realpath(__file__)) + '/OasisPy/config/OASIS.config', 'a') as conf:
                    conf.write("\nloc \t %s \t # location of OASIS file tree. DO NOT CHANGE." % loc)
                os.system("cp %s/OasisPy/config/OASIS.config %s/OASIS/config" % (os.path.dirname(os.path.realpath(__file__)), loc))
            else:
                print("-> Error: Location does not exist\n-> Exiting...\n")
                sys.exit()
        install.run(self)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='OasisPy',
      version='1.0.3',
      description='Difference Imaging Engine for Optical SETI Applications',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Andrew Stewart',
      url='https://github.com/ahstewart/OASIS',
      author_email='ah.stewart@outlook.com',
      packages=['OasisPy'],
      package_dir={'OasisPy': 'OasisPy'},
      package_data={'OasisPy': ['AIS/package/*', 'AIS/package/abs/*', 'AIS/package/bin/*', 'AIS/package/Bphot/*', 'AIS/package/Cphot/*', 'AIS/package/cross/*', 'AIS/package/czerny/*', 'AIS/package/detect/*', 'AIS/package/extract/*', 'AIS/package/fit2d/*', 'AIS/package/images/*', 'AIS/package/interp/*', 'AIS/package/images2/*', 'AIS/package/phot_ref/*', 'AIS/package/register/*', 'AIS/package/stack/*', 'AIS/package/subtract/*', 'AIS/package/utils/*', 'config/*', 'test_config/*']},
      include_package_data = True,
      entry_points = {
          'console_scripts': ['oasis-initialize=OasisPy.initialize:INITIALIZE',
                              'oasis-get=OasisPy.get:GET',
                              'oasis-mask=OasisPy.mask:MASK',
                              'oasis-align=OasisPy.align:ALIGN',
                              'oasis-psf=OasisPy.psf:PSF',
                              'oasis-combine=OasisPy.combine:COMBINE',
                              'oasis-subtract=OasisPy.subtract:SUBTRACT',
                              'oasis-mr=OasisPy.MR:MR',
                              'oasis-extract=OasisPy.extract:EXTRACT',
                              'oasis-pipeline=OasisPy.pipeline:PIPELINE',
                              'oasis-simulate=OasisPy.simulation:SIM',
                              'oasis-test=OasisPy.test:TEST',
                              'oasis-run=OasisPy.run:RUN']},
      cmdclass={'install': PostInstallCommand},
      install_requires=[
          'astropy',
          'numpy',
          'datetime',
          'tabulate',
          'scipy',
          'requests',
          'MontagePy',
          'tqdm',
          'astroscrappy',
          'astroalign',
          'image_registration',
          'photutils']
      )