from setuptools import setup, find_packages
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='ttlab',
      version='0.44.90',
      description='Physics lab equipment analysis software',
      #long_description_content_type='text/markdown',
      long_description=open("README.rst").read(),
      url='',
      author='Christopher Tiburski and Johan Tenghamn',
      author_email='info@ttlab.se',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      keywords='XPS Cary5000 MassSpec Mass spectrometer Light spectrometer Insplorion Physics Analysis Pfeiffer Multipak Plasmonics Activation energy X0Reactor Plasmons',
      classifiers=['Development Status :: 4 - Beta','Programming Language :: Python :: 3.6','Intended Audience :: Science/Research','Topic :: Scientific/Engineering :: Physics'],
      zip_safe=False)
# "![](https://bytebucket.org/tt-lab/ttlab/raw/07af7e037611c6d2b47aef425bc7e078519c04ce/assets/header.png?token=9425964a76732a6a54d81fb58935ae6dc8acbfa4)\n#!/usr/bin/python\n\n# TT - lab\n___\nEasy to use import scripts for the most common physics equipments such as XPS, mass spectrometer, light spectrometers.\nFunctions for the most typical analysis procedures. \n\n## Installation\n```\npip install ttlab\n```\n\n## How to use\nFor full explanation, see the documentation at 'link'.\n\nExample with mass spectrometer data:\n```\n\nfrom ttlab import MassSpectrometer\n\n# Create a mass spec object\nfilename = \'path/filename.asc\'\nMS = MassSpectrometer(filename)\n\n# Check what gases are included in the data\nprint(MS.get_gases())\n# Plot one of the gases, using matploltlib, returns the axes\nax = MS.plot_gas(\'Ar\')\n\n# Get the ion current and the relative time for the gas, returns np arrays with the data\nion_current_argon = MS.get_ion_current(\'Ar\')\ntime_relative = MS.get_relative_time(\'Ar\')\n```\n## Want to contibute?\n\nWith money? Plz give it it to charity instead.\n\nWith code?\n\nContact us by mail: \n\nChalmers tekniska h�gskola AB \n\n Chemical Physics\n\n TTLAB \n\n412 96 G�teborg\n\n## License \nMIT license \n Feel free to use ttlab in whatever way you want to."